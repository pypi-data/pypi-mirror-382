# WowMySQL Python SDK

Official Python client library for WowMySQL REST API v2.

## Installation

```bash
pip install wowmysql-sdk
```

## Quick Start

```python
from wowmysql import WowMySQLClient

# Initialize client
client = WowMySQLClient(
    project_url="myproject",  # Your project subdomain
    api_key="your_api_key_here"
)

# Query data
users = client.table("users") \
    .select(["id", "name", "email"]) \
    .filter({"column": "age", "operator": "gt", "value": 18}) \
    .order("created_at", "desc") \
    .limit(10) \
    .get()

print(users["data"])
```

## Features

✅ **Fully Typed** - Complete type hints for IDE support  
✅ **Fluent API** - Chainable query builder  
✅ **RESTful** - Uses standard HTTP methods  
✅ **Error Handling** - Descriptive error messages  
✅ **Context Manager** - Automatic resource cleanup  

## Usage

### Initialize Client

```python
# Option 1: With just project slug (recommended)
client = WowMySQLClient(
    project_url="myproject",  # Just the subdomain
    api_key="your_api_key"
)

# Option 2: With full URL
client = WowMySQLClient(
    project_url="https://myproject.wowmysql.com/api",
    api_key="your_api_key"
)

# Option 3: Development mode with SSL verification disabled
client = WowMySQLClient(
    project_url="myproject",
    api_key="your_api_key",
    verify_ssl=False  # Only for development/testing
)

# Option 4: Custom domain
client = WowMySQLClient(
    project_url="myproject",
    api_key="your_api_key",
    base_domain="yourdomain.com"  # For self-hosted instances
)

# Using context manager (recommended)
with WowMySQLClient(project_url="myproject", api_key="key") as client:
    users = client.table("users").get()
```

### Query Records

```python
# Get all records
result = client.table("users").get()

# With filters
adults = client.table("users") \
    .filter({"column": "age", "operator": "gte", "value": 18}) \
    .get()

# Select specific columns
names = client.table("users") \
    .select(["id", "name"]) \
    .get()

# Multiple filters
active = client.table("users") \
    .filter({"column": "status", "operator": "eq", "value": "active"}) \
    .filter({"column": "age", "operator": "gt", "value": 18}) \
    .order("created_at", "desc") \
    .limit(20) \
    .get()

# Get first record
user = client.table("users") \
    .filter({"column": "email", "operator": "eq", "value": "john@example.com"}) \
    .first()
```

### Filter Operators

- `eq` - Equals
- `neq` - Not equals
- `gt` - Greater than
- `gte` - Greater than or equal
- `lt` - Less than
- `lte` - Less than or equal
- `like` - Pattern matching
- `is` - IS NULL / IS NOT NULL

### Get Record by ID

```python
user = client.table("users").get_by_id(123)
```

### Create Record

```python
result = client.table("users").create({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

print(f"Created user with ID: {result['id']}")
```

### Update Record

```python
client.table("users").update(123, {
    "email": "newemail@example.com"
})
```

### Delete Record

```python
client.table("users").delete(123)
```

### List Tables

```python
tables = client.list_tables()
print("Available tables:", tables)
```

### Get Table Schema

```python
schema = client.get_table_schema("users")
print("Columns:", schema["columns"])
print("Primary key:", schema["primary_key"])
```

## Type Hints

The SDK includes full type hints for better IDE support:

```python
from wowmysql import WowMySQLClient, QueryResponse
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    email: str
    age: int

client = WowMySQLClient(project_url="myproject", api_key="key")
users: QueryResponse = client.table("users").get()

for user in users["data"]:
    print(user["name"])
```

## Error Handling

```python
from wowmysql import WowMySQLError

try:
    user = client.table("users").get_by_id(999)
except WowMySQLError as e:
    print(f"Status: {e.status_code}")
    print(f"Message: {e}")
    print(f"Response: {e.response}")
```

## Advanced Examples

### Pagination

```python
page = 1
page_size = 20

result = client.table("users") \
    .limit(page_size) \
    .offset((page - 1) * page_size) \
    .get()

print(f"Showing {result['count']} of {result['total']} records")
```

### Complex Queries

```python
result = client.table("orders") \
    .select(["id", "user_id", "total", "status"]) \
    .filter({"column": "status", "operator": "eq", "value": "completed"}) \
    .filter({"column": "total", "operator": "gte", "value": 100}) \
    .order("created_at", "desc") \
    .limit(50) \
    .get()
```

### Batch Operations

```python
with WowMySQLClient(project_url="myproject", api_key="key") as client:
    users_table = client.table("users")
    
    # Create multiple records
    new_users = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
    ]
    
    for user_data in new_users:
        result = users_table.create(user_data)
        print(f"Created user: {result['id']}")
```

## Troubleshooting

### SSL Certificate Verification Failed

If you encounter SSL certificate errors like:
```
ssl.SSLCertVerificationError: certificate verify failed: Hostname mismatch
```

**Temporary workaround** (development only):
```python
client = WowMySQLClient(
    project_url="myproject",
    api_key="your_api_key",
    verify_ssl=False  # Disable SSL verification
)
```

**Production solution**: Ensure your server has a proper wildcard SSL certificate configured for `*.wowmysql.com`. See [WILDCARD_SSL_SETUP_GUIDE.md](../../WILDCARD_SSL_SETUP_GUIDE.md) in the main repository.

### Connection Timeout

```python
# Increase timeout
client = WowMySQLClient(
    project_url="myproject",
    api_key="your_api_key",
    timeout=60  # 60 seconds
)
```

### Custom Domain Setup

If you're self-hosting on a custom domain:
```python
client = WowMySQLClient(
    project_url="myproject",
    api_key="your_api_key",
    base_domain="yourcompany.com"  # Will use myproject.yourcompany.com
)
```

## Requirements

- Python 3.8+
- requests >= 2.31.0
- typing-extensions >= 4.0.0

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/wowmysql

# Format code
black src/
```

## Support

- **Documentation**: https://docs.wowmysql.com
- **Issues**: https://github.com/wowmysql/wowmysql/issues
- **Email**: support@wowmysql.com

## License

MIT © WowMySQL Team
