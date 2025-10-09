# sibi-dst

Data Science Toolkit
---------------------
Data Science Toolkit built with Python, Pandas, Dask, OpenStreetMaps, Scikit-Learn, XGBOOST, Django ORM, SQLAlchemy, DjangoRestFramework, FastAPI

Major Functionality
--------------------
1) **Build DataCubes, DataSets, and DataObjects** from diverse data sources, including **relational databases, Parquet files, Excel (`.xlsx`), delimited tables (`.csv`, `.tsv`), JSON, and RESTful APIs (`JSON API REST`)**.
2) **Comprehensive DataFrame Management** utilities for efficient data handling, transformation, and optimization using **Pandas** and **Dask**.
3) **Flexible Data Sharing** with client applications by writing to **Data Warehouses, local filesystems, and cloud storage platforms** such as **Amazon S3, Google Cloud Storage (GCS), and Azure Blob Storage**.
4) **Microservices for Data Access** – Build scalable **API-driven services** using **RESTful APIs (`Django REST Framework`, `FastAPI`) and gRPC** for high-performance data exchange.

Supported Technologies
--------------------
- **Data Processing**: Pandas, Dask
- **Machine Learning**: Scikit-Learn, XGBoost
- **Databases & Storage**: SQLAlchemy, Django ORM, Parquet, Amazon S3, GCS, Azure Blob Storage
- **Mapping & Geospatial Analysis**: OpenStreetMaps, OSMnx, Geopy
- **API Development**: Django REST Framework, gRPC, FastAPI

Installation
---------------------
```bash
pip install sibi-dst
```

Usage
---------------------
### Loading Data from SQLAlchemy
```python
from sibi_dst.df_helper import DfHelper
from conf.transforms.fields.crm import customer_fields
from conf.credentials import replica_db_conf
from conf.storage import get_fs_instance

config = {
    'backend': 'sqlalchemy',
    'connection_url': replica_db_conf.get('db_url'),
    'table': 'crm_clientes_archivo',
    'field_map': customer_fields,
    'legacy_filters': True,
    'fs': get_fs_instance()
}

df_helper = DfHelper(**config)
result = df_helper.load(id__gte=1)
```

### Saving Data to ClickHouse
```python
clk_creds = {
    'host': '192.168.3.171',
    'port': 18123,
    'user': 'username',
    'database': 'xxxxxxx',
    'table': 'customer_file',
    'order_by': 'id'
}

df_helper.save_to_clickhouse(**clk_creds)
```

### Saving Data to Parquet
```python
df_helper.save_to_parquet(
    parquet_filename='filename.parquet',
    parquet_storage_path='/path/to/my/files/'
)
```

Backends Supported
---------------------
| Backend       | Description |
|--------------|-------------|
| `sqlalchemy` | Load data from SQL databases using SQLAlchemy. |
| `django_db`  | Load data from Django ORM models. |
| `parquet`    | Load and save data from Parquet files. |
| `http`       | Fetch data from HTTP endpoints. |
| `osmnx`      | Geospatial mapping and routing using OpenStreetMap. |
| `geopy`      | Geolocation services for address lookup and reverse geocoding. |

Geospatial Utilities
---------------------
### **OSMnx Helper (`sibi_dst.osmnx_helper`)
**
Provides **OpenStreetMap-based mapping utilities** using `osmnx` and `folium`.

#### 🔹 Key Features
- **BaseOsmMap**: Manages interactive Folium-based maps.
- **PBFHandler**: Loads `.pbf` (Protocolbuffer Binary Format) files for network graphs.

#### Example: Generating an OSM Map
```python
from sibi_dst.osmnx_helper import BaseOsmMap
osm_map = BaseOsmMap(osmnx_graph=my_graph, df=my_dataframe)
osm_map.generate_map()
```

### **Geopy Helper (`sibi_dst.geopy_helper`)
**
Provides **geolocation services** using `Geopy` for forward and reverse geocoding.

#### 🔹 Key Features
- **GeolocationService**: Interfaces with `Nominatim` API for geocoding.
- **Error Handling**: Manages `GeocoderTimedOut` and `GeocoderServiceError` gracefully.
- **Singleton Geolocator**: Efficiently reuses a global geolocator instance.

#### Example: Reverse Geocoding
```python
from sibi_dst.geopy_helper import GeolocationService
gs = GeolocationService()
location = gs.reverse((9.935,-84.091))
print(location)
```

Advanced Features
---------------------
### Querying with Custom Filters
Filters can be applied dynamically using Django-style syntax:
```python
result = df_helper.load(date__gte='2023-01-01', status='active')
```

### Parallel Processing
Leverage Dask for parallel execution:
```python
result = df_helper.load_parallel(status='active')
```

Testing
---------------------
To run unit tests, use:
```bash
pytest tests/
```

Contributing
---------------------
Contributions are welcome! Please submit pull requests or open issues for discussions.

License
---------------------
sibi-dst is licensed under the MIT License.

