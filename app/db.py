import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import sessionmaker


# SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sqlite.db"
# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@postgresserver/db"

# set check_same_thread to false specifically for sqlite3 file database
# This is to allow multiple threads to access same connection in FastAPI
# Ref: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#pysqlite-threading-pooling
# check_same_thread custom setting is not needed for other databases
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

# create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    # enable sql statements logging for debug/development
    echo=True,
)


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# To create async session, we should disable "expire_on_commit".
# This is because we don't want sqlalchemy to issue new sql queries
# to the database when accessing already committed objects.
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# create FastAPI dependency async function to get an async db session
# use with-as context manager for session cleanup
async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db
