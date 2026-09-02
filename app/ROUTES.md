# Tinkover v1 Route Documentation

## Overview

Tinkover V1 is a server-rendered web application built with FastAPI, Jinja2, SQLAlchemy, and SQLite.

The project initially used JSON API endpoints, but these were replaced with Jinja2 template-rendering routes to simplify the architecture and allow V1 to focus primarily on learning FastAPI, backend development, authentication, and database integration.

The current application uses HTML forms for client-server communication and session-based authentication. Future versions may introduce a JavaScript frontend framework such as React to provide a more interactive user experience while retaining FastAPI as the backend.

## CSRF Protection

All POST form submissions are protected using session-based CSRF tokens.
Tokens are generated securely, stored in the user's session, included as
hidden form fields, and validated before state-changing operations are
performed.



## Access Levels

## Public

Can be accessed without logging in.

## Authenticated

Requires a valid logged in user/session.

## Authorization

Requires authentication ownership of the requested resource. 


# Routes

## Home

### 'GET /'

**Access:** Public

**Purpose:** 
Navigate to the home/main page. 

**Response:**
Website home page loads.

**Possible errors:**
- None expected under normal application operation.


## Login 

### 'GET /login'

**Access:** Public

**Purpose:** 
Navigate to the login page. 

**Response:**
Website login page loads.

**Possible errors:**
- None expected under normal application operation.

### 'POST /login'

**Access:** Public

**Purpose:** 
Login existing user account.

**Input:**
- username - form data 
- password - form data

**Response:**
303 SEE OTHER: User is routed to the homepage ('/') as a logged in user. 

**Possible errors:**
- 401 UNAUTHORIZED: Invalid username or password

### `POST /logout`

**Access:** Public / Session Action

**Purpose:** 
Clears current browser session and logs the user out if a session exists.

The route clears the session whether a user is currently logged in or already logged out.

**Response:**
303 SEE OTHER: User is routed to `GET /`. 

**Possible errors:**
- None expected under normal application operation.

### 'GET /register'
**Access:** Public

**Purpose:** 
Navigate to the register page. 

**Response:**
Website register page loads.

**Possible errors:**
- None expected under normal application operation.

### 'POST /register'

**Access:** Public

**Purpose:** 
Register a new user account.

**Input:**
- username - form data 
- password - form data

**Response:**
- Stores a temporary session/flash message: Registration successful! Please log in.
- 303 SEE OTHER:  Redirects to `GET /login`.

**Possible errors:**
- 400 BAD REQUEST: Username already exists

**Validation Rules:**

*username*
- required
- maximum 20 characters
- Leading and trailing whitespace is removed
- Must contain at least one non-whitespace character

*password*
- required
- minimum 6 characters

### `GET /blog/create`

**Access:** Authenticated

**Purpose:** 
Navigate to create blog page. 

**Authentication:** 
Verified by `get_current_user`


**Response:**
Website create blog page loads.

**Possible errors:**
- 401 UNAUTHORIZED: User is not authenticated.

### `POST /blog/create`

**Access:** Authenticated

**Purpose:** 
Create new blogs.

**Authentication:** 
Verified by `get_current_user`.

**Input:**
- title - form data 
- content - form data

**Response:**
303 SEE OTHER: Redirects to the newly created blog's detail page at `/blog/{blog_id}`.

**Possible errors:**
- 401 UNAUTHORIZED: User is not authenticated.

**Validation Rules:**

*title*
- required
- maximum 60 characters
- Leading and trailing whitespace is removed
- Must contain at least one non-whitespace character

*content*
- required
- Leading and trailing whitespace is removed
- minimum 1500 characters


### `GET /blog/{blog_id}`


**Access:** Public

**Purpose:** 
Navigate to specific blog page.

**Response:**
Website {blog_id} blog page loads.

**Possible errors:**
- 404 NOT FOUND: Blog not found

### `GET /blog/{blog_id}/edit`

**Access:** Owner-only

**Purpose:** 
Navigate to edit blog page.

**Authentication:** 
Verified by `get_current_user`

**Authorization:** 
authenticated user id should match blog user_id

**Response:**
Website edit blog page loads.

**Possible errors:**
- 404 NOT FOUND: Blog not found
- 403 FORBIDDEN: You are not authorized to edit this blog
- 401 UNAUTHORIZED: User is not authenticated.


### `POST /blog/{blog_id}/edit`

**Access:** Owner-only

**Purpose:** 
Update a blog.

**Authentication:** 
Verified by `get_current_user`

**Authorization:** 
The authenticated user's `id` must match the blog's `user_id`.

**Response:**
303 SEE OTHER: Redirects to `/blog/{blog_id}`.

**Input:**
- title - form data 
- content - form data

**Possible errors:**
- 404 NOT FOUND: Blog not found
- 403 FORBIDDEN: You are not authorized to edit this blog
- 401 UNAUTHORIZED: User is not authenticated.

**Validation Rules:**

*title*
- required
- maximum 60 characters
- Leading and trailing whitespace is removed
- Must contain at least one non-whitespace character

*content*
- required
- Leading and trailing whitespace is removed
- minimum 1500 characters

### `POST /blog/{blog_id}/delete`

**Access:** Owner-only

**Purpose:** 
Delete a blog.

**Authentication:** 
Verified by `get_current_user`

**Authorization:** 
The authenticated user's `id` must match the blog's `user_id`.

**Response:**
303 SEE OTHER: Redirects to `/`.

**Possible errors:**
- 404 NOT FOUND: Blog not found
- 403 FORBIDDEN: You are not authorized to delete this blog
- 401 UNAUTHORIZED: User is not authenticated.


### `GET /account`

**Access:** Authenticated

**Purpose:** 
Navigate to current user's account page.

**Authentication:** 
Verified by `get_current_user`

**Response:**
- Account information
- Blogs owned by the authenticated user

**Possible errors:**
- 401 UNAUTHORIZED: User is not authenticated.

### `POST /account/delete`

**Access:** Authenticated

**Purpose:** 
Delete the currently authenticated user's account.

**Authentication:** 
Verified by `get_current_user`

**Response:**
- Deletes the account.
- Associated blogs are deleted through database cascade.
- Clears the session.
- 303 SEE OTHER: Redirects to `/`.

**Possible errors:**
- 401 UNAUTHORIZED: User is not authenticated.
