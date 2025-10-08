# MangledDLT - Local Databricks Development Bridge

MangledDLT enables developers to write and test Databricks code locally by intercepting Spark operations and fetching data from remote Unity Catalog environments. Write your PySpark code once and run it anywhere - locally or on Databricks - without changes.

## Features

- **Transparent Spark Interception**: Automatically intercepts `spark.read.table()` and `spark.readStream.table()` calls
- **Unity Catalog Integration**: Fetches data directly from remote Unity Catalog tables
- **Smart Caching**: LRU cache with TTL for improved development performance
- **Multiple Auth Methods**: Supports PAT, OAuth, and Service Principal authentication
- **Zero Code Changes**: Same code works locally and on Databricks
- **Connection Pooling**: Efficient connection management for better performance
- **Error Recovery**: Automatic retry with exponential backoff

## Installation

```bash
pip install MangledDlt
```

Or with all dependencies:

```bash
pip install MangledDlt[all]
```

## Quick Start

```python
from pyspark.sql import SparkSession
from mangledlt import MangledDLT

# Create Spark session as usual
spark = SparkSession.builder \
    .appName("LocalDev") \
    .getOrCreate()

# Enable MangledDLT
mdlt = MangledDLT()
mdlt.enable()

# Now you can read from Unity Catalog!
df = spark.read.table("main.default.customers")
df.show()

# When done, disable interception
mdlt.disable()
```

## Configuration

### Using Environment Variables

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
export DATABRICKS_WAREHOUSE_ID="your-warehouse-id"
```

### Using Databricks CLI Config

```bash
# Configure Databricks CLI
databricks configure --token

# MangledDLT will automatically use your configuration
```

### Using Custom Config

```python
from mangledlt import MangledDLT

config = {
    "host": "https://workspace.cloud.databricks.com",
    "token": "your-token",
    "warehouse_id": "warehouse-id",
    "cache_enabled": True,
    "cache_ttl": 600  # 10 minutes
}

mdlt = MangledDLT(config=config)
mdlt.enable()
```

## Development vs Production

```python
from pyspark.sql import SparkSession
from mangledlt import MangledDLT

spark = SparkSession.builder.appName("MyApp").getOrCreate()

# Auto-detect environment
if not spark.conf.get("spark.databricks.service.clusterId"):
    # Running locally - enable MangledDLT
    mdlt = MangledDLT()
    mdlt.enable()
    print("Running locally with MangledDLT")
else:
    print("Running on Databricks")

# Your code works the same in both environments
customers = spark.read.table("catalog.schema.customers")
orders = spark.read.table("catalog.schema.orders")
result = customers.join(orders, "customer_id")
result.show()
```

## Caching

MangledDLT includes intelligent caching to speed up iterative development:

```python
mdlt = MangledDLT(config={
    "cache_enabled": True,
    "cache_ttl": 1800,  # 30 minutes
    "cache_max_size": 100  # Max 100 cached queries
})
mdlt.enable()

# First read - fetches from Unity Catalog
df1 = spark.read.table("catalog.schema.large_table")  # Takes 5 seconds

# Subsequent reads - served from cache
df2 = spark.read.table("catalog.schema.large_table")  # Takes <100ms

# Check cache statistics
stats = mdlt.get_cache_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Hit rate: {stats['hit_rate']}%")

# Clear cache when needed
mdlt.clear_cache()
```

## Error Handling

```python
from mangledlt import MangledDLT
from mangledlt.exceptions import AuthError, TableNotFoundError

try:
    mdlt = MangledDLT()
    mdlt.enable()

    df = spark.read.table("catalog.schema.table")
    df.show()

except AuthError as e:
    print(f"Authentication failed: {e}")
    print("Please check your Databricks credentials")

except TableNotFoundError as e:
    print(f"Table not found: {e}")
    print("Please verify the table exists and you have access")
```

## Multiple Workspaces

```python
from mangledlt import MangledDLT
from mangledlt.config import Config

# Connect to development workspace
dev_config = Config.from_file(profile="DEV")
dev_mdlt = MangledDLT(config=dev_config)
dev_mdlt.enable()

# Read from dev
dev_data = spark.read.table("dev_catalog.schema.table")

# Switch to production
dev_mdlt.disable()
prod_config = Config.from_file(profile="PROD")
prod_mdlt = MangledDLT(config=prod_config)
prod_mdlt.enable()

# Read from production
prod_data = spark.read.table("prod_catalog.schema.table")
```

## API Reference

### MangledDLT

Main class for enabling local Databricks development.

- `__init__(config=None)`: Initialize with optional configuration
- `enable()`: Enable Spark operation interception
- `disable()`: Disable interception
- `get_status()`: Get connection status
- `clear_cache()`: Clear query cache
- `get_cache_stats()`: Get cache statistics

### Config

Configuration management class.

- `from_file(path, profile)`: Load from Databricks CLI config
- `from_env()`: Load from environment variables
- `validate()`: Validate configuration

### Exceptions

- `ConfigError`: Configuration issues
- `AuthError`: Authentication failures
- `ConnectionError`: Connection problems
- `TableNotFoundError`: Table doesn't exist
- `PermissionError`: Insufficient permissions
- `InvalidReferenceError`: Invalid table reference format

## Requirements

- Python 3.9+
- PySpark 3.4+ (user must install separately)
- databricks-sql-connector 2.9+

## Development

```bash
# Clone the repository
git clone https://github.com/mangledlt/mangledlt.git
cd mangledlt

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Support

- Issues: https://github.com/mangledlt/mangledlt/issues
- Discussions: https://github.com/mangledlt/mangledlt/discussions
- Documentation: https://github.com/mangledlt/mangledlt/docs