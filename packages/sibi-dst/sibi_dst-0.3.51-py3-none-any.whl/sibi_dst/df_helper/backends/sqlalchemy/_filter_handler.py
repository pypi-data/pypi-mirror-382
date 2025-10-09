import datetime

from sqlalchemy import func, cast
from sqlalchemy.sql.sqltypes import Date, Time


class SqlAlchemyFilterHandler:
    @staticmethod
    def apply_filters_sqlalchemy(query, model, filters):
        """
        Apply Django-like filters to an SQLAlchemy query.

        Args:
            query: The base SQLAlchemy query.
            model: The SQLAlchemy model to filter.
            filters: A dictionary of filters with Django-like syntax.

        Returns:
            query: The filtered SQLAlchemy query.
        """
        # Define operators and their SQLAlchemy equivalents
        dt_operators = ["date", "time"]
        date_operators = ["year", "month", "day", "hour", "minute", "second", "week_day"]

        comparison_operators = [
            "gte", "lte", "gt", "lt", "exact", "in", "range",
            "contains", "startswith", "endswith", "isnull",
        ]

        operation_map = {
            "exact": lambda col, val: col == val,
            "gt": lambda col, val: col > val,
            "gte": lambda col, val: col >= val,
            "lt": lambda col, val: col < val,
            "lte": lambda col, val: col <= val,
            "in": lambda col, val: col.in_(val),
            "range": lambda col, val: col.between(val[0], val[1]),
            "contains": lambda col, val: col.like(f"%{val}%"),
            "startswith": lambda col, val: col.like(f"{val}%"),
            "endswith": lambda col, val: col.like(f"%{val}"),
            "isnull": lambda col, val: col.is_(None) if val else col.isnot(None),
        }

        def parse_filter_value(casting, value):
            """
            Convert filter value to appropriate type based on the casting (e.g., date).
            """
            if casting == "date":
                if isinstance(value, str):
                    return datetime.date.fromisoformat(value)
                if isinstance(value, list):
                    return [datetime.date.fromisoformat(v) for v in value]
            return value

        def handle_date_operator(column, date_op):
            """
            Handle filtering on specific datetime parts (e.g., year, month).
            """
            if date_op == "year":
                return func.extract("year", column)
            elif date_op == "month":
                return func.extract("month", column)
            elif date_op == "day":
                return func.extract("day", column)
            elif date_op == "hour":
                return func.extract("hour", column)
            elif date_op == "minute":
                return func.extract("minute", column)
            elif date_op == "second":
                return func.extract("second", column)
            elif date_op == "week_day":
                # SQLAlchemy uses 1 for Sunday, 2 for Monday, etc.
                return func.strftime("%w", column)
            else:
                raise ValueError(f"Unsupported date operator: {date_op}")

        for key, value in filters.items():
            parts = key.split("__")
            field_name = parts[0]
            casting = None
            operation = "exact"

            if len(parts) == 3:
                # Adjust logic based on the parts
                _, casting, operation = parts
            elif len(parts) == 2:
                # Could be either a casting or an operation
                if parts[1] in comparison_operators:
                    operation = parts[1]
                elif parts[1] in dt_operators + date_operators:
                    casting = parts[1]

            # Get the column from the model
            column = getattr(model, field_name, None)
            # column = model.__table__.columns.get(field_name)
            if not column:
                raise AttributeError(f"Field '{field_name}' not found in model '{model.__name__}'")

            # Convert the filter value to the correct type
            parsed_value = parse_filter_value(casting, value)

            # Handle casting (e.g., date, time)
            if casting == "date":
                column = cast(column, Date)
            elif casting == "time":
                column = cast(column, Time)

            # Handle specific datetime parts (e.g., year, month)
            if casting in date_operators:
                column = handle_date_operator(column, casting)

            # Apply the filter operation
            if operation in operation_map:
                condition = operation_map[operation](column, parsed_value)
                query = query.filter(condition)
            else:
                raise ValueError(f"Unsupported operation: {operation}")

        return query
