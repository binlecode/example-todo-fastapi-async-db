import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from .models_timestamp import AutoTimestampMixin
from .models_crud import CrudMixin
from .models_filter import FilterMixin

Base = declarative_base()


# NOTE: to work with sqlite3, as sqlite3 doesn't have a built-in UUID type, we
# use a string type for the uuid column.


class User(Base, AutoTimestampMixin, CrudMixin, FilterMixin):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    lname = Column(String)
    fname = Column(String)
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")


class Todo(Base, AutoTimestampMixin):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    text = Column(String, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")
