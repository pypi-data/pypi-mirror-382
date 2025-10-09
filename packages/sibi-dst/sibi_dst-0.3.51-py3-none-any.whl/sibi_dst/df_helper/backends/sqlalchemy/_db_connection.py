from typing import Any, Optional

from pydantic import BaseModel, model_validator
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

from ._sql_model_builder import SqlAlchemyModelBuilder


class SqlAlchemyConnectionConfig(BaseModel):
    """
    Configuration class for managing an SQLAlchemy database connection.

    This class provides configurations to establish a connection to a database,
    validate the connection, and dynamically build a SQLAlchemy model for a specific
    table if required. It initializes the database engine using the provided connection URL
    and ensures that the connection and table information are properly validated.

    :ivar connection_url: The URL used to connect to the database.
    :type connection_url: str
    :ivar table: The name of the database table for which a model will be constructed.
    :type table: Optional[str]
    :ivar model: The dynamically built SQLAlchemy model for the specified table.
    :type model: Any
    :ivar engine: The SQLAlchemy engine instance reused for database connections.
    :type engine: Optional[Any]
    """
    connection_url: str
    table: Optional[str] = None
    model: Any = None
    engine: Optional[Any] = None  # Save engine to reuse it

    @model_validator(mode="after")
    def validate_and_initialize(self):
        """
        Validate connection parameters, initialize the engine, and build the dynamic model if necessary.
        """
        # Validate `connection_url`
        if not self.connection_url:
            raise ValueError("`connection_url` must be provided.")

        # Initialize the engine
        self.engine = create_engine(self.connection_url)

        # Validate the connection
        self.validate_connection()
        if not self.table:
            raise ValueError("`table_name` must be provided to build the model.")
        try:
            self.model = SqlAlchemyModelBuilder(self.engine, self.table).build_model()
        except Exception as e:
            raise ValueError(f"Failed to build model for table '{self.table}': {e}")

        return self

    def validate_connection(self):
        """
        Test the database connection by executing a simple query.
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except OperationalError as e:
            raise ValueError(f"Failed to connect to the database: {e}")

