# Infino Python SDK

Python SDK for interacting with Infino's API, providing AWS SigV4 authenticated access to search, analytics, and AI capabilities.

## Installation

```bash
pip install infino-sdk
```

## Quick Start

```python
from infino_sdk.lib import InfinoSDK
import asyncio

async def main():
    # Create SDK instance with your credentials
    async with InfinoSDK(
        access_key="your_access_key",
        secret_key="your_secret_key",
        endpoint="http://localhost:9200"
    ) as sdk:
        # Check connection
        info = await sdk.ping()
        print(f"Connected to: {info}")

        # Create an index
        await sdk.create_index("my_index")

        # Search documents
        query = '{"query": {"match_all": {}}}'
        results = await sdk.search("my_index", query)
        print(f"Search results: {results}")

# Run the async function
asyncio.run(main())
```

## Usage Examples

### Basic Operations

```python
from infino_sdk.lib import InfinoSDK

async with InfinoSDK(access_key, secret_key, endpoint) as sdk:
    # Index operations
    await sdk.create_index("products")
    await sdk.delete_index("old_products")
    indices = await sdk.get_cat_indices()

    # Document operations
    doc = await sdk.get_document("products", "doc_id")
    source = await sdk.get_source("products", "doc_id")

    # Search operations
    results = await sdk.search("products", '{"query": {"term": {"category": "electronics"}}}')
    ai_results = await sdk.search_ai("products", "find all smartphones")

    # SQL queries
    sql_results = await sdk.sql("SELECT * FROM products WHERE price > 100")

    # Bulk operations
    bulk_data = '{"index": {"_id": "1"}}\n{"name": "Product 1"}\n'
    await sdk.bulk_ingest("products", bulk_data)
```

### WebSocket Connections

```python
async with InfinoSDK(access_key, secret_key, endpoint) as sdk:
    # Connect to WebSocket endpoint with automatic SigV4 authentication
    ws = await sdk.websocket_connect("/_conversation/ws")

    try:
        # Send message
        await ws.send('{"type": "message", "content": "Hello"}')

        # Receive response
        response = await ws.recv()
        print(f"Received: {response}")
    finally:
        await ws.close()
```

### Security Operations

```python
async with InfinoSDK(access_key, secret_key, endpoint) as sdk:
    # User management
    user_config = {
        "password": "strong_password",
        "backend_roles": ["admin"]
    }
    await sdk.create_user("new_user", user_config)
    users = await sdk.list_users()

    # Role management
    role_config = {
        "cluster_permissions": ["indices:admin/*"],
        "index_permissions": [{
            "index_patterns": ["*"],
            "allowed_actions": ["read", "write"]
        }]
    }
    await sdk.create_role("custom_role", role_config)

    # Role mapping
    mapping_config = {
        "users": ["new_user"],
        "backend_roles": ["custom_role"]
    }
    await sdk.create_role_mapping("my_mapping", mapping_config)
```

### ML Commons Operations

```python
async with InfinoSDK(access_key, secret_key, endpoint) as sdk:
    # Register a model
    model_config = {
        "name": "my_model",
        "version": "1.0",
        "model_type": "text_embedding"
    }
    result = await sdk.register_model(model_config)
    model_id = result["model_id"]

    # Deploy the model
    await sdk.deploy_model(model_id)

    # Make predictions
    input_data = {"text": "Sample text for embedding"}
    prediction = await sdk.predict(model_id, input_data)

    # Undeploy when done
    await sdk.undeploy_model(model_id)
```

### Account Management

```python
async with InfinoSDK(access_key, secret_key, endpoint) as sdk:
    # Create a new account (no authentication required)
    account_data = {
        "public": "account_name",
        "private": "account_password"
    }
    new_account = await sdk.create_account(account_data)
    account_id = new_account["account_id"]

    # Get account information
    account_info = await sdk.get_account(account_id)

    # Rotate API keys
    new_keys = await sdk.rotate_api_keys("username")
    print(f"New access key: {new_keys['access_key']}")

    # Delete account
    await sdk.delete_account(account_id)
```

### Manual Session Management

If you need more control over the session lifecycle:

```python
from infino_sdk.lib import InfinoSDK

# Create SDK instance
sdk = InfinoSDK(access_key, secret_key, endpoint)

# Initialize session manually
await sdk._ensure_session()

try:
    # Use SDK methods
    await sdk.ping()
    results = await sdk.search("my_index", query)
finally:
    # Always close the session when done
    await sdk.close()
```

## API Reference

### Core Methods

- `ping()` - Test connection to the Infino endpoint
- `close()` - Close the underlying HTTP session

### Index Operations

- `create_index(index_name)` - Create a new index
- `create_index_with_mapping(index_name, mapping)` - Create index with custom mapping
- `delete_index(index_name)` - Delete an index
- `get_index(index_name)` - Get index information
- `get_cat_indices()` - List all indices

### Document Operations

- `get_document(index, doc_id)` - Retrieve a document
- `get_source(index, doc_id)` - Get document source
- `document_exists(index, doc_id)` - Check if document exists
- `delete_by_query(index, query)` - Delete documents matching query

### Search Operations

- `search(index, query)` - Execute a search query
- `search_ai(index, query_text)` - AI-powered natural language search
- `msearch(queries)` - Multi-search across indices
- `sql(query)` - Execute SQL query
- `count(index, query)` - Count matching documents

### Bulk Operations

- `bulk_ingest(index, payload)` - Bulk index documents (NDJSON format)
- `metrics(index, payload)` - Ingest metrics data

### WebSocket

- `websocket_connect(path, headers=None)` - Connect to WebSocket with SigV4 auth

### Security APIs

- `create_user()`, `get_user()`, `update_user()`, `delete_user()`, `list_users()`
- `create_role()`, `get_role()`, `update_role()`, `delete_role()`, `list_roles()`
- `create_role_mapping()`, `get_role_mapping()`, `update_role_mapping()`, `delete_role_mapping()`
- `rotate_api_keys(username)` - Rotate user API keys

## Authentication

The SDK uses AWS SigV4 authentication. All requests are automatically signed with your access key and secret key. For WebSocket connections, authentication is provided via query parameters.

## Error Handling

```python
from infino_sdk.lib import InfinoError

try:
    await sdk.get_document("index", "missing_doc")
except InfinoError as e:
    if e.status_code() == 404:
        print("Document not found")
    else:
        print(f"Error: {e.message}")
```

## Requirements

- Python 3.7+
- requests
- websockets
- backoff

## License

See LICENSE file in the repository root.

## Development & Publishing

### Setup Development Environment
```bash
pip install -e .[dev]
```

### Pre-Publication Checklist

Before publishing to PyPI, ensure:

- [ ] Version number updated in `pyproject.toml` and `__init__.py`
- [ ] CHANGELOG.md updated with release notes
- [ ] README.md reviewed and accurate
- [ ] LICENSE file present in package root
- [ ] Dependencies verified and correct
- [ ] Build succeeds: `python -m build`
- [ ] Package installable locally: `pip install dist/*.whl`
- [ ] Import works: `python -c "from infino_sdk import InfinoSDK; print('OK')"`
- [ ] `twine check dist/*` passes without warnings

### Publishing Workflow

#### 1. Test with TestPyPI

Build the package:
```bash
cd sdk/python
python -m build
```

Check the distribution:
```bash
twine check dist/*
```

Upload to TestPyPI:
```bash
twine upload --repository testpypi dist/*
```

Test installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps infino-sdk
python -c "from infino_sdk import InfinoSDK; print('Success!')"
```

#### 2. Publish to PyPI

Once tested on TestPyPI, publish to production PyPI:

```bash
twine upload dist/*
```

Verify installation:
```bash
pip install infino-sdk
```

### Notes

- Package name on PyPI: `infino-sdk` (kebab-case)
- Import name in Python: `infino_sdk` (snake_case)
- Always test on TestPyPI before production PyPI