from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from .models import Todo
from .db import SessionLocal
from .crud_user import get_user, get_users

DEFAULT_LIMIT = 5


async def create_todo(db: AsyncSession, todo_data: schemas.TodoCreate):
    # get user by owner_id
    owner = await get_user(db, todo_data.owner_id)
    if not owner:
        return None

    todo = Todo(
        text=todo_data.text,
        completed=todo_data.completed,
        owner=owner,
    )
    db.add(todo)
    try:
        await db.commit()
        # this db.refresh on todo instance is not needed actually
        # because there's no further usage of it in this session
        await db.refresh(todo)
    except:
        await db.rollback()
        raise
    return todo


# TODO: convert to async
def update_todo(db: Session, todo_data: schemas.TodoUpdate):
    todo = db.query(Todo).filter(Todo.id == id).first()
    todo.text = todo_data.text
    todo.completed = todo_data.completed
    db.commit()
    db.refresh(todo)
    return todo


# TODO: convert to async
def delete_todo(db: Session, id: int):
    todo = db.query(Todo).filter(Todo.id == id).first()
    db.delete(todo)
    db.commit()


async def get_todo(id: int):
    # use a separate `select .. in` query to eager load owner data
    query = select(Todo).where(Todo.id == id).options(selectinload(Todo.owner))
    # ! Note: this is an alternative implementation to the FastAPI dependency
    #   injected db session.
    #   See the get_todos(db: AsyncSession, ...) below for comparison.
    async with SessionLocal() as db:
        todos = await db.execute(query)
    # AsyncResult.first() returns none if no row, or 1 element tuple
    todo = todos.first()
    if todo is not None:
        (todo,) = todo  # take the element from the tuple
    return todo


async def get_todos(db: AsyncSession, offset: int = 0, limit: int = DEFAULT_LIMIT):
    query = select(Todo).limit(limit).offset(offset)
    # query = select(Todo).limit(limit).offset(offset).options(joinedload(Todo.owner))
    todos = await db.execute(query)
    todos = todos.scalars().all()
    return todos


async def get_user_todos(
    db: AsyncSession, user_id: int, offset: int = 0, limit: int = DEFAULT_LIMIT
):
    query = select(Todo).where(Todo.owner_id == user_id).limit(limit).offset(offset)
    todos = await db.execute(query)
    todos = todos.scalars().all()
    return todos