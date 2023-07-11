from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from .. import schemas
from .. import crud_user

router = APIRouter(prefix="/api/users", dependencies=[])


# @router.get("/", response_model=list[schemas.UserReadNested])
@router.get("/", response_model=list[schemas.UserRead])
async def read_users(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await crud_user.get_users(db, offset=offset, limit=limit)


# @router.get("/{id}", response_model=schemas.UserRead)
@router.get("/{id}", response_model=schemas.UserReadNested)
async def read_user(id: int, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return user


@router.post("/signup", response_model=schemas.UserRead)
async def signup(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # check existing user with same email
    users = await crud_user.get_users(db, {"email": user_data.email})
    if users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )
    signed_up_user = await crud_user.create_user(db, user_data)
    return signed_up_user