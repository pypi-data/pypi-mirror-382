# kiarina-lib-falkordb

A Python client library for [FalkorDB](https://falkordb.com/) with configuration management and connection pooling.

## Features

- **Configuration Management**: Use `pydantic-settings-manager` for flexible configuration
- **Connection Pooling**: Automatic connection caching and reuse
- **Retry Support**: Built-in retry mechanism for connection failures
- **Sync & Async**: Support for both synchronous and asynchronous operations
- **Type Safety**: Full type hints and Pydantic validation

## Installation

```bash
pip install kiarina-lib-falkordb
```

## Quick Start

### Basic Usage (Sync)

```python
from kiarina.lib.falkordb import get_falkordb

# Get a FalkorDB client with default settings
db = get_falkordb()

# Select a graph and run a query
graph = db.select_graph("social")
result = graph.query("CREATE (p:Person {name: 'Alice', age: 30}) RETURN p")
print(result.result_set)
```

### Async Usage

```python
from kiarina.lib.falkordb.asyncio import get_falkordb

async def main():
    # Get an async FalkorDB client
    db = get_falkordb()

    # Select a graph and run a query
    graph = db.select_graph("social")
    result = await graph.query("CREATE (p:Person {name: 'Bob', age: 25}) RETURN p")
    print(result.result_set)
```

## Configuration

This library uses [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) for flexible configuration management.

### Environment Variables

Configure the FalkorDB connection using environment variables:

```bash
# FalkorDB connection URL
export KIARINA_LIB_FALKORDB_URL="falkor://localhost:6379"

# Enable retry mechanism
export KIARINA_LIB_FALKORDB_USE_RETRY="true"

# Timeout settings
export KIARINA_LIB_FALKORDB_SOCKET_TIMEOUT="6.0"
export KIARINA_LIB_FALKORDB_SOCKET_CONNECT_TIMEOUT="3.0"

# Retry settings
export KIARINA_LIB_FALKORDB_RETRY_ATTEMPTS="3"
export KIARINA_LIB_FALKORDB_RETRY_DELAY="1.0"
```

### Programmatic Configuration

```python
from kiarina.lib.falkordb import settings_manager

# Configure for multiple environments
settings_manager.user_config = {
    "development": {
        "url": "falkor://localhost:6379",
        "use_retry": True,
        "retry_attempts": 3
    },
    "production": {
        "url": "falkor://prod-server:6379",
        "use_retry": True,
        "retry_attempts": 5,
        "socket_timeout": 10.0
    }
}

# Switch to production configuration
settings_manager.active_key = "production"
db = get_falkordb()
```

### Runtime Overrides

```python
from kiarina.lib.falkordb import get_falkordb

# Override settings at runtime
db = get_falkordb(
    url="falkor://custom-server:6379",
    use_retry=True
)
```

## Advanced Usage

### Connection Caching

```python
from kiarina.lib.falkordb import get_falkordb

# These will return the same cached connection
db1 = get_falkordb()
db2 = get_falkordb()
assert db1 is db2

# Use different cache keys for separate connections
db3 = get_falkordb(cache_key="secondary")
assert db1 is not db3
```

### Custom Configuration Keys

```python
from kiarina.lib.falkordb import settings_manager, get_falkordb

# Configure multiple named configurations
settings_manager.user_config = {
    "analytics": {
        "url": "falkor://analytics-db:6379",
        "socket_timeout": 30.0
    },
    "cache": {
        "url": "falkor://cache-db:6379",
        "socket_timeout": 5.0
    }
}

# Use specific configurations
analytics_db = get_falkordb("analytics")
cache_db = get_falkordb("cache")
```

### Error Handling and Retries

```python
from kiarina.lib.falkordb import get_falkordb

# Enable automatic retries for connection issues
db = get_falkordb(use_retry=True)

try:
    graph = db.select_graph("mydata")
    result = graph.query("MATCH (n) RETURN count(n)")
except Exception as e:
    print(f"Query failed: {e}")
```

## Configuration Reference

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `url` | `KIARINA_LIB_FALKORDB_URL` | `"falkor://localhost:6379"` | FalkorDB connection URL |
| `use_retry` | `KIARINA_LIB_FALKORDB_USE_RETRY` | `false` | Enable automatic retries |
| `socket_timeout` | `KIARINA_LIB_FALKORDB_SOCKET_TIMEOUT` | `6.0` | Socket timeout in seconds |
| `socket_connect_timeout` | `KIARINA_LIB_FALKORDB_SOCKET_CONNECT_TIMEOUT` | `3.0` | Connection timeout in seconds |
| `health_check_interval` | `KIARINA_LIB_FALKORDB_HEALTH_CHECK_INTERVAL` | `60` | Health check interval in seconds |
| `retry_attempts` | `KIARINA_LIB_FALKORDB_RETRY_ATTEMPTS` | `3` | Number of retry attempts |
| `retry_delay` | `KIARINA_LIB_FALKORDB_RETRY_DELAY` | `1.0` | Delay between retries in seconds |

## URL Formats

FalkorDB URLs support the following formats:

- `falkor://localhost:6379` - Basic connection
- `falkor://username:password@localhost:6379` - With authentication
- `falkors://localhost:6379` - SSL/TLS connection
- `falkors://username:password@localhost:6379` - SSL/TLS with authentication

## Development

### Prerequisites

- Python 3.12+
- Docker (for running FalkorDB in tests)

### Setup

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment (installs tools, syncs dependencies, downloads test data)
mise run setup

# Start FalkorDB for testing
docker compose up -d falkordb
```

### Running Tests

```bash
# Run format, lint, type checks and tests
mise run package kiarina-lib-falkordb

# Coverage report
mise run package:test kiarina-lib-falkordb --coverage

# Run specific tests
uv run --group test pytest packages/kiarina-lib-falkordb/tests/test_sync.py
uv run --group test pytest packages/kiarina-lib-falkordb/tests/test_async.py
```

## Dependencies

- [falkordb](https://github.com/kiarina/falkordb-py) - FalkorDB Python client (fork with redis-py 6.x support and async bug fixes)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Advanced settings management
- [redis](https://github.com/redis/redis-py) - Redis client (FalkorDB is Redis-compatible)

### Note on FalkorDB Client

This library uses a [fork of the official FalkorDB Python client](https://github.com/kiarina/falkordb-py) instead of the [upstream version](https://github.com/FalkorDB/falkordb-py). The fork includes:

- **Redis-py 6.x compatibility**: Support for redis-py 6.4.0+ (upstream only supports 5.x)
- **Async client bug fixes**: Fixes for issues in the asynchronous client implementation
- **Enhanced stability**: Additional improvements for production use

The fork is based on the upstream `develop` branch and will be synchronized with upstream changes. Once these improvements are merged upstream, this library will migrate back to the official client.

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Contributing

This is a personal project, but contributions are welcome! Please feel free to submit issues or pull requests.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - The main monorepo containing this package
- [FalkorDB](https://www.falkordb.com/) - The graph database this library connects to
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Configuration management library used by this package
