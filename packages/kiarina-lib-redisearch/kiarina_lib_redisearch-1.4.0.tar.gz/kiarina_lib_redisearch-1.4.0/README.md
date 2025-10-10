# kiarina-lib-redisearch

A comprehensive Python client library for [RediSearch](https://redis.io/docs/interact/search-and-query/) with advanced configuration management, schema definition, and both full-text and vector search capabilities.

## Features

- **Full-Text Search**: Advanced text search with stemming, phonetic matching, and fuzzy search
- **Vector Search**: Similarity search using FLAT and HNSW algorithms with multiple distance metrics
- **Schema Management**: Type-safe schema definition with automatic migration support
- **Configuration Management**: Flexible configuration using `pydantic-settings-manager`
- **Sync & Async**: Support for both synchronous and asynchronous operations
- **Advanced Filtering**: Intuitive query builder with type-safe filter expressions
- **Index Management**: Complete index lifecycle management (create, migrate, reset, drop)
- **Type Safety**: Full type hints and Pydantic validation throughout

## Installation

```bash
pip install kiarina-lib-redisearch
```

## Quick Start

### Basic Usage (Sync)

```python
import redis
from kiarina.lib.redisearch import create_redisearch_client, RedisearchSettings

# Configure your schema
schema = [
    {"type": "tag", "name": "category"},
    {"type": "text", "name": "title"},
    {"type": "numeric", "name": "price", "sortable": True},
    {"type": "vector", "name": "embedding", "algorithm": "FLAT", "dims": 1536}
]

# Create Redis connection (decode_responses=False is required)
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=False)

# Create RediSearch client
client = create_redisearch_client(
    redis=redis_client,
    config_key="default"  # Optional: use specific configuration
)

# Configure settings
from kiarina.lib.redisearch import settings_manager
settings_manager.user_config = {
    "default": {
        "key_prefix": "products:",
        "index_name": "products_index",
        "index_schema": schema
    }
}

# Create index
client.create_index()

# Add documents
client.set({
    "category": "electronics",
    "title": "Wireless Headphones",
    "price": 99.99,
    "embedding": [0.1, 0.2, 0.3, ...]  # 1536-dimensional vector
}, id="product_1")

# Full-text search
results = client.find(
    filter=[["category", "==", "electronics"]],
    return_fields=["title", "price"]
)

# Vector similarity search
results = client.search(
    vector=[0.1, 0.2, 0.3, ...],  # Query vector
    limit=10
)
```

### Async Usage

```python
import redis.asyncio
from kiarina.lib.redisearch.asyncio import create_redisearch_client

async def main():
    # Create async Redis connection
    redis_client = redis.asyncio.Redis(host="localhost", port=6379, decode_responses=False)

    # Create async RediSearch client
    client = create_redisearch_client(redis=redis_client)

    # All operations are awaitable
    await client.create_index()
    await client.set({"title": "Example"}, id="doc_1")
    results = await client.find()
```

## Schema Definition

Define your search schema with type-safe field definitions:

### Field Types

#### Tag Fields
```python
{
    "type": "tag",
    "name": "category",
    "separator": ",",           # Default: ","
    "case_sensitive": False,    # Default: False
    "sortable": True,          # Default: False
    "multiple": True           # Allow multiple tags (library-specific)
}
```

#### Text Fields
```python
{
    "type": "text",
    "name": "description",
    "weight": 2.0,             # Default: 1.0
    "no_stem": False,          # Default: False
    "sortable": True,          # Default: False
    "phonetic_matcher": "dm:en" # Optional phonetic matching
}
```

#### Numeric Fields
```python
{
    "type": "numeric",
    "name": "price",
    "sortable": True,          # Default: False
    "no_index": False          # Default: False
}
```

#### Vector Fields

**FLAT Algorithm (Exact Search)**
```python
{
    "type": "vector",
    "name": "embedding",
    "algorithm": "FLAT",
    "dims": 1536,
    "datatype": "FLOAT32",        # FLOAT32 or FLOAT64
    "distance_metric": "COSINE",  # L2, COSINE, or IP
    "initial_cap": 1000          # Optional initial capacity
}
```

**HNSW Algorithm (Approximate Search)**
```python
{
    "type": "vector",
    "name": "embedding",
    "algorithm": "HNSW",
    "dims": 1536,
    "datatype": "FLOAT32",
    "distance_metric": "COSINE",
    "m": 16,                     # Default: 16
    "ef_construction": 200,      # Default: 200
    "ef_runtime": 10,           # Default: 10
    "epsilon": 0.01             # Default: 0.01
}
```

## Configuration

This library uses [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) for flexible configuration management.

### Environment Variables

```bash
# Basic settings
export KIARINA_LIB_REDISEARCH_KEY_PREFIX="myapp:"
export KIARINA_LIB_REDISEARCH_INDEX_NAME="main_index"
export KIARINA_LIB_REDISEARCH_PROTECT_INDEX_DELETION="true"
```

### Programmatic Configuration

```python
from kiarina.lib.redisearch import settings_manager

# Configure multiple environments
settings_manager.user_config = {
    "development": {
        "key_prefix": "dev:",
        "index_name": "dev_index",
        "index_schema": dev_schema,
        "protect_index_deletion": False
    },
    "production": {
        "key_prefix": "prod:",
        "index_name": "prod_index",
        "index_schema": prod_schema,
        "protect_index_deletion": True
    }
}

# Switch configurations
settings_manager.active_key = "production"
```

## Advanced Filtering

Use the intuitive filter API to build complex queries:

### Filter API

```python
import kiarina.lib.redisearch.filter as rf

# Tag filters
filter1 = rf.Tag("category") == "electronics"
filter2 = rf.Tag("tags") == ["new", "featured"]  # Multiple tags
filter3 = rf.Tag("brand") != "apple"

# Numeric filters
filter4 = rf.Numeric("price") > 100
filter5 = rf.Numeric("rating") >= 4.5
filter6 = rf.Numeric("stock") <= 10

# Text filters
filter7 = rf.Text("title") == "exact match"
filter8 = rf.Text("description") % "*wireless*"  # Wildcard search
filter9 = rf.Text("content") % "%%fuzzy%%"       # Fuzzy search

# Combine filters
complex_filter = (
    (rf.Tag("category") == "electronics") &
    (rf.Numeric("price") < 500) &
    (rf.Text("title") % "*headphone*")
)

# Use in searches
results = client.find(filter=complex_filter)
```

### Condition Lists

Alternatively, use simple condition lists:

```python
# Equivalent to the complex filter above
conditions = [
    ["category", "==", "electronics"],
    ["price", "<", 500],
    ["title", "like", "*headphone*"]
]

results = client.find(filter=conditions)
```

## Search Operations

The library provides three main search operations: `count`, `find`, and `search`. These are the core functions for querying your indexed data.

### 1. Count Documents (`count`)

Count the number of documents matching specific criteria without retrieving the actual documents. This is efficient for getting result counts.

```python
# Count all documents
total = client.count()
print(f"Total documents: {total.total}")

# Count with filters
electronics_count = client.count(
    filter=[["category", "==", "electronics"]]
)
print(f"Electronics products: {electronics_count.total}")

# Complex filter counting
expensive_electronics = client.count(
    filter=[
        ["category", "==", "electronics"],
        ["price", ">", 500]
    ]
)
print(f"Expensive electronics: {expensive_electronics.total}")

# Using filter API
import kiarina.lib.redisearch.filter as rf
filter_expr = (rf.Tag("category") == "electronics") & (rf.Numeric("price") > 500)
count_result = client.count(filter=filter_expr)
```

**Count Result Structure:**
```python
class SearchResult:
    total: int        # Number of matching documents
    duration: float   # Query execution time in milliseconds
    documents: list   # Empty for count operations
```

### 2. Full-Text Search (`find`)

Search and retrieve documents based on filters, with support for sorting, pagination, and field selection.

#### Basic Find Operations

```python
# Find all documents
results = client.find()
print(f"Found {results.total} documents")

# Find with specific fields returned
results = client.find(
    return_fields=["title", "price", "category"]
)
for doc in results.documents:
    print(f"ID: {doc.id}")
    print(f"Title: {doc.mapping['title']}")
    print(f"Price: {doc.mapping['price']}")
```

#### Filtering

```python
# Single filter condition
results = client.find(
    filter=[["category", "==", "electronics"]]
)

# Multiple filter conditions (AND logic)
results = client.find(
    filter=[
        ["category", "==", "electronics"],
        ["price", ">=", 100],
        ["price", "<=", 500]
    ]
)

# Using filter expressions for complex logic
import kiarina.lib.redisearch.filter as rf
complex_filter = (
    (rf.Tag("category") == "electronics") |
    (rf.Tag("category") == "computers")
) & (rf.Numeric("price") < 1000)

results = client.find(filter=complex_filter)
```

#### Sorting

```python
# Sort by price (ascending)
results = client.find(
    sort_by="price",
    sort_desc=False
)

# Sort by rating (descending)
results = client.find(
    filter=[["category", "==", "electronics"]],
    sort_by="rating",
    sort_desc=True
)

# Note: Only sortable fields can be used for sorting
# Define sortable fields in your schema:
# {"type": "numeric", "name": "price", "sortable": True}
```

#### Pagination

```python
# Get first 10 results
results = client.find(limit=10)

# Get next 10 results (pagination)
results = client.find(offset=10, limit=10)

# Get results 21-30
results = client.find(offset=20, limit=10)

# Combine with filtering and sorting
results = client.find(
    filter=[["category", "==", "electronics"]],
    sort_by="price",
    sort_desc=True,
    offset=0,
    limit=20
)
```

#### Field Selection

```python
# Return only specific fields (more efficient)
results = client.find(
    return_fields=["title", "price"]
)

# Return no content, only document IDs (most efficient for counting)
results = client.find(
    return_fields=[]  # or omit return_fields parameter
)

# Include computed fields
results = client.find(
    return_fields=["title", "price", "id"]  # id is automatically computed
)
```

#### Complete Find Example

```python
# Comprehensive search with all options
results = client.find(
    filter=[
        ["category", "in", ["electronics", "computers"]],
        ["price", ">=", 50],
        ["rating", ">=", 4.0]
    ],
    sort_by="price",
    sort_desc=False,
    offset=0,
    limit=25,
    return_fields=["title", "price", "rating", "category"]
)

print(f"Found {results.total} products (showing {len(results.documents)})")
print(f"Query took {results.duration}ms")

for doc in results.documents:
    print(f"- {doc.mapping['title']}: ${doc.mapping['price']} ({doc.mapping['rating']}⭐)")
```

### 3. Vector Similarity Search (`search`)

Perform semantic similarity search using vector embeddings. This is ideal for AI-powered search, recommendation systems, and semantic matching.

#### Basic Vector Search

```python
# Simple vector search
query_vector = [0.1, 0.2, 0.3, ...]  # Your query embedding (must match schema dims)
results = client.search(vector=query_vector)

print(f"Found {results.total} similar documents")
for doc in results.documents:
    print(f"Document: {doc.id}, Similarity Score: {doc.score:.4f}")
```

#### Vector Search with Filtering

```python
# Pre-filter documents before vector search (more efficient)
results = client.search(
    vector=query_vector,
    filter=[["category", "==", "electronics"]],  # Only search within electronics
    limit=10
)

# Complex pre-filtering
results = client.search(
    vector=query_vector,
    filter=[
        ["category", "in", ["electronics", "computers"]],
        ["price", "<=", 1000],
        ["in_stock", "==", "true"]
    ],
    limit=20
)
```

#### Pagination and Field Selection

```python
# Paginated vector search
results = client.search(
    vector=query_vector,
    offset=10,
    limit=10,
    return_fields=["title", "description", "price", "distance"]
)

# Get similarity scores and distances
for doc in results.documents:
    distance = doc.mapping.get('distance', 0)
    score = doc.score  # Normalized similarity score (0-1)
    print(f"{doc.mapping['title']}: score={score:.4f}, distance={distance:.4f}")
```

#### Understanding Vector Search Results

```python
results = client.search(
    vector=query_vector,
    limit=5,
    return_fields=["title", "distance"]
)

for i, doc in enumerate(results.documents, 1):
    print(f"{i}. {doc.mapping['title']}")
    print(f"   Similarity Score: {doc.score:.4f}")  # Higher = more similar
    print(f"   Distance: {doc.mapping['distance']:.4f}")  # Lower = more similar
    print(f"   Document ID: {doc.id}")
    print()
```

#### Vector Search Best Practices

```python
# 1. Use appropriate vector dimensions
schema = [{
    "type": "vector",
    "name": "embedding",
    "algorithm": "HNSW",  # or "FLAT"
    "dims": 1536,  # Must match your embedding model
    "distance_metric": "COSINE"  # COSINE, L2, or IP
}]

# 2. Pre-filter for better performance
results = client.search(
    vector=query_vector,
    filter=[["category", "==", "target_category"]],  # Reduce search space
    limit=50  # Don't retrieve more than needed
)

# 3. Use HNSW for large datasets
hnsw_schema = {
    "type": "vector",
    "name": "embedding",
    "algorithm": "HNSW",
    "dims": 1536,
    "m": 16,              # Connections per node
    "ef_construction": 200, # Build-time accuracy
    "ef_runtime": 100      # Search-time accuracy
}

# 4. Use FLAT for smaller datasets or exact search
flat_schema = {
    "type": "vector",
    "name": "embedding",
    "algorithm": "FLAT",
    "dims": 1536
}
```

### Search Result Structure

All search operations return a `SearchResult` object:

```python
class SearchResult:
    total: int                    # Total matching documents
    duration: float              # Query execution time (ms)
    documents: list[Document]    # Retrieved documents

class Document:
    key: str                     # Redis key
    id: str                      # Document ID
    score: float                 # Relevance/similarity score (-1.0 to 1.0)*
    mapping: dict[str, Any]      # Document fields
```

### Performance Comparison

| Operation | Use Case | Performance | Returns |
|-----------|----------|-------------|---------|
| `count()` | Get result counts | Fastest | Count only |
| `find()` | Full-text search, filtering | Fast | Full documents |
| `search()` | Semantic similarity | Moderate* | Ranked by similarity |

*Vector search performance depends on algorithm (FLAT vs HNSW) and dataset size.

### Combining Operations

```python
# 1. First, check how many results we'll get
count_result = client.count(
    filter=[["category", "==", "electronics"]]
)
print(f"Will search through {count_result.total} electronics")

# 2. If reasonable number, do full-text search
if count_result.total < 10000:
    text_results = client.find(
        filter=[["category", "==", "electronics"]],
        sort_by="rating",
        sort_desc=True,
        limit=100
    )

# 3. For semantic search within results
if query_vector:
    semantic_results = client.search(
        vector=query_vector,
        filter=[["category", "==", "electronics"]],
        limit=20
    )
```

## Index Management

### Index Lifecycle

```python
# Check if index exists
if not client.exists_index():
    client.create_index()

# Get index information
info = client.get_info()
print(f"Index: {info.index_name}, Documents: {info.num_docs}")

# Reset index (delete all documents, recreate index)
client.reset_index()

# Drop index (optionally delete documents)
client.drop_index(delete_documents=True)
```

### Schema Migration

Automatically migrate your index when schema changes:

```python
# Update your schema
new_schema = [
    {"type": "tag", "name": "category"},
    {"type": "text", "name": "title"},
    {"type": "numeric", "name": "price", "sortable": True},
    {"type": "numeric", "name": "rating", "sortable": True},  # New field
    {"type": "vector", "name": "embedding", "algorithm": "HNSW", "dims": 1536}  # Changed algorithm
]

# Update configuration
settings_manager.user_config["production"]["index_schema"] = new_schema

# Migrate (automatically detects changes and recreates index)
client.migrate_index()
```

## Document Operations

### Adding Documents

```python
# Add single document
client.set({
    "category": "electronics",
    "title": "Wireless Mouse",
    "price": 29.99,
    "rating": 4.5,
    "embedding": [0.1, 0.2, ...]
}, id="mouse_001")

# Add document with ID in mapping
client.set({
    "id": "keyboard_001",
    "category": "electronics",
    "title": "Mechanical Keyboard",
    "price": 129.99,
    "embedding": [0.2, 0.3, ...]
})
```

### Retrieving Documents

```python
# Get single document
doc = client.get("mouse_001")
if doc:
    print(f"Title: {doc.mapping['title']}")
    print(f"Price: {doc.mapping['price']}")

# Get Redis key for document
key = client.get_key("mouse_001")  # Returns "products:mouse_001"
```

### Deleting Documents

```python
# Delete single document
client.delete("mouse_001")
```

## Integration with Other Libraries

### Using with kiarina-lib-redis

```python
from kiarina.lib.redis import get_redis
from kiarina.lib.redisearch import create_redisearch_client

# Get Redis client from kiarina-lib-redis
redis_client = get_redis(decode_responses=False)

# Create RediSearch client
search_client = create_redisearch_client(redis=redis_client)
```

### Custom Redis Configuration

```python
import redis
from kiarina.lib.redisearch import create_redisearch_client

# Custom Redis client with connection pooling
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=False,  # Required!
    max_connections=20,
    socket_timeout=30,
    socket_connect_timeout=10
)

search_client = create_redisearch_client(redis=redis_client)
```

## Error Handling

```python
try:
    client.create_index()
except Exception as e:
    if "Index already exists" in str(e):
        print("Index already exists, continuing...")
    else:
        raise

# Protect against accidental index deletion
settings_manager.user_config["production"]["protect_index_deletion"] = True

# This will return False instead of deleting
success = client.drop_index()
if not success:
    print("Index deletion is protected")
```

## Performance Considerations

### Vector Search Optimization

```python
# Use HNSW for large datasets (faster but approximate)
hnsw_schema = {
    "type": "vector",
    "name": "embedding",
    "algorithm": "HNSW",
    "dims": 1536,
    "m": 32,              # Higher M = better recall, more memory
    "ef_construction": 400, # Higher = better index quality, slower indexing
    "ef_runtime": 100      # Higher = better recall, slower search
}

# Use FLAT for smaller datasets or exact search
flat_schema = {
    "type": "vector",
    "name": "embedding",
    "algorithm": "FLAT",
    "dims": 1536,
    "initial_cap": 10000  # Pre-allocate capacity
}
```

### Indexing Best Practices

```python
# Use appropriate field options
schema = [
    {
        "type": "tag",
        "name": "category",
        "sortable": True,     # Only if you need sorting
        "no_index": False     # Set True for storage-only fields
    },
    {
        "type": "text",
        "name": "description",
        "weight": 1.0,        # Adjust relevance weight
        "no_stem": False      # Enable stemming for better search
    }
]
```

## Development

### Prerequisites

- Python 3.12+
- Redis with RediSearch module
- Docker (for running Redis in tests)

### Setup

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment
mise run setup

# Start Redis with RediSearch for testing
docker compose up -d redis
```

### Running Tests

```bash
# Run all tests for this package
mise run package kiarina-lib-redisearch

# Run specific test categories
uv run --group test pytest packages/kiarina-lib-redisearch/tests/sync/
uv run --group test pytest packages/kiarina-lib-redisearch/tests/async/

# Run with coverage
mise run package:test kiarina-lib-redisearch --coverage
```

## Configuration Reference

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `key_prefix` | `KIARINA_LIB_REDISEARCH_KEY_PREFIX` | `""` | Redis key prefix for documents |
| `index_name` | `KIARINA_LIB_REDISEARCH_INDEX_NAME` | `"default"` | RediSearch index name |
| `index_schema` | - | `None` | Index schema definition (list of field dicts) |
| `protect_index_deletion` | `KIARINA_LIB_REDISEARCH_PROTECT_INDEX_DELETION` | `false` | Prevent accidental index deletion |

## Dependencies

- [redis](https://github.com/redis/redis-py) - Redis client for Python
- [numpy](https://numpy.org/) - Numerical computing (for vector operations)
- [pydantic](https://docs.pydantic.dev/) - Data validation and settings management
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Advanced settings management

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Contributing

This is a personal project, but contributions are welcome! Please feel free to submit issues or pull requests.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - The main monorepo containing this package
- [RediSearch](https://redis.io/docs/interact/search-and-query/) - The search and query engine this library connects to
- [kiarina-lib-redis](../kiarina-lib-redis/) - Redis client library for basic Redis operations
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Configuration management library used by this package
