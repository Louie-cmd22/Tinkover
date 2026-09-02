from fastapi import Request, Depends, HTTPException, status

from sqlalchemy.orm import Session
from .db import get_db
from .model import User

from pwdlib import PasswordHash
import secrets

password_hasher = PasswordHash.recommended()

# password hashing and verification
def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


# User authentication and retrieval
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

# If user not logged in, return None
def get_optional_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    
    return db.query(User).filter(User.id == user_id).first()

# CSRF token utility functions
def get_csrf_token(request: Request):
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)

    return request.session["csrf_token"]


def validate_csrf_token(request: Request, token: str):
    session_token = request.session.get("csrf_token")


    print("Submitted:", token)
    print("Session:", session_token)

    if not session_token or not secrets.compare_digest(session_token, token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )

