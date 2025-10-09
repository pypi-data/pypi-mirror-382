import datetime
import logging
from typing import Optional, Any, Dict

import dask.dataframe as dd
import fsspec

from sibi_dst.df_helper import DfHelper
from sibi_dst.utils import DataWrapper, DateUtils, Logger


class ParquetArtifact(DfHelper):
    """
    Class designed to manage Parquet data storage and retrieval using a specified
    DataWrapper class for data processing. It provides functionality for loading,
    updating, rebuilding, and generating Parquet files within a configurable
    storage filesystem. The class ensures that all essential configurations and
    filesystems are properly set up before operations.

    Detailed functionality includes support for dynamically managing and generating
    Parquet files based on time periods, with customizable options for paths,
    filenames, date fields, and more. It is an abstraction for efficiently handling
    storage tasks related to distributed or local file systems.

    :ivar config: Configuration dictionary containing all configurable parameters
                  for managing Parquet data storage, such as paths, filenames,
                  and date ranges.
    :type config: dict
    :ivar df: Cached Dask DataFrame used to store and manipulate data loaded
              from the Parquet file.
    :type df: Optional[dask.dataframe.DataFrame]
    :ivar data_wrapper_class: Class responsible for abstracting data processing
                              operations required for Parquet file generation.
    :type data_wrapper_class: type
    :ivar date_field: Name of the field used to identify and process data by date.
    :type date_field: Optional[str]
    :ivar parquet_storage_path: Filesystem path to store Parquet files.
    :type parquet_storage_path: Optional[str]
    :ivar parquet_filename: Name of the Parquet file to be generated and managed.
    :type parquet_filename: Optional[str]
    :ivar parquet_start_date: Date string specifying the start date for data range
                              processing.
    :type parquet_start_date: Optional[str]
    :ivar parquet_end_date: Date string specifying the end date for data range
                            processing.
    :type parquet_end_date: Optional[str]
    :ivar filesystem_type: Type of the filesystem used for managing storage
                           operations (e.g., `file`, `s3`, etc.).
    :type filesystem_type: str
    :ivar filesystem_options: Additional options for configuring the filesystem.
    :type filesystem_options: dict
    :ivar fs: Filesystem object used for storage operations.
    :type fs: fsspec.AbstractFileSystem
    """
    DEFAULT_CONFIG = {
        'backend': 'parquet'
    }

    def __init__(self, data_wrapper_class,  **kwargs):
        """
        Initializes an instance of the class with given configuration and validates
        required parameters. Sets up the filesystem to handle storage, ensuring
        necessary directories exist. The configuration supports a variety of options
        to manage parquet storage requirements, including paths, filenames, and date
        ranges.

        :param data_wrapper_class: The class responsible for wrapping data to be managed
                                   by this instance.
        :type data_wrapper_class: type
        :param kwargs: Arbitrary keyword arguments to override default configuration.
                       Includes settings for `date_field`, `parquet_storage_path`,
                       `parquet_filename`, `parquet_start_date`, `parquet_end_date`,
                       `filesystem_type`, `filesystem_options`, and `fs`.
        :type kwargs: dict

        :raises ValueError: If any of the required configuration options
                            (`date_field`, `parquet_storage_path`,
                            `parquet_filename`, `parquet_start_date`,
                            or `parquet_end_date`) are missing or not set properly.
        """
        self.config = {
            **self.DEFAULT_CONFIG,
            **kwargs,
        }
        self.df: Optional[dd.DataFrame] = None
        self.debug = self.config.setdefault('debug', False)
        self.logger = self.config.setdefault('logger',Logger.default_logger(logger_name=f'parquet_artifact_{__class__.__name__}'))
        self.logger.set_level(logging.DEBUG if self.debug else logging.INFO)
        self.data_wrapper_class = data_wrapper_class
        self.class_params = self.config.setdefault('class_params', None)
        self.load_params = self.config.setdefault('load_params', None)
        self.date_field = self.config.setdefault('date_field', None)
        if self.date_field is None:
            raise ValueError('date_field must be set')
        self.parquet_storage_path = self.config.setdefault('parquet_storage_path', None)
        if self.parquet_storage_path is None:
            raise ValueError('parquet_storage_path must be set')

        self.parquet_filename = self.config.setdefault('parquet_filename', None)
        if self.parquet_filename is None:
            raise ValueError('parquet_filename must be set')
        self.parquet_start_date = self.config.setdefault('parquet_start_date', None)
        if self.parquet_start_date is None:
            raise ValueError('parquet_start_date must be set')

        self.parquet_end_date = self.config.setdefault('parquet_end_date', None)
        if self.parquet_end_date is None:
            raise ValueError('parquet_end_date must be set')

        # Filesystem setup
        self.filesystem_type = self.config.setdefault('filesystem_type', 'file')
        self.filesystem_options = self.config.setdefault('filesystem_options', {})
        self.fs = self.config.setdefault('fs', None)
        if self.fs is None:
            self.fs = fsspec.filesystem(self.filesystem_type, **self.filesystem_options)
        self.config.setdefault('fs', self.fs)
        # Ensure the directory exists
        self.ensure_directory_exists(self.parquet_storage_path)
        super().__init__(**self.config)

    def load(self, **kwargs):
        self.df = super().load(**kwargs)
        return self.df

    def generate_parquet(self, **kwargs) -> None:
        """
        Generate a Parquet file using the configured DataWrapper class.
        """
        params = self._prepare_params(kwargs)
        dw = DataWrapper(self.data_wrapper_class, **params)
        dw.process()

    def __exit__(self, exc_type, exc_value, traceback):
        # Ensure resources are cleaned up
        if self.fs:
            self.fs.close()

    def update_parquet(self, period: str = 'today', **kwargs) -> None:
        """Update the Parquet file with data from a specific period."""

        def itd_config():
            try:
                start_date = kwargs.pop('history_begins_on')
            except KeyError:
                raise ValueError("For period 'itd', you must provide 'history_begins_on' in kwargs.")
            return {'parquet_start_date': start_date, 'parquet_end_date': datetime.date.today().strftime('%Y-%m-%d')}

        def ytd_config():
            return {
                'parquet_start_date': datetime.date(datetime.date.today().year, 1, 1).strftime('%Y-%m-%d'),
                'parquet_end_date': datetime.date.today().strftime('%Y-%m-%d')
            }

        config_map = {
            'itd': itd_config,
            'ytd': ytd_config
        }

        if period in config_map:
            kwargs.update(config_map[period]())
        else:
            kwargs.update(self.parse_parquet_period(period=period))
        self.logger.debug(f"kwargs passed to update parquet: {kwargs}")
        self.generate_parquet(**kwargs)

    def rebuild_parquet(self, **kwargs) -> None:
        """Rebuild the Parquet file from the start to end date."""
        kwargs.update(self._get_rebuild_params(kwargs))
        self.generate_parquet(**kwargs)

    def _get_rebuild_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for rebuilding the Parquet file."""
        return {
            'overwrite': True,
            'reverse_order': True,
            'start_date': kwargs.get('parquet_start_date', self.parquet_start_date),
            'end_date': kwargs.get('parquet_end_date', self.parquet_end_date),
        }

    def _prepare_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the parameters for generating the Parquet file."""
        kwargs = {**self.config, **kwargs}
        return {
            'class_params': kwargs.pop('class_params', None),
            'date_field': kwargs.pop('date_field', self.date_field),
            'data_path': self.parquet_storage_path,
            'parquet_filename': kwargs.pop('parquet_filename', self.parquet_filename),
            'start_date': kwargs.pop('parquet_start_date', self.parquet_start_date),
            'end_date': kwargs.pop('parquet_end_date', self.parquet_end_date),
            'verbose': kwargs.pop('verbose', False),
            'load_params': kwargs.pop('load_params', None),
            'reverse_order': kwargs.pop('reverse_order', True),
            'overwrite': kwargs.pop('overwrite', False),
            'ignore_missing': kwargs.pop('ignore_missing', False),
            'logger': self.logger,
            'history_days_threshold': kwargs.pop('history_days_threshold', 30),
            'max_age_minutes': kwargs.pop('max_age_minutes', 10),
            'show_progress': kwargs.pop('show_progress', False),
            'fs': self.fs,
            'filesystem_type': self.filesystem_type,
            'filesystem_options': self.filesystem_options,
        }

    @staticmethod
    def parse_parquet_period(**kwargs):
        start_date, end_date = DateUtils.parse_period(**kwargs)
        return {
            'parquet_start_date': start_date.strftime('%Y-%m-%d'),
            'parquet_end_date': end_date.strftime('%Y-%m-%d'),
        }

    def ensure_directory_exists(self, path: str) -> None:
        """Ensure the directory exists in the specified filesystem."""
        try:
            self.fs.makedirs(path, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Error creating directory {path} in filesystem {self.filesystem_type}: {e}")
