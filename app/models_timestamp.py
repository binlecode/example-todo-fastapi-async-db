from sqlalchemy import Column, DateTime
from datetime import datetime


# add autotimestamp support for models


class AutoTimestampMixin:
    # ! note that `server_default` takes a SQL expression
    # the python type for `DateTime` columns is datetime.datetime
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=lambda: datetime.utcnow())
