from typing import Any, Optional

from pydantic import BaseModel, model_validator, ConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from sibi_dst.v2.utils import Logger
from ._model_builder import SqlAlchemyModelBuilder


class SqlAlchemyConnectionConfig(BaseModel):
    """
    Configuration for establishing an SQLAlchemy database connection and dynamically building
    an ORM model for a specific table.

    Attributes:
        connection_url (str): The URL used to connect to the database.
        table_name (Optional[str]): The name of the table for which the model will be built.
        model (Any): The dynamically built SQLAlchemy model.
        engine (Optional[Engine]): The SQLAlchemy engine instance.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    connection_url: str
    table: Optional[str] = None
    model: Any = None
    engine: Optional[Engine] = None
    debug: bool = False
    logger: Optional[Logger] = None
    add_relationships: bool = False
    export_models: bool = False
    export_file_name: str = 'models.py'

    @model_validator(mode="after")
    def validate_and_initialize(self) -> "SqlAlchemyConnectionConfig":
        """
        Validate the configuration, initialize the engine, test the connection, and build the model.

        Raises:
            ValueError: If `connection_url` or `table_name` is missing, or if the connection or model
                        building fails.
        """
        self.logger = self.logger or Logger.default_logger(logger_name="sqlalchemy_connection", debug=self.debug)
        self.logger.debug("Validating and initializing SQLAlchemy connection configuration.")
        if not self.connection_url:
            raise ValueError("`connection_url` must be provided.")

        # Initialize the engine.
        self.engine = create_engine(self.connection_url)
        self.logger.debug(f"Engine created for URL")

        # Validate the connection.
        self.validate_connection()

        if not self.table:
            raise ValueError("`table` must be provided to build the model.")

        try:
            builder = SqlAlchemyModelBuilder(self.engine, self.table, self.add_relationships, self.debug, self.logger)
            self.model = builder.build_model()
            if self.export_models:
                builder.export_models_to_file(self.export_file_name)
            self.logger.debug(f"Successfully built model for table: {self.table}")
        except Exception as e:
            raise ValueError(f"Failed to build model for table {self.table}: {e}")

        return self

    def validate_connection(self) -> None:
        """
        Test the database connection by executing a simple query.

        Raises:
            ValueError: If the connection cannot be established.
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            self.logger.debug("Database connection validated.")
        except OperationalError as e:
            raise ValueError(f"Failed to connect to the database: {e}")
