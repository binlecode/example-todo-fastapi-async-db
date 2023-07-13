from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# general support of dynamic filters in ORM query


class FilterMixin:
    @classmethod
    def build_query(cls, filter_conditions: list, query=None):
        """
        Return filtered queryset based on filter condition.
        :param query: pre-defined base query object
        :param filter_conditions: a list of filters, ie: [(key, operator, value)]
        operator list:
            eq for ==
            lt for <
            ge for >=
            in for in_
            like for like
            ilike for ilike
            value could be list or a CSV string
        :return: queryset
        """

        if query is None:
            query = select(cls)

        for fc in filter_conditions:
            try:
                key, op, value = fc
            except ValueError:
                raise Exception(f"Invalid filter: {fc}")
            # get model column by key
            column = getattr(cls, key, None)
            if not column:
                raise Exception(f"Invalid filter column: {key}")

            # build filter with column expression
            # see: https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement
            # translate op `in` to `ColumnElement.in_()`
            if op == "in":
                if isinstance(value, list):
                    fltr = column.in_(value)
                else:
                    fltr = column.in_(value.split(","))
            else:
                # translate op `op` to one of the following possible forms:
                # - `op()`
                # - `op_()`
                # - `__op__()`
                # and use `hasattr` to find the one that is supported by the
                # target ColumnElement
                try:
                    supported_op_form = list(
                        filter(
                            lambda expr: hasattr(column, expr % op),
                            ["%s", "%s_", "__%s__"],
                        )
                    )[0]
                    # get op string with found supported form
                    op_attr = supported_op_form % op
                except IndexError:  # supported op not found for this column
                    raise Exception(f"Invalid filter operator: {op}")
                if value == "null":
                    value = None
                # construct column expression function
                fltr = getattr(column, op_attr)(value)

            # concatenate filter from each filter condition to existing query
            query = query.filter(fltr)
        return query

    @classmethod
    async def filter(cls, db: AsyncSession, filter_conditions: list, query=None):
        qry = cls.build_query(filter_conditions, query)
        rs = await db.execute(qry)
        return rs.scalars().all()
