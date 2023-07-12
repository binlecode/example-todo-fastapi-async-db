from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sa_update
from sqlalchemy import delete as sa_delete


# Class level CRUD functions provide common support of CRUD operations
# as mixin for SqlAlchemy models.
# It saves boilerplate code for each model persistence implementation.
# There's a limitation: these class level CRUD functions don't provide
# instance reference of the model. An explicit session.get(Model, id)
# is needed to fetch the instance from the session.


class CrudMixin:

    # There is a big limitation of a class level list or get function:
    # the query can not be built with model specific ORM relationship.
    # Therefore, the query won't be able to support a custom eager fetch,
    # such as `select(..).where(..).options(joinedload(User.todos))`.

    @classmethod
    async def list(cls, db: AsyncSession, limit: int = 10, offset: int = 0):

        query = select(cls).limit(limit).offset(offset)
        users = await db.execute(query)
        # By sqlalchemy doc: use `.scalars()` method to skip the generation of
        # `Row` objects and instead receive ORM entities directly.
        # See: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-orm-entities-and-attributes
        return users.scalars().all()

    @classmethod
    async def get(cls, db: AsyncSession, id):
        query = select(cls).where(cls.id == id)
        rs = await db.execute(query)
        # AsyncResult.first() returns none if no row, or 1-element tuple
        r = rs.first()
        if r:
            (d,) = r  # take the element from the tuple
            return d
        return None

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        db.add(cls(**kwargs))
        await db.commit()

    # About synchronization strategy in ORM update:
    # `synchronize_session` chooses the strategy to update the attributes on
    # objects in the session.
    # In this case `fetch` indicates the list of affected primary keys should
    # be fetched either via a separate select statement or via `returning` if
    # the backend database supports it.
    # Objects locally present in memory will be updated in memory based on
    # these primary key identities. — from SQLAlchemy Documentation
    # See: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#selecting-a-synchronization-strategy
    @classmethod
    async def update(cls, db: AsyncSession, id, **kwargs):
        query = (
            sa_update(cls)
            .where(cls.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete(cls, db: AsyncSession, id):
        query = sa_delete(cls).where(cls.id == id)
        await db.execute(query)
        await db.commit()
