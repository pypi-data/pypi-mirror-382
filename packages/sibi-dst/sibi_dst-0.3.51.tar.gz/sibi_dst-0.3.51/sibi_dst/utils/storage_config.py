from .storage_manager import StorageManager
from .credentials import ConfigManager

class StorageConfig:
    def __init__(self, config:ConfigManager, depots:dict=None):
        self.conf = config
        self.depots = depots
        self._initialize_storage()
        self.storage_manager = StorageManager(self.base_storage, self.filesystem_type, self.filesystem_options)
        if self.depots is not None:
            self.depot_paths, self.depot_names = self.storage_manager.rebuild_depot_paths(depots)
        else:
            self.depot_paths = None
            self.depot_names = None

    def _initialize_storage(self):
        self.filesystem_type = self.conf.get('fs_type','file')
        self.base_storage = self.conf.get('fs_path', "local_storage/")
        if self.filesystem_type == "file":
            self.filesystem_options ={}
        elif self.filesystem_type == "s3":
            self.filesystem_options = {
                "key": self.conf.get('fs_key',''),
                "secret": self.conf.get('fs_secret'),
                "token": self.conf.get('fs_token'),
                "skip_instance_cache":True,
                "use_listings_cache": False,
                "client_kwargs": {
                    "endpoint_url": self.conf.get('fs_endpoint')
                }
            }
        elif self.filesystem_type == "webdav":
            verify_ssl = self.conf.get('fs_verify_ssl', True)
            # Convert string 'false' to boolean False
            if isinstance(verify_ssl, str) and verify_ssl.lower() == 'false':
                verify_ssl = False
            self.filesystem_options = {
                "base_url": self.conf.get('fs_endpoint', ''),
                "username": self.conf.get('fs_key', ''),
                "password": self.conf.get('fs_secret', ''),
                "token": self.conf.get('fs_token', ''),
                "verify": verify_ssl
            }
        else:
            # unsupported filesystem type
            # defaulting to local filesystem
            self.filesystem_type = 'file'
            self.filesystem_options = {}
        self.filesystem_options = {k: v for k, v in self.filesystem_options.items() if v}