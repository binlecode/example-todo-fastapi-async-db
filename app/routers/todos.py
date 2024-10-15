from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db_session
from .. import schemas
from .. import crud_todo

router = APIRouter(prefix="/api/todos", dependencies=[])


# @router.get("/")
# @router.get("/", response_model=list[schemas.TodoReadNested])
@router.get("/", response_model=list[schemas.TodoRead])
async def read_todos(
    user_id: str = None,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
):
    if user_id:
        todos = await crud_todo.get_user_todos(db, user_id, offset=offset, limit=limit)
    else:
        todos = await crud_todo.get_todos(db, offset=offset, limit=limit)
    return todos


# @router.get("/{id}", response_model=schemas.TodoRead)
@router.get("/{id}", response_model=schemas.TodoReadNested)
async def read_todo(id: str):
    todo = await crud_todo.get_todo(id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return todo


@router.post("/", response_model=schemas.TodoRead)
async def create_todo(
    todo_data: schemas.TodoCreate, db: AsyncSession = Depends(get_db_session)
):
    todo = await crud_todo.create_todo(db, todo_data)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request"
        )
    return todo


@router.put("/{id}", response_model=schemas.TodoRead)
async def update_todo(
    id: str, todo_data: schemas.TodoUpdate, db: AsyncSession = Depends(get_db_session)
):
    todo = await crud_todo.update_todo(db, id, todo_data)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request"
        )
    return todo


@router.delete("/{id}")
async def delete_todo(id: str, db: AsyncSession = Depends(get_db_session)):
    r = await crud_todo.delete_todo(db, id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request"
        )
    return {"message": "resource deleted"}, 200
