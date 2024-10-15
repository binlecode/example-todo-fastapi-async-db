# express the schema of incoming/outgoing data using pydantic models
# and use these models as type hint for auto validation and conversion
# these models (better called 'schemas`) are data shape specs.

from datetime import datetime
from pydantic import BaseModel
from pydantic import EmailStr


## User schemas


class UserBase(BaseModel):
    email: EmailStr
    lname: str
    fname: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserCreate):
    id: str


# UserRead schema excludes hashed_password field
class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


## Todo schemas


class TodoCreate(BaseModel):
    owner_id: str
    text: str
    completed: bool


class TodoUpdate(TodoCreate):
    id: str


class TodoRead(TodoUpdate):
    owner_id: str
    # owner: UserRead
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# nested view model includes child orm objects


# be careful to only use UserRead, not UserReadNested
# otherwise it will lead to endless circular lazy loading...
class TodoReadNested(TodoRead):
    owner: UserRead


class UserReadNested(UserRead):
    todos: list[TodoRead]
