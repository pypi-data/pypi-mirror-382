import asyncio
import datetime
import logging
import warnings
from typing import Any, Dict, TypeVar
from typing import Union, Optional

import dask.dataframe as dd
from dask import delayed, compute
import pandas as pd
from pydantic import BaseModel
import fsspec

from sibi_dst.df_helper.core import QueryConfig, ParamsConfig, FilterHandler
from sibi_dst.utils import Logger
from sibi_dst.utils import ParquetSaver, ClickHouseWriter
from .backends.django import *
from .backends.http import HttpConfig
from .backends.parquet import ParquetConfig
from .backends.sqlalchemy import *

# Define a generic type variable for BaseModel subclasses
T = TypeVar("T", bound=BaseModel)

# It is considered acceptable in Django to access protected class members
warnings.filterwarnings(
    "ignore",
    message="Access to a protected member _meta",
    category=UserWarning,
)


class DfHelper:
    """
    DfHelper is a utility class for managing, loading, and processing data from
    various backends, such as Django databases, Parquet files, HTTP sources, and
    SQLAlchemy-based databases. The class abstracts the complexities of handling
    different backends and provides a unified interface for data operations.

    The class is particularly useful for projects that require flexibility in
    data source configuration and seamless integration with both Dask and Pandas
    for handling data frames. It includes robust mechanisms for post-processing
    data, filtering columns, renaming, and setting indices.

    :ivar df: The DataFrame currently being processed or loaded.
    :type df: Union[dd.DataFrame, pd.DataFrame]
    :ivar backend_django: Configuration for interacting with Django database backends.
    :type backend_django: Optional[DjangoConnectionConfig]
    :ivar _backend_query: Internal configuration for query handling.
    :type _backend_query: Optional[QueryConfig]
    :ivar _backend_params: Internal parameters configuration for DataFrame handling.
    :type _backend_params: Optional[ParamsConfig]
    :ivar backend_parquet: Configuration for Parquet file handling.
    :type backend_parquet: Optional[ParquetConfig]
    :ivar backend_http: Configuration for interacting with HTTP-based backends.
    :type backend_http: Optional[HttpConfig]
    :ivar backend_sqlalchemy: Configuration for interacting with SQLAlchemy-based databases.
    :type backend_sqlalchemy: Optional[SqlAlchemyConnectionConfig]
    :ivar parquet_filename: The filename for a Parquet file, if applicable.
    :type parquet_filename: str
    :ivar logger: Logger instance used for debugging and information logging.
    :type logger: Logger
    :ivar default_config: Default configuration dictionary that can be overridden.
    :type default_config: Dict
    """
    df: Union[dd.DataFrame, pd.DataFrame] = None
    backend_django: Optional[DjangoConnectionConfig] = None
    _backend_query: Optional[QueryConfig] = None
    _backend_params: Optional[ParamsConfig] = None
    backend_parquet: Optional[ParquetConfig] = None
    backend_http: Optional[HttpConfig] = None
    backend_sqlalchemy: Optional[SqlAlchemyConnectionConfig] = None
    parquet_filename: str = None
    logger: Logger
    default_config: Dict = None

    def __init__(self, backend='django_db', **kwargs):
        # Ensure default_config is not shared across instances
        self.default_config = self.default_config or {}
        kwargs = {**self.default_config.copy(), **kwargs}
        self.backend = backend
        self.debug = kwargs.setdefault("debug", False)
        self.logger = kwargs.get("logger", Logger.default_logger(logger_name=self.__class__.__name__))
        # Configure logger level
        self.logger.set_level(logging.DEBUG if self.debug else logging.INFO)
        self.logger.debug("Logger initialized in DEBUG mode.")
        self.parquet_storage_path = kwargs.setdefault("parquet_storage_path", None)
        self.dt_field = kwargs.setdefault("dt_field", None)
        self.as_pandas = kwargs.setdefault("as_pandas", False)
        self.filesystem = kwargs.pop('filesystem', 'file')
        self.filesystem_options = kwargs.pop('filesystem_options', {})
        kwargs.setdefault("live", True)
        kwargs.setdefault("logger", self.logger)
        self.fs =kwargs.setdefault("fs", fsspec.filesystem('file'))
        self.__post_init(**kwargs)

    def __str__(self):
        return self.__class__.__name__

    def __call__(self, **options):
        return self.load(**options)

    def __post_init(self, **kwargs):
        """
        Initializes backend-specific configurations based on the provided backend type and other
        parameters. This method performs configuration setup dependent on the selected backend,
        such as 'django_db', 'parquet', 'http', or 'sqlalchemy'. Configuration for each backend
        type is fetched or instantiated as necessary using provided parameters or default values.

        :param kwargs: Dictionary of arguments passed during initialization of backend configurations.
                       Additional parameters for specific backend types are extracted here.
        :return: None
        """
        self.logger.debug(f"backend used: {self.backend}")
        self.logger.debug(f"kwargs passed to backend plugins: {kwargs}")
        self._backend_query = self.__get_config(QueryConfig, kwargs)
        self._backend_params = self.__get_config(ParamsConfig, kwargs)
        if self.backend == 'django_db':
            self.backend_django = self.__get_config(DjangoConnectionConfig, kwargs)
        elif self.backend == 'parquet':
            self.parquet_filename = kwargs.setdefault("parquet_filename", None)
            self.backend_parquet = ParquetConfig(**kwargs)
        elif self.backend == 'http':
            self.backend_http = HttpConfig(**kwargs)
        elif self.backend == 'sqlalchemy':
            self.backend_sqlalchemy = self.__get_config(SqlAlchemyConnectionConfig, kwargs)


    def __get_config(self, model: [T], kwargs: Dict[str, Any]) -> Union[T]:
        """
        Initializes a Pydantic model with the keys it recognizes from the kwargs,
        and removes those keys from the kwargs dictionary.
        :param model: The Pydantic model class to initialize.
        :param kwargs: The dictionary of keyword arguments.
        :return: The initialized Pydantic model instance.
        """
        # Extract keys that the model can accept
        recognized_keys = set(model.__annotations__.keys())
        self.logger.debug(f"recognized keys: {recognized_keys}")
        model_kwargs = {k: kwargs.pop(k) for k in list(kwargs.keys()) if k in recognized_keys}
        self.logger.debug(f"model_kwargs: {model_kwargs}")
        return model(**model_kwargs)

    def load_parallel(self, **options):
        """
        Executes the `load` method in parallel using Dask, allowing multiple instances
        to run concurrently. This function leverages Dask's `delayed` and `compute`
        methods to schedule and process tasks in parallel. It is designed to handle
        concurrent workloads efficiently by utilizing up to 4 parallel executions of
        the `load` function.

        :param options: Keyword arguments to be passed to the `load` method. These options
            will be applied to all parallel instances of the `load` method.
        :return: A list of results, where each element represents the output
            from one of the parallel executions of the `load` method.
        """
        # Define tasks using Dask's delayed
        tasks = [delayed(self.load)(**options) for _ in range(4)]
        results = compute(*tasks)
        return results

    def load(self, **options):
        """
        Loads data from a dataframe backend, ensuring compatibility with multiple
        data processing backends. Provides the data in a pandas dataframe format
        if the `as_pandas` attribute is set to True.

        :param options: Arbitrary keyword arguments for dataframe loading customization.
        :type options: dict
        :return: The loaded dataframe, computed as a pandas dataframe if
            `as_pandas` is set to True, or kept in its native backend format otherwise.
        """
        # this will be the universal method to load data from a df irrespective of the backend
        df = self.__load(**options)
        if self.as_pandas:
            return df.compute()
        return df

    def __load(self, **options):
        """
        Private method responsible for loading data using a specified backend. This method
        abstracts away the details of interacting with the backend and dynamically calls the
        appropriate function depending on the backend type. It supports multiple backend
        types, such as `django_db`, `sqlalchemy`, `parquet`, and `http`. If the `http` backend
        is selected, it checks whether the asyncio event loop is running and either runs the
        process as a new asyncio task or synchronously.

        :param options: Arbitrary keyword arguments provided for backend-specific configurations.
                        These should align with the requirements of the chosen backend.
        :type options: dict

        :return: The data loaded from the specified backend. The return type is dependent on
                 the particular backend being used.
        :rtype: Depending on backend implementation; could be `Task`, `List`, `Dict`, or
                another format defined by the backend.
        """
        if self.backend == 'django_db':
            self._backend_params.parse_params(options)
            return self.__load_from_db(**options)
        elif self.backend == 'sqlalchemy':
            self._backend_params.parse_params(options)
            return self.__load_from_sqlalchemy(**options)
        elif self.backend == 'parquet':
            return self.__load_from_parquet(**options)
        elif self.backend == 'http':
            if asyncio.get_event_loop().is_running():
                self.logger.debug("Running as a task from an event loop")
                return asyncio.create_task(self.__load_from_http(**options))
            else:
                self.logger.debug("Regular asyncio run...")
                return asyncio.run(self.__load_from_http(**options))

    def __load_from_sqlalchemy(self, **options):
        """
        Loads data from an SQLAlchemy database source into a dataframe. The method processes
        the loaded data and applies post-processing to transform it into the desired structure.
        If the operation fails, an empty pandas DataFrame is created as a fallback.

        :param options: Additional keyword arguments to configure the data loading process.
            These options can include configurations such as 'debug' and other parameters
            required by the `SqlAlchemyLoadFromDb` class.
        :type options: dict
        :return: A dataframe containing the data loaded from the SQLAlchemy database.
        :rtype: dask.dataframe.DataFrame
        """
        try:
            options.setdefault("debug", self.debug)
            db_loader = SqlAlchemyLoadFromDb(
                self.backend_sqlalchemy,
                self._backend_query,
                self._backend_params,
                self.logger,
                **options
            )
            self.df = db_loader.build_and_load()
            self.__process_loaded_data()
            self.__post_process_df()
            self.logger.debug("Data successfully loaded from sqlalchemy database.")
        except Exception as e:
            self.logger.debug(f"Failed to load data from sqlalchemy database: {e}: options: {options}")
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)

        return self.df

    def __load_from_db(self, **options) -> Union[pd.DataFrame, dd.DataFrame]:
        """
        Loads data from a Django database using a specific backend query mechanism. Processes the loaded data
        and applies further post-processing before returning the dataframe. If the operation fails, an
        empty dataframe with a single partition is returned instead.

        :param options: Additional settings for the database loading process, which include optional configurations
            like debug mode, among others.
        :type options: dict
        :return: A dataframe containing the loaded data either as a Pandas or Dask dataframe.
        :rtype: Union[pd.DataFrame, dd.DataFrame]
        """
        try:
            options.setdefault("debug", self.debug)
            db_loader = DjangoLoadFromDb(
                self.backend_django,
                self._backend_query,
                self._backend_params,
                self.logger,
                **options
            )
            self.df = db_loader.build_and_load()
            self.__process_loaded_data()
            self.__post_process_df()
            self.logger.debug("Data successfully loaded from django database.")
        except Exception as e:
            self.logger.debug(f"Failed to load data from django database: {e}")
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)

        return self.df

    async def __load_from_http(self, **options) -> Union[pd.DataFrame, dd.DataFrame]:
        """
        Loads data asynchronously from an HTTP source using the configured HTTP plugin.
        If the HTTP plugin is not properly configured, this method logs a debug message and
        returns an empty Dask DataFrame. If an exception occurs during data fetching, the error
        is logged and an empty Dask DataFrame with one partition is returned.

        :param options: Additional keyword arguments that are passed to the HTTP plugin for
                        fetching the data.
        :returns: A DataFrame object that can either be a pandas or a Dask DataFrame. When the
                  fetching operation fails, it defaults to returning an empty Dask DataFrame
                  with a single partition.
        """
        if not self.backend_http:
            self.logger.debug("HTTP plugin not configured properly.")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)
        try:
            self.df = await self.backend_http.fetch_data(**options)
        except Exception as e:
            self.logger.debug(f"Failed to load data from http plugin: {e}")
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)
        return self.df

    def __post_process_df(self):
        """
        Processes a DataFrame according to the provided parameters defined within the
        `self._backend_params.df_params` dictionary. This involves filtering columns,
        renaming columns, setting an index column, and handling datetime indexing.
        The method modifies the DataFrame in place.

        :raises ValueError: If the lengths of `fieldnames` and `column_names` do not match,
            or if the specified `index_col` is not found in the DataFrame.
        """
        df_params = self._backend_params.df_params
        fieldnames = df_params.get("fieldnames", None)
        index_col = df_params.get("index_col", None)
        datetime_index = df_params.get("datetime_index", False)
        column_names = df_params.get("column_names", None)

        # Filter columns
        if fieldnames:
            existing_columns = set(self.df.columns)
            valid_fieldnames = list(filter(existing_columns.__contains__, fieldnames))
            self.df = self.df[valid_fieldnames]

        # Rename columns
        if column_names is not None:
            if len(fieldnames) != len(column_names):
                raise ValueError(
                    f"Length mismatch: fieldnames ({len(fieldnames)}) and column_names ({len(column_names)}) must match."
                )
            rename_mapping = dict(zip(fieldnames, column_names))
            self.df = self.df.map_partitions(lambda df: df.rename(columns=rename_mapping))

        # Set index column
        if index_col is not None:
            if index_col in self.df.columns:
                self.df = self.df.set_index(index_col)
            else:
                raise ValueError(f"Index column '{index_col}' not found in DataFrame.")

        # Handle datetime index
        if datetime_index and self.df.index.dtype != 'datetime64[ns]':
            self.df = self.df.map_partitions(lambda df: df.set_index(pd.to_datetime(df.index, errors='coerce')))

        self.logger.debug("Post-processing of DataFrame completed.")

    def __process_loaded_data(self):
        """
        Processes the dataframe by applying renaming logic based on the given field map
        configuration. Inspects the dataframe for missing columns referenced in the field
        map and flags them with a warning. Applies renaming only for columns that exist
        in the dataframe while ensuring that no operations take place if the dataframe
        is empty.

        :param self: The instance of the class where the dataframe is being processed.
        :type self: object with attributes `df`, `_backend_params`, and `logger`.

        :raises Warning: Logs a warning if specified columns in the `field_map` are not
            present in the dataframe.

        :return: None
        """
        self.logger.debug(f"Type of self.df: {type(self.df)}")
        if self.df.map_partitions(len).compute().sum() > 0:
            field_map = self._backend_params.field_map or {}
            if isinstance(field_map, dict):
                rename_mapping = {k: v for k, v in field_map.items() if k in self.df.columns}
                missing_columns = [k for k in field_map.keys() if k not in self.df.columns]

                if missing_columns:
                    self.logger.warning(
                        f"The following columns in field_map are not in the DataFrame: {missing_columns}")

                def rename_columns(df, mapping):
                    return df.rename(columns=mapping)

                if rename_mapping:
                    # Apply renaming
                    self.df = self.df.map_partitions(rename_columns, mapping=rename_mapping)

            self.logger.debug("Processing of loaded data completed.")

    def save_to_parquet(self, parquet_filename: Optional[str] = None, **kwargs):
        """
        Save the dataframe result to a Parquet file using specified configurations.

        This method leverages the ParquetSaver class to store the dataframe result
        into a Parquet file. It also provides functionality for overriding the default
        filesystem (`fs`) and storage path (`parquet_storage_path`). The method logs
        details about the saving operation for debugging purposes.

        :param parquet_filename: The name of the Parquet file to save the dataframe to.
                                  If not provided, a default name will be used.
        :param kwargs: Additional arguments to customize the saving process. These may
                       include:
                       - `fs`: Filesystem to be used for saving Parquet files. If not
                         provided, defaults to the instance's filesystem attribute.
                       - `parquet_storage_path`: The root path in the filesystem where
                         Parquet files should be saved. If not provided, defaults to
                         the instance's attribute for storage path.
        :return: None
        """
        fs = kwargs.pop('fs', self.fs)
        parquet_storage_path = kwargs.pop('parquet_storage_path', self.parquet_storage_path)
        ps = ParquetSaver(df_result=self.df, parquet_storage_path=parquet_storage_path, logger=self.logger, fs=fs)
        ps.save_to_parquet(parquet_filename)
        self.logger.debug(f"Parquet saved to {parquet_filename} in parquet storage: {parquet_storage_path}.")

    def save_to_clickhouse(self, **credentials):
        """
        Saves the current DataFrame to ClickHouse using the provided credentials. This
        method first checks if the DataFrame is empty. If it is empty, the method logs
        a debug message and does not proceed with saving. Otherwise, it initializes
        a ClickHouseWriter instance and uses it to save the DataFrame to ClickHouse,
        logging a debug message upon successful completion.

        :param credentials: Credentials required to connect to ClickHouse as keyword
            arguments.
        :type credentials: dict
        :return: None
        """
        if self.df.map_partitions(len).compute().sum() == 0:
            self.logger.debug("Cannot write to clickhouse since Dataframe is empty")
            return
        cs = ClickHouseWriter(logger=self.logger, **credentials)
        cs.save_to_clickhouse(self.df)
        self.logger.debug("Save to ClickHouse completed.")

    def __load_from_parquet(self, **options) -> Union[pd.DataFrame, dd.DataFrame]:
        """
        Loads data from parquet files into a DataFrame, applies provided filters, and handles exceptions.

        This method leverages a backend-specific implementation to load data from parquet files into a
        DataFrame. If additional options are provided and the data is successfully loaded, filters are
        applied to the DataFrame using a filter handler. Errors during this process are handled gracefully
        by logging the issue and returning an empty Dask DataFrame.

        :param options: A dictionary of filter options to be applied to the DataFrame.
        :type options: dict

        :return: A DataFrame containing the loaded and filtered data. If the operation fails, an empty
            Dask DataFrame is returned.
        :rtype: Union[pd.DataFrame, dd.DataFrame]
        """
        try:
            self.df = self.backend_parquet.load_files()
            if options and self.df is not None:
                """
                deprecated specific filter handling to a generic one
                self.df = ParquetFilterHandler(logger=self.logger).apply_filters_dask(self.df, options)

                """
                self.df = FilterHandler(backend='dask', logger=self.logger).apply_filters(self.df, filters=options)
            return self.df
        except Exception as e:
            self.logger.debug(f"Failed to load data from parquet: {e}")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)

    def load_period(self, **kwargs):
        """
        Loads a period with specified parameters.

        This method acts as a wrapper around the private ``__load_period`` method. It
        accepts arbitrary keyword arguments that are passed directly to the private
        method for execution. The purpose of allowing keyword arguments is to permit
        flexible configuration or parameterization for loading a specific period, based
        on the internal implementation of the private ``__load_period`` method.

        Note:
        The arguments and return values are entirely determined by the private
        method's behavior. This method is intentionally designed to mask details
        of the internal logic behind the abstraction.

        :param kwargs: Arbitrary keyword arguments to parameterize the internal logic
            of loading a period. The specific keys and values expected by the
            ``__load_period`` method depend on its own internal implementation.
        :return: The result of calling the private ``__load_period`` method with the
            provided keyword arguments. The return type is dependent on the internal
            implementation of ``__load_period``.
        """
        return self.__load_period(**kwargs)

    def __load_period(self, **kwargs):
        """
        Validates and processes the temporal filtering parameters `start` and `end` for querying,
        ensuring correctness and compatibility with a specified backend (Django or SQLAlchemy).
        This method dynamically maps and validates the provided datetime or date field from the
        model according to the configured backend, and applies the appropriate filters to query objects.

        This function enforces that both `start` and `end` are provided and checks if the start date
        is earlier or the same as the end date. It supports parsing string representations of dates
        and validates them against the date or datetime fields associated with the chosen backend.
        If the backend or field is incompatible or missing, appropriate errors are raised.

        The resulting filter conditions are integrated into `kwargs` for querying with the
        appropriate backend model.

        :param kwargs: Keyword arguments, including temporal filtering parameters and optionally a
            datetime or date field name. Supported parameters include:
            - **dt_field**: The name of the date or datetime field to use in filtering. Defaults
              to an internally set field if not explicitly provided.
            - **start**: The starting date or datetime for the query range. Can be a `str` or
              `datetime.date/datetime.datetime` object.
            - **end**: The ending date or datetime for the query range. Can be a `str` or
              `datetime.date/datetime.datetime` object.

        :return: Queryset or result of the load function with the applied temporal filters.
        :rtype: Any

        :raises ValueError: If the `dt_field` is not provided, if `start` or `end`
            are missing, if the `start` date is later than `end`, or if the `dt_field`
            does not exist in the backend model or its metadata.
        """
        dt_field = kwargs.pop("dt_field", self.dt_field)
        if dt_field is None:
            raise ValueError("dt_field must be provided")

        start = kwargs.pop("start", None)
        end = kwargs.pop("end", None)

        # Ensure start and end are provided
        if start is None or end is None:
            raise ValueError("Both 'start' and 'end' must be provided.")

        # Parse string dates
        if isinstance(start, str):
            start = self.parse_date(start)
        if isinstance(end, str):
            end = self.parse_date(end)

        # Validate that start <= end
        if start > end:
            raise ValueError("The 'start' date cannot be later than the 'end' date.")

        # Reverse map to original field name
        field_map = getattr(self._backend_params, 'field_map', {}) or {}
        reverse_map = {v: k for k, v in field_map.items()}
        mapped_field = reverse_map.get(dt_field, dt_field)

        # Common logic for Django and SQLAlchemy
        if self.backend == 'django_db':
            model_fields = {field.name: field for field in self.backend_django.model._meta.get_fields()}
            if mapped_field not in model_fields:
                raise ValueError(f"Field '{dt_field}' does not exist in the Django model.")
            field_type = type(model_fields[mapped_field]).__name__
            is_date_field = field_type == 'DateField'
            is_datetime_field = field_type == 'DateTimeField'
        elif self.backend == 'sqlalchemy':
            model = self.backend_sqlalchemy.model
            fields = [column.name for column in model.__table__.columns]
            if mapped_field not in fields:
                raise ValueError(f"Field '{dt_field}' does not exist in the SQLAlchemy model.")
            column = getattr(model, mapped_field)
            field_type = str(column.type).upper()
            is_date_field = field_type == 'DATE'
            is_datetime_field = field_type == 'DATETIME'
        else:
            raise ValueError(f"Unsupported backend '{self.backend}'")
            # Build query filters
        if start == end:
            if is_date_field:
                kwargs[mapped_field] = start
            elif is_datetime_field:
                kwargs[f"{mapped_field}__date"] = start
        else:
            if is_date_field:
                kwargs[f"{mapped_field}__gte"] = start
                kwargs[f"{mapped_field}__lte"] = end
            elif is_datetime_field:
                kwargs[f"{mapped_field}__date__gte"] = start
                kwargs[f"{mapped_field}__date__lte"] = end
        self.logger.debug(f"load_period kwargs: {kwargs}")
        return self.load(**kwargs)

    @staticmethod
    def parse_date(date_str: str) -> Union[datetime.datetime, datetime.date]:
        """
        Parses a date string and converts it to a `datetime.datetime` or
        `datetime.date` object.

        This method attempts to parse the given string in two distinct formats:
        1. First, it tries to interpret the string as a datetime with the format
           ``%Y-%m-%d %H:%M:%S``. If successful, it returns a `datetime.datetime`
           object.
        2. If the first format parsing fails, it attempts to parse the string as
           a date with the format ``%Y-%m-%d``. If successful, it returns a
           `datetime.date` object.

        If the string cannot be parsed in either of these formats, the method will
        raise a `ValueError`.

        :param date_str: The date string to be parsed. Expected to match one of the
            formats: ``%Y-%m-%d %H:%M:%S`` or ``%Y-%m-%d``.
        :type date_str: str
        :return: A `datetime.datetime` object if the string matches the first format,
            or a `datetime.date` object if the string matches the second format.
        :rtype: Union[datetime.datetime, datetime.date]
        :raises ValueError: Raised if neither date format can be successfully parsed
            from the provided string.
        """
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
