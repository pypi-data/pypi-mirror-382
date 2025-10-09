from typing import Any, Optional

from pydantic import BaseModel, model_validator, ConfigDict
from sqlmodel import create_engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from sibi_dst.v2.utils import Logger
from ._model_builder import SQLModelModelBuilder  # Refactored builder for SQLModel


class SQLModelConnectionConfig(BaseModel):
    """
    Configuration for establishing an SQLModel database connection and dynamically building
    an ORM model for a specific table.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    connection_url: str
    table: Optional[str] = None
    model: Any = None
    engine: Optional[Any] = None
    debug: bool = False
    logger: Optional[Logger] = None
    add_relationships: bool = False
    export_models: bool = False
    export_file_name: str = 'models.py'

    @model_validator(mode="after")
    def validate_and_initialize(self) -> "SQLModelConnectionConfig":
        """
        Validates the configuration, initializes the engine, tests the connection,
        and builds the ORM model for the specified table.
        """
        self.logger = self.logger or Logger.default_logger(logger_name="sqlmodel_connection", debug=self.debug)
        self.logger.debug("Validating and initializing SQLModel connection configuration.")

        if not self.connection_url:
            raise ValueError("`connection_url` must be provided.")

        # Initialize the engine using SQLModel's create_engine.
        self.engine = create_engine(self.connection_url)
        self.logger.debug("Engine created for connection URL.")

        # Validate the connection.
        self.validate_connection()

        if not self.table:
            raise ValueError("`table` must be provided to build the model.")

        try:
            builder = SQLModelModelBuilder(
                self.engine,
                self.table,
                self.add_relationships,
                self.debug,
                self.logger
            )
            self.model = builder.build_model()
            if self.export_models:
                builder.export_models_to_file(self.export_file_name)
            self.logger.debug(f"Successfully built model for table: {self.table}")
        except Exception as e:
            raise ValueError(f"Failed to build model for table {self.table}: {e}")

        return self

    def validate_connection(self) -> None:
        """
        Tests the database connection by executing a simple query.
        Raises:
            ValueError: If the connection cannot be established.
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            self.logger.debug("Database connection validated.")
        except OperationalError as e:
            raise ValueError(f"Failed to connect to the database: {e}")