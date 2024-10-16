## local run

```sh
pyenv shell 3.11
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
# install all dependencies
pip install -r requirements.txt
# to upgrade all packages to latest version
pip install --upgrade $(pip freeze | cut -d '=' -f 1)

# reset local sqlite db during app start up
RESET_DB=true uvicorn app.main:app --reload
# or without db reset
uvicorn app.main:app --reload
```

## openapi doc endpoint

Openapi doc is auto-generated at `http://127.0.0.1:8000/docs`.

## async db with sqlalchemy

About async SqlAlchemy implementation:

-   async db, connection string for sqlite uses `aiosqlite`:
    `SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sqlite.db"`
-   create_async_engine() and async SessionLocal factory method
    see [`app/db.py`](./app/db.py).
-   async session context manager with `yield` for FastApi web stack dependency
-   async CRUD with async session
-   db session independent SqlAlchemy entity models
-   db session independent Pydentic schemas

There are two common ways of using async session:

1. implicit context manager with `yield` for resource cleanup:

```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db
```

This session getter can be used in fastapi dependency injection during router
function definition.

````python

1) explicit with .. as context manager

```python
async with SessionLocal() as db:
    todos = await db.execute(query)
...
````

Both are useful for their suitable use cases.
Option 1 is good for dependency injection such as FastAPI routers.
Option 2 has explicit session scope boundary isolation

## ORM relationship in async queries

Lazy load is tricky in async session queries, usually in need of session
manual commit followed by refresh and sometimes global
session `expire_on_commit`
change.
Eager load is safer as it bundles all db operations in current session
transaction.

Two eager load modes used:

-   use `joinedload`, which use a join query to load associated entities
-   use `selectinload`, which runs a second `select * where key in (..)` query

The query design tradeoff is one join query vs two separate select queries.
Join load is preferred for one-to-many relations.
Select-in load is preferred for many-to-one relations.

## dynamic filtering with ORM query

With Sqlalchemy 2.0 new query syntax, a dynamic query builder is implemented
as ORM model mixin to support dynamic filtering.

Dynamic filters are implemented as SqlAlchemy ColumnElement expressions
concatenated in Query builder DSL.

See: https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement

## model validation with pydantic

To convert Sqlalchemy orm model data into pydantic validation schema,
the schema (pydantic model) has to load custom config with `orm_mode = True`.

## environment bootstrap

```sh
pyenv shell 3.10
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
# use sqlalchemy for data models
pip install sqlalchemy
# install async support for sqlalchemy, it includes greenlet
pip install "sqlalchemy[asyncio]"
pip install aiosqlite
pip install fastapi
pip install pydantic "pydantic[email]"
pip install uvicorn
# install passlib for password hashing
# choose bcrypt as password hashing algorithm
# ref: https://en.wikipedia.org/wiki/Bcrypt
pip install "passlib[bcrypt]"
# freeze the dependency list
pip freeze > requirements.txt
```

Async db driver libs are needed for specific databases, for example:
`pip install asyncpg` for postgreSql.
