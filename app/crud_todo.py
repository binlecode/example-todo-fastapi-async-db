from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy import delete as sa_delete
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
        # this db.refresh is not needed actually
        # because there's no further usage of this instance in this session
        await db.refresh(todo)
    except:
        await db.rollback()
        raise
    return todo


async def update_todo(db: AsyncSession, id: str, todo_data: schemas.TodoUpdate):
    query = select(Todo).where(Todo.id == id)
    todos = await db.execute(query)
    # AsyncResult.first() returns none if no row, or 1 element tuple
    if not todos:
        return None
    (todo,) = todos.first()
    todo.text = todo_data.text
    todo.completed = todo_data.completed
    todo.owner_id = todo_data.owner_id
    db.add(todo)
    try:
        await db.commit()
        await db.refresh(todo)
    except:
        await db.rollback()
        raise
    return todo


async def delete_todo(db: Session, id: str):
    query = sa_delete(Todo).where(Todo.id == id)
    await db.execute(query)
    try:
        await db.commit()
    except:
        await db.rollback()
        raise
    return True


async def get_todo(id: str):
    # use a separate `select .. in` query to eager load owner data
    query = select(Todo).where(Todo.id == id).options(selectinload(Todo.owner))
    # ! Note: this is an alternative way of requesting a db session to the
    #   FastAPI dependency injected db session.
    # See the get_todos(db: AsyncSession, ...) below for comparison.
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
    db: AsyncSession, user_id: str, offset: int = 0, limit: int = DEFAULT_LIMIT
):
    query = select(Todo).where(Todo.owner_id == user_id).limit(limit).offset(offset)
    todos = await db.execute(query)
    todos = todos.scalars().all()
    return todos
