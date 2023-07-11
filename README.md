## local run

```sh
pyenv shell 3.10
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# reset local sqlite db during app start up
RESET_DB=true uvicorn app.main:app --reload
# or without db reset
uvicorn app.main:app --reload
```

## async db with sqlalchemy

About async SqlAlchemy:

- create_async_engine() the asyncengine
- work with connect() and begin() transaction methods that deliver
  asynchronous context type managers
- async context manager uses AsyncConnection to invoke the statements
  in the server-side async results
- uses asyncio platform with the greenlet lib provided by python runtime

For async db, the connection string for sqlite uses `aiosqlite`:
`SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sqlite.db"`




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

