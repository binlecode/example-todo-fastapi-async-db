from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db_session
from .. import schemas
from .. import crud_user

router = APIRouter(prefix="/api/users", dependencies=[])


# @router.get("/", response_model=list[schemas.UserReadNested])
@router.get("/", response_model=list[schemas.UserRead])
async def read_users(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
):
    return await crud_user.get_users(db, offset=offset, limit=limit)


@router.get("/crudmixin/", response_model=list[schemas.UserRead])
async def read_users_with_crudmixin(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
):
    return await crud_user.get_users_with_crudmixin(db, offset=offset, limit=limit)


@router.get("/{id}", response_model=schemas.UserReadNested)
async def read_user(id: int, db: AsyncSession = Depends(get_db_session)):
    user = await crud_user.get_user(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return user


@router.get("/crudmixin/{id}", response_model=schemas.UserRead)
async def read_user_with_crudmixin(id: int, db: AsyncSession = Depends(get_db_session)):
    user = await crud_user.get_user_with_crudmixin(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return user


@router.get("/filter/", response_model=list[schemas.UserRead])
async def filter_users(
    email: str | None = None,
    lname: str | None = None,
    fname: str | None = None,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
):
    filter_conditions = []
    if email:
        filter_conditions.append(("email", "ilike", email))
    if lname:
        filter_conditions.append(("lname", "ilike", lname))
    if fname:
        filter_conditions.append(("fname", "ilike", fname))
    return await crud_user.filter_users(
        db, filter_conditions, offset=offset, limit=limit
    )


@router.post("/signup/", response_model=schemas.UserRead)
async def signup(
    user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db_session)
):
    # check existing user with same email
    users = await crud_user.get_users(db, {"email": user_data.email})
    if users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )
    signed_up_user = await crud_user.create_user(db, user_data)
    return signed_up_user
