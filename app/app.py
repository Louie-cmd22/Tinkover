from fastapi import FastAPI, Depends, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .db import  get_db
from .model import Blog, User
from .utils import get_current_user, hash_password, verify_password, get_optional_user, get_csrf_token, validate_csrf_token
import os
import dotenv



dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set.")

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
IS_PRODUCTION = ENVIRONMENT == "production"

# create FastAPI app
app = FastAPI()

# Add session middleware for handling user sessions
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age = 60 * 60 * 24 * 7,  # 1 week in seconds
    same_site="lax",
    https_only=IS_PRODUCTION
)

# Jinja templates
templates = Jinja2Templates(directory="app/templates")

# Serve static files
app.mount(
    "/static", 
    StaticFiles(directory="app/static"), 
    name="static"
)


### Website routes ###

## Home page
@app.get("/")
def homepage(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):
    blogs = db.query(Blog).all()

    return templates.TemplateResponse(  
        request=request,
        name="home.html", 
        context={"blogs": blogs, "user": user}
    )

## Create blog page
@app.get("/blog/create")
def create_blog_page(request: Request, user: User = Depends(get_current_user)):

    # Reuse the session's CSRF token or generate one if missing
    csrf_token = get_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="create_blog.html",
        context={"user": user, "csrf_token": csrf_token}
    )

# Create blog form
@app.post("/blog/create")
def create_blog(request: Request, title: str = Form(...), content: str = Form(...), csrf_token: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    validate_csrf_token(request, csrf_token)

    # Form validation
    title = title.strip()
    content = content.strip()

    if not title:
        return templates.TemplateResponse(
            request=request,
            name="create_blog.html",
            context={
                "error": "Title cannot be empty", 
                "user": user,
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not content:
        return templates.TemplateResponse(
            request=request,
            name="create_blog.html",
            context={
                "error": "Content cannot be empty", 
                "user": user,
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(title) > 60:
        return templates.TemplateResponse(
            request=request,
            name="create_blog.html",
            context={
                "error": "Title cannot exceed 60 characters", 
                "user": user,
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(content) < 1500:
        return templates.TemplateResponse(
            request=request,
            name="create_blog.html",
            context={
                "error": "Content must be at least 1500 characters long", 
                "user": user,
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    new_blog = Blog(
        title=title,
        content=content,
        user_id=user.id
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return RedirectResponse(url=f"/blog/{new_blog.id}", status_code=status.HTTP_303_SEE_OTHER)

## Blog page
@app.get("/blog/{blog_id}")
def blog_page(blog_id: int, request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return templates.TemplateResponse(
            request=request,
            name="blog_detail.html",
            context={"error": "Blog not found", "user": user},
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Reuse the session's CSRF token or generate one if missing
    csrf_token = get_csrf_token(request)

    return templates.TemplateResponse(  
        request=request,
        name="blog_detail.html", 
        context={"blog": blog, "user": user, "csrf_token": csrf_token}
    )

## Edit blog page
@app.get("/blog/{blog_id}/edit")
def edit_blog_page(blog_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):


    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={"error": "Blog not found", "user": user},
            status_code=status.HTTP_404_NOT_FOUND
        )

    if blog.user_id != user.id:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={"error": "You are not authorized to edit this blog", "user": user},
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Reuse the session's CSRF token or generate one if missing
    csrf_token = get_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="edit_blog.html",
        context={"blog": blog, "user": user, "csrf_token": csrf_token}
    )

# Edit blog form
@app.post("/blog/{blog_id}/edit")
def edit_blog(blog_id: int, request: Request, title: str = Form(...), content: str = Form(...), csrf_token: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):


    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={"error": "Blog not found", "user": user},
            status_code=status.HTTP_404_NOT_FOUND
        )

    if blog.user_id != user.id:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={"error": "You are not authorized to edit this blog", "user": user},
            status_code=status.HTTP_403_FORBIDDEN
        )

    validate_csrf_token(request, csrf_token)
    
    # Form validation
    title = title.strip()
    content = content.strip()

    if not title:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={
                "error": "Title cannot be empty", 
                "user": user,
                "csrf_token": csrf_token,
                "blog": blog
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not content:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={
                "error": "Content cannot be empty", 
                "user": user,
                "csrf_token": csrf_token,
                "blog": blog
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(title) > 60:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={
                "error": "Title cannot exceed 60 characters", 
                "user": user,
                "csrf_token": csrf_token,
                "blog": blog
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(content) < 1500:
        return templates.TemplateResponse(
            request=request,
            name="edit_blog.html",
            context={
                "error": "Content must be at least 1500 characters long", 
                "user": user,
                "csrf_token": csrf_token,
                "blog": blog
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )


    blog.title = title
    blog.content = content
    db.commit()
    db.refresh(blog)

    return RedirectResponse(url=f"/blog/{blog.id}", status_code=status.HTTP_303_SEE_OTHER)

## Delete blog
@app.post("/blog/{blog_id}/delete")
def delete_blog(blog_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user), csrf_token: str = Form(...)):


    validate_csrf_token(request, csrf_token)

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return templates.TemplateResponse(
            request=request,
            name="blog_detail.html",
            context={"error": "Blog not found", "user": user},
            status_code=status.HTTP_404_NOT_FOUND
        )

    if blog.user_id != user.id:
        return templates.TemplateResponse(
            request=request,
            name="blog_detail.html",
            context={
                "blog": blog,
                "user": user,
                "error": "You are not authorized to delete this blog"
            },
            status_code=status.HTTP_403_FORBIDDEN
        )

    db.delete(blog)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

## Account page
@app.get("/account")
def account_page(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    # Reuse the session's CSRF token or generate one if missing
    csrf_token = get_csrf_token(request)


    user_blogs = db.query(Blog).filter(Blog.user_id == user.id).all()
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"user": user, "user_blogs": user_blogs, "csrf_token": csrf_token}
    )

# Delete account
@app.post("/account/delete")
def delete_account(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user), csrf_token: str = Form(...)):

    
    validate_csrf_token(request, csrf_token)

    db.delete(user)
    db.commit()

    request.session.clear()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

## Login page
@app.get("/login")
def login_page(request: Request):

    message = request.session.pop("message", None)

    # Reuse the session's CSRF token or generate one if missing
    csrf_token = get_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": message, "csrf_token": csrf_token}
    )

# Login form
@app.post("/login")
def login_user(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...), db: Session = Depends(get_db)):

    print("BEFORE CSRF")
    validate_csrf_token(request, csrf_token)
    print("AFTER CSRF")
    existing_user = db.query(User).filter(User.username == username).first()
    if not existing_user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid username or password" ,
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not verify_password(password, existing_user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid username or password",
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    request.session["user_id"] = existing_user.id

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

## Logout
@app.post("/logout")
def logout_user(request: Request, csrf_token: str = Form(...)):

    
    validate_csrf_token(request, csrf_token)

    
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

## Register page
@app.get("/register")
def register_page(request: Request):
  
    # Reuse the session's CSRF token or generate one if missing
    csrf_token = get_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"csrf_token": csrf_token}
    )

# Registration form
@app.post("/register")
def register_user(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...), db: Session = Depends(get_db)):

    print("BEFORE CSRF")
    validate_csrf_token(request, csrf_token)
    print("AFTER CSRF")
    # Form validation
    username = username.strip()
    if not username:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Username cannot be empty", 
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(username) > 20:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Username cannot exceed 20 characters",
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Password must be at least 6 characters long",
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )


    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Username already exists",
                "csrf_token": csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    hashed_password = hash_password(password)

    new_user = User(
        username=username,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    request.session["message"] = "Registration successful! Please log in."

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


