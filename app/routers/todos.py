from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from .. import schemas
from .. import crud_todo

router = APIRouter(prefix="/api/todos", dependencies=[])


# @router.get("/")
# @router.get("/", response_model=list[schemas.TodoReadNested])
@router.get("/", response_model=list[schemas.TodoRead])
async def read_todos(
    user_id: int = None,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    if user_id:
        todos = await crud_todo.get_user_todos(db, user_id, offset=offset, limit=limit)
    else:
        todos = await crud_todo.get_todos(db, offset=offset, limit=limit)
    return todos


# @router.get("/{id}", response_model=schemas.TodoRead)
@router.get("/{id}", response_model=schemas.TodoReadNested)
async def read_todo(id: int):
    todo = await crud_todo.get_todo(id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return todo


@router.post("/", response_model=schemas.TodoRead)
async def create_todo(
    todo_data: schemas.TodoCreate, db: AsyncSession = Depends(get_db)
):
    todo = await crud_todo.create_todo(db, todo_data)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request"
        )
    return todo
