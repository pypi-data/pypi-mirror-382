import re

from sqlalchemy import MetaData, Table
from sqlalchemy.orm import declarative_base, relationship

# Base class for dynamically created models
Base = declarative_base()

apps_label = "datacubes"


class SqlAlchemyModelBuilder:
    """
    Provides functionality for building SQLAlchemy ORM models dynamically from
    reflected database tables. This class is intended for use with a SQLAlchemy
    engine and metadata to automatically generate ORM models for specified
    database tables.

    The primary purpose of this class is to simplify the process of creating
    SQLAlchemy ORM models by reflecting tables from a connected database,
    dynamically generating model classes, and handling relationships between
    tables.

    :ivar engine: SQLAlchemy engine connected to the database.
    :type engine: Engine
    :ivar table_name: Name of the table for which the model is generated.
    :type table_name: str
    :ivar metadata: SQLAlchemy MetaData instance for reflecting tables.
    :type metadata: MetaData
    :ivar table: Reflected SQLAlchemy Table object for the specified table name.
    :type table: Optional[Table]
    :ivar class_name: Dynamically normalized class name derived from table_name.
    :type class_name: str
    """
    _model_cache = {}  # Local cache for model classes

    def __init__(self, engine, table_name):
        """
        Initialize the model builder with a database engine and specific table.

        Args:
            engine: SQLAlchemy engine connected to the database.
            table_name (str): Name of the table to generate the model for.
        """
        self.engine = engine
        self.table_name = table_name
        self.metadata = MetaData()
        self.table = None  # Placeholder for the specific table
        self.class_name = self.normalize_class_name(self.table_name)

    def build_model(self) -> type:
        """
        Builds and returns a database model class corresponding to the specified table name.
        The method checks if the model is already registered in the ORM's registry. If not,
        it reflects the database schema of the specified table and dynamically creates the
        model class.

        :raises ValueError: If the specified table does not exist in the database.
        :return: A database model class corresponding to the specified table name.
        :rtype: type
        """
        # Check if the model is already registered
        model = Base.registry._class_registry.get(self.class_name)
        if model:
            return model

        self.metadata.reflect(only=[self.table_name], bind=self.engine)
        self.table = self.metadata.tables.get(self.table_name)
        if self.table is None:
            raise ValueError(f"Table '{self.table_name}' does not exist in the database.")

        model = self.create_model()
        return model

    def create_model(self) -> type:
        """
        Generates a SQLAlchemy model class dynamically based on the specified table and
        its columns. The method extracts column information, defines the necessary
        attributes, and creates the model class if it doesn't already exist in the
        SQLAlchemy base registry.

        :raises KeyError: If the table or table name does not exist in the provided
            schema.
        :raises Exception: If the model creation fails for any reason.

        :return: The dynamically created or fetched model class.
        :rtype: type
        """
        # Normalize the class name from the table name
        columns = self.get_columns(self.table)

        # Define attributes for the model class
        attrs = {
            "__tablename__": self.table_name,
            "__table__": self.table,
            "__module__": f"{apps_label}.models",
            "__mapper_args__": {"eager_defaults": True},
        }

        # Add columns and relationships to the model
        attrs.update(columns)
        #self.add_relationships(attrs, self.table)
        model = Base.registry._class_registry.get(self.class_name)
        if not model:
            model = type(self.class_name, (Base,), attrs)
            # Add the class to Base.registry so it is registered
            Base.registry._class_registry[self.class_name] = model
        return model

    def get_columns(self, table: Table):
        """
        Extracts and returns a dictionary of column names and their corresponding column
        objects from a given table, excluding reserved names. Reserved names are used
        internally and should not overlap with column names in the provided table. The
        method ensures sanitized column names through normalization and filters out any
        column matching reserved keywords.

        :param table: The table object from which columns are to be extracted.
        :type table: Table
        :return: A dictionary containing the sanitized column names as keys and their
            corresponding column objects as values, excluding reserved names.
        :rtype: dict
        """
        columns = {}
        reserved_names = ["metadata", "class_", "table"]

        for column in table.columns:
            column_name = self.normalize_column_name(column.name)
            if column_name not in reserved_names:
                columns[column_name] = column
        return columns

    def add_relationships(self, attrs, table: Table):
        """
        Adds relationships to the provided attributes dictionary for a given database table.

        This method iterates through the foreign keys of the provided table, constructs
        relationship attributes, and updates the attributes dictionary with relationships
        that connect the current table to related tables.

        :param attrs: Dictionary of attributes to which relationships will be added.
                      The dictionary will be updated with new relationship mappings.
        :type attrs: dict
        :param table: A database table object containing foreign key relationships.
                      The method will use this table to establish relationships.
        :return: None
        """
        for fk in table.foreign_keys:
            related_table_name = fk.column.table.name
            related_class_name = self.normalize_class_name(related_table_name)
            relationship_name = self.normalize_column_name(related_table_name)
            attrs[relationship_name] = relationship(related_class_name, back_populates=None)


    @staticmethod
    def normalize_class_name(table_name: str) -> str:
        """
        Generate a normalized class name from a given table name by capitalizing
        each word separated by underscores and concatenating them.

        This static method takes a string representation of a table name, where
        words are separated by underscores, and converts it into a camel case
        class name. It processes the string by capitalizing the first letter of
        each word and removing the underscores. The normalized class name
        returned can be used programmatically for various purposes, such as
        class generation or naming conventions.

        :param table_name: The table name to normalize, with words separated by
            underscores. E.g., 'sample_table' becomes 'SampleTable'.
        :type table_name: str
        :return: A normalized class name in camel case format.
        :rtype: str
        """
        return "".join(word.capitalize() for word in table_name.split("_"))

    @staticmethod
    def normalize_column_name(column_name: str) -> str:
        """
        Normalize a column name by replacing any non-word characters or leading numbers
        with underscores, while ensuring it does not conflict with reserved keywords
        such as 'class', 'def', 'return', etc. If the normalized name conflicts with
        a Python reserved keyword, "_field" is appended to it.

        :param column_name: The original name of the column to be normalized.
        :type column_name: str
        :return: A normalized column name that is safe and compatible for usage
            in various contexts such as database columns or Python code.
        :rtype: str
        """
        column_name = re.sub(r"\W|^(?=\d)", "_", column_name)
        if column_name in {"class", "def", "return", "yield", "global"}:
            column_name += "_field"
        return column_name
