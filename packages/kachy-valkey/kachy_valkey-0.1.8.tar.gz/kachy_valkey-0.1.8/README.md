# Kachy Valkey Python Client

High-performance Valkey client with automatic authentication and multi-tenancy support for Python.

## Installation

```bash
pip install kachy-valkey
```

## Quick Start

```python
import os
import kachy

# Initialize with your access key
kachy.init(os.environ.get("KACHY_ACCESS_KEY"))

# Basic operations
kachy.set("greeting", "Hello, World!")
kachy.set("user:123:name", "John Doe")
kachy.set("session:abc", "active", 3600)  # 1 hour expiration

# Retrieve values
greeting = kachy.get("greeting")
user_name = kachy.get("user:123:name")
session = kachy.get("session:abc")

print(f"Greeting: {greeting}")
print(f"User name: {user_name}")
print(f"Session: {session}")

# Check if keys exist
exists_greeting = kachy.exists("greeting")
print(f"Greeting exists: {exists_greeting}")

# Get TTL
ttl = kachy.ttl("session:abc")
print(f"Session TTL: {ttl} seconds")

# Cleanup
kachy.delete("greeting")
kachy.delete("user:123:name")
kachy.delete("session:abc")

# Close connection
kachy.close()
```

## Advanced Operations

### Custom Valkey Commands

```python
# Hash operations
kachy.valkey("HMSET", "user:123:profile", "age", "30", "city", "New York")
profile = kachy.valkey("HMGET", "user:123:profile", "age", "city")
print(f"User profile: {profile}")

# List operations
kachy.valkey("LPUSH", "notifications:123", "Welcome message")
kachy.valkey("LPUSH", "notifications:123", "System update")
notifications = kachy.valkey("LRANGE", "notifications:123", 0, -1)
print(f"Notifications: {notifications}")
```

### Pipeline Operations

```python
# Batch operations for better performance
with kachy.pipeline() as pipe:
    pipe.set("batch:1", "value1")
    pipe.set("batch:2", "value2")
    pipe.set("batch:3", "value3")
    results = pipe.execute()

print(f"Pipeline results: {results}")
```

## Configuration

Configure the client using environment variables:

- `KACHY_ACCESS_KEY`: Your authentication access key (required)
- `KACHY_BASE_URL`: API base URL (default: https://api.klache.net)
- `KACHY_TIMEOUT`: Request timeout in seconds (default: 30)
- `KACHY_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `KACHY_RETRY_DELAY`: Delay between retries in seconds (default: 1.0)
- `KACHY_POOL_SIZE`: Connection pool size (default: 10)

## API Reference

| Operation | Method | Description |
|-----------|--------|-------------|
| `set` | `kachy.set(key, value, ex?)` | Set key-value pair with optional expiration |
| `get` | `kachy.get(key)` | Get value by key |
| `delete` | `kachy.delete(key)` | Delete a key |
| `exists` | `kachy.exists(key)` | Check if key exists |
| `expire` | `kachy.expire(key, seconds)` | Set expiration for key |
| `ttl` | `kachy.ttl(key)` | Get time to live for key |
| `valkey` | `kachy.valkey(command, *args)` | Execute any Valkey command |
| `pipeline` | `kachy.pipeline()` | Create pipeline for batch operations |

## Requirements

- Python 3.7+
- requests >= 2.25.0

## Development

```bash
# Clone the repository
git clone https://github.com/Klug-Labs/kachy-valkey-python.git
cd kachy-valkey-python

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://docs.klache.net
- **API Status**: https://status.klache.net
- **Support Email**: support@klache.net