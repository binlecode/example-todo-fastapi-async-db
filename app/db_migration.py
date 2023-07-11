from app.db import engine
from app.models import Base
from app.db import SessionLocal
from app.models import User, Todo


# async version of table initialization
# use async_engine.begin() for transaction control
# use run_sync to run a sync sqlalchemy method
async def init_tables():
    async with engine.begin() as conn:
        print(">> sqlalchemy dropping existing tables")
        await conn.run_sync(Base.metadata.drop_all)
        print(">> sqlalchemy creating tables")
        await conn.run_sync(Base.metadata.create_all)


# async version of table data migration
# the SessionLocal() creates an asyncSession context
async def migrate_data():
    async with SessionLocal() as db:
        u1 = User(
            lname="Doe",
            fname="John",
            email="johndoe@example.com",
            # plain pswd: "secret"
            hashed_password="$2b$12$mV7rTpEAAk77POssNFkBfO.F0UvhU5Z2llYTbu3RcS8s8C3S2hNUC",
        )
        u2 = User(
            fname="Alice",
            lname="Wonderson",
            email="alice@example.com",
            # plain pswd: "secret2"
            hashed_password="$2b$12$Th16FzsG7bexKod7DpgKZORxIpoV1E8hu0Xh/jZOhM2hAJV03HKCu",
        )
        db.add_all([u1, u2])
        await db.commit()

        db.add_all(
            [
                Todo(
                    text="Bake french bread",
                    owner=u1,
                ),
                Todo(
                    text="Water flower",
                    owner=u1,
                ),
                Todo(
                    text="Play outdoor tennis",
                    owner=u2,
                ),
            ]
        )
        await db.commit()
