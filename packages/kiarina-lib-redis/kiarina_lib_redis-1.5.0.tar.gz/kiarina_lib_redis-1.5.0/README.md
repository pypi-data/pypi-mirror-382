# kiarina-lib-redis

A Python client library for [Redis](https://redis.io/) with configuration management and connection pooling.

## Features

- **Configuration Management**: Use `pydantic-settings-manager` for flexible configuration
- **Connection Pooling**: Automatic connection caching and reuse
- **Retry Support**: Built-in retry mechanism for connection failures
- **Sync & Async**: Support for both synchronous and asynchronous operations
- **Type Safety**: Full type hints and Pydantic validation

## Installation

```bash
pip install kiarina-lib-redis
```

## Quick Start

### Basic Usage (Sync)

```python
from kiarina.lib.redis import get_redis

# Get a Redis client with default settings
redis = get_redis()

# Basic operations
redis.set("key", "value")
value = redis.get("key")
print(value)  # b'value'

# With decode_responses=True for string values
redis = get_redis(decode_responses=True)
redis.set("key", "value")
value = redis.get("key")
print(value)  # 'value'
```

### Async Usage

```python
from kiarina.lib.redis.asyncio import get_redis

async def main():
    # Get an async Redis client
    redis = get_redis(decode_responses=True)

    # Basic operations
    await redis.set("key", "value")
    value = await redis.get("key")
    print(value)  # 'value'
```

## Configuration

This library uses [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) for flexible configuration management.

### Environment Variables

Configure the Redis connection using environment variables:

```bash
# Redis connection URL
export KIARINA_LIB_REDIS_URL="redis://localhost:6379"

# Enable retry mechanism
export KIARINA_LIB_REDIS_USE_RETRY="true"

# Timeout settings
export KIARINA_LIB_REDIS_SOCKET_TIMEOUT="6.0"
export KIARINA_LIB_REDIS_SOCKET_CONNECT_TIMEOUT="3.0"

# Retry settings
export KIARINA_LIB_REDIS_RETRY_ATTEMPTS="3"
export KIARINA_LIB_REDIS_RETRY_DELAY="1.0"
```

### Programmatic Configuration

```python
from kiarina.lib.redis import settings_manager

# Configure for multiple environments
settings_manager.user_config = {
    "development": {
        "url": "redis://localhost:6379",
        "use_retry": True,
        "retry_attempts": 3
    },
    "production": {
        "url": "redis://prod-server:6379",
        "use_retry": True,
        "retry_attempts": 5,
        "socket_timeout": 10.0
    }
}

# Switch to production configuration
settings_manager.active_key = "production"
redis = get_redis()
```

### Runtime Overrides

```python
from kiarina.lib.redis import get_redis

# Override settings at runtime
redis = get_redis(
    url="redis://custom-server:6379",
    use_retry=True,
    decode_responses=True
)
```

## Advanced Usage

### Connection Caching

```python
from kiarina.lib.redis import get_redis

# These will return the same cached connection
redis1 = get_redis()
redis2 = get_redis()
assert redis1 is redis2

# Use different cache keys for separate connections
redis3 = get_redis(cache_key="secondary")
assert redis1 is not redis3
```

### Custom Configuration Keys

```python
from kiarina.lib.redis import settings_manager, get_redis

# Configure multiple named configurations
settings_manager.user_config = {
    "cache": {
        "url": "redis://cache-db:6379",
        "socket_timeout": 5.0
    },
    "session": {
        "url": "redis://session-db:6379",
        "socket_timeout": 10.0
    }
}

# Use specific configurations
cache_redis = get_redis("cache")
session_redis = get_redis("session")
```

### Error Handling and Retries

```python
from kiarina.lib.redis import get_redis
import redis

# Enable automatic retries for connection issues
redis_client = get_redis(use_retry=True)

try:
    redis_client.set("key", "value")
    value = redis_client.get("key")
except redis.ConnectionError as e:
    print(f"Connection failed: {e}")
except redis.TimeoutError as e:
    print(f"Operation timed out: {e}")
```

## Configuration Reference

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `url` | `KIARINA_LIB_REDIS_URL` | `"redis://localhost:6379"` | Redis connection URL |
| `use_retry` | `KIARINA_LIB_REDIS_USE_RETRY` | `false` | Enable automatic retries |
| `socket_timeout` | `KIARINA_LIB_REDIS_SOCKET_TIMEOUT` | `6.0` | Socket timeout in seconds |
| `socket_connect_timeout` | `KIARINA_LIB_REDIS_SOCKET_CONNECT_TIMEOUT` | `3.0` | Connection timeout in seconds |
| `health_check_interval` | `KIARINA_LIB_REDIS_HEALTH_CHECK_INTERVAL` | `60` | Health check interval in seconds |
| `retry_attempts` | `KIARINA_LIB_REDIS_RETRY_ATTEMPTS` | `3` | Number of retry attempts |
| `retry_delay` | `KIARINA_LIB_REDIS_RETRY_DELAY` | `1.0` | Delay between retries in seconds |

## URL Formats

Redis URLs support the following formats:

- `redis://localhost:6379` - Basic connection
- `redis://username:password@localhost:6379` - With authentication
- `rediss://localhost:6379` - SSL/TLS connection
- `rediss://username:password@localhost:6379` - SSL/TLS with authentication
- `redis://localhost:6379/0` - Specify database number
- `unix:///path/to/socket.sock` - Unix socket connection

## Development

### Prerequisites

- Python 3.12+
- Docker (for running Redis in tests)

### Setup

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment (installs tools, syncs dependencies, downloads test data)
mise run setup

# Start Redis for testing
docker compose up -d redis
```

### Running Tests

```bash
# Run format, lint, type checks and tests
mise run package kiarina-lib-redis

# Coverage report
mise run package:test kiarina-lib-redis --coverage

# Run specific tests
uv run --group test pytest packages/kiarina-lib-redis/tests/test_sync.py
uv run --group test pytest packages/kiarina-lib-redis/tests/test_async.py
```

## Dependencies

- [redis](https://github.com/redis/redis-py) - Redis client for Python
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Advanced settings management

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Contributing

This is a personal project, but contributions are welcome! Please feel free to submit issues or pull requests.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - The main monorepo containing this package
- [Redis](https://redis.io/) - The in-memory data structure store this library connects to
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Configuration management library used by this package
