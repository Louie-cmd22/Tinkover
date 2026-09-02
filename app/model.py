from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from .db import Base
from datetime import datetime


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    date_posted = Column(DateTime, default=datetime.now, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    date_created = Column(DateTime, default=datetime.now, nullable=False)