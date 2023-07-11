from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .security import get_password_hash
from . import schemas

DEFAULT_LIMIT = 5


async def get_user(db: AsyncSession, id: int):
    # use `joinedload` mode eager load to fetch belonging todos
    # other modes are like: `selectinload`, which runs `select * where user_id in (..)`
    # this is a query design tradeoff of one join query vs two separate select queries
    query = select(User).where(User.id == id).options(joinedload(User.todos))
    # query = select(User).where(User.id == id).options(selectinload(User.todos))
    users = await db.execute(query)
    user = users.first()
    if user:
        (user,) = user
        return user
    return None


async def get_users(
    db: AsyncSession, filters: dict = {}, offset: int = 0, limit: int = DEFAULT_LIMIT
):
    query = select(User).limit(limit).offset(offset)

    if filters.get("email"):
        query = query.where(User.email == filters["email"])

    users = await db.execute(query)
    # By sqlalchemy doc: use `.scalars()` method to skip the generation of
    # `Row` objects and instead receive ORM entities directly.
    # See: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-orm-entities-and-attributes
    users = users.scalars().all()
    return users


async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> User:
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        fname=user_data.fname,
        lname=user_data.lname,
        # is_superuser=user_data.is_superuser,
    )
    db.add(user)
    try:
        await db.commit()
        # await db.refresh(user)
    except:
        db.rollback()
        raise
    return user