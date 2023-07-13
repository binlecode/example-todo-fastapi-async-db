from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from .models_timestamp import AutoTimestampMixin
from .models_crud import CrudMixin
from .models_filter import FilterMixin

Base = declarative_base()


class User(Base, AutoTimestampMixin, CrudMixin, FilterMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    lname = Column(String)
    fname = Column(String)
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")


class Todo(Base, AutoTimestampMixin):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")
