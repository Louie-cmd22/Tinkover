# Tinkover

Tinkover is a simple blogging website where users can create an account, express their thoughts, share ideas, and write about topics that interest them.

The project was built as a hands-on way to learn backend web development with FastAPI, including authentication, database management, security, migrations, version control, and deployment.

## Live Demo

https://tinkover.onrender.com/

> The application is hosted on Render's free tier, so it may take a short time to start after a period of inactivity.

## Features

- User registration and login
- Session-based authentication
- CSRF protection
- Create, read, edit, and delete blog posts
- User account management
- Authorization for editing and deleting posts
- Cascade deletion of a user's blog posts when their account is deleted
- Server-side form validation

## Tech Stack

- **Python**
- **FastAPI** - backend web framework
- **Jinja2** - server-side HTML templating
- **SQLAlchemy** - ORM and database access
- **Alembic** - database schema migrations
- **PostgreSQL** - production database
- **SQLite** - local development database
- **Psycopg** - PostgreSQL database driver
- **Uvicorn** - ASGI server
- **Render** - application hosting
- **Aiven** - managed PostgreSQL hosting

## Project Structure

Tinkover uses FastAPI for routing and backend logic, SQLAlchemy for interacting with the database, and Jinja2 for rendering the frontend. Database schema changes are managed through Alembic.

The application supports both SQLite and PostgreSQL through environment-based database configuration. SQLite was used during initial development, while PostgreSQL is used for the deployed application.

## Deployment

The application is deployed on Render and connects to a managed PostgreSQL database hosted on Aiven.

Production configuration and credentials are supplied through environment variables and are not stored in the repository.

## Version
**v1.0.0** - First Release

**v1.1.0** - PostgreSQL support and production deployment