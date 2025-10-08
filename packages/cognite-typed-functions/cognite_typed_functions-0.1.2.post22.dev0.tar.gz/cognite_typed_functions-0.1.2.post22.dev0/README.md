# Cognite Typed Functions

A FastAPI-style framework for building type-safe Cognite Functions with automatic OpenAPI schema generation, request validation, and comprehensive error handling.

## Why Typed Cognite Functions?

Standard [Cognite Functions](https://docs.cognite.com/cdf/functions/) require a simple `handle(client, data)` function, which can become unwieldy for complex APIs. Our framework enhances Cognite Functions with modern web API development practices:

### 🎯 **FastAPI-Style Developer Experience**

**Standard Cognite Function:**

```python
def handle(client, data):
    try:
        asset_no = int(data["assetNo"])  # Manual validation
        include_tax = data.get("includeTax", "false").lower() == "true"  # Manual parsing
        # Handle routing manually based on data
        if data.get("action") == "get_item":
            # Implementation here
        elif data.get("action") == "create_item":
            # Different implementation
    except Exception as e:
        return {"error": str(e)}  # Basic error handling
```

**Our Framework:**

```python
@app.get("/items/{item_id}")
def get_item(client: CogniteClient, item_id: int, include_tax: bool = False) -> ItemResponse:
    """Retrieve an item by ID"""
    # Type validation and coercion handled automatically
    # Clear function signature with proper types
    # Automatic error handling and response formatting
```

### 🚀 **Key Improvements**

- **Function introspection** - Solve the "black box" problem where customers forget how to call their deployed functions
- **Multiple endpoints in one function** - Instead of one function per endpoint
- **Async/await support** - Write efficient concurrent code with native async handlers
- **Recursive type validation** - Automatic conversion of complex nested data structures (dict[str, BaseModel], Optional[Union[...]], etc.)
- **Built-in API documentation** - OpenAPI schema generation with introspection endpoints
- **AI-friendly interfaces** - Machine-readable function signatures enable AI code generation
- **Structured error handling** - Consistent error responses with detailed information
- **Modern Python syntax** - Python 3.10+ features: union types (`x | None`), match statements, and builtin generics

## Features

- 🚀 **FastAPI-style decorators** - Use familiar `@app.get()`, `@app.post()`, etc. decorators
- ⚡ **Async/await support** - Write both sync and async handlers seamlessly for concurrent operations
- 📝 **Recursive type validation** - Deep conversion of nested data structures with Pydantic models
- 📊 **OpenAPI schema generation** - Auto-generated API documentation
- 🔍 **Introspection endpoints** - Built-in `/__schema__`, `/__routes__`, and `/__health__` endpoints
- 🛡️ **Comprehensive error handling** - Structured error responses with detailed information
- 📋 **Enterprise logging** - Isolated logger with dependency injection that works across all cloud providers
- 🎯 **Path parameters** - Support for dynamic URL parameters like `/items/{item_id}`
- 🔧 **Advanced type coercion** - Recursive conversion supporting nested BaseModels, Optional types, and Union types
- 📦 **Modular architecture** - Clean separation of concerns across multiple modules
- ✅ **Full Cognite Functions compatibility** - Works with scheduling, secrets, and all deployment methods

## Quick Start

### Installation

**Requirements:**

- Python 3.10 or higher
- uv (recommended) or pip

```bash
# Install the package (when published)
# pip install cognite-typed-functions

# For development:
# Clone this repository and install dependencies
uv sync
```

### Basic Usage

```python
# No typing imports needed - using builtin generic types
from cognite.client import CogniteClient
from pydantic import BaseModel

from cognite_typed_functions import CogniteApp, create_function_handle

# Create your app
app = CogniteApp(title="My API", version="1.0.0")

# Define your models
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ItemResponse(BaseModel):
    id: int
    item: Item
    total_price: float

# Define your endpoints
@app.get("/items/{item_id}")
def get_item(
    client: CogniteClient,
    item_id: int,
    include_tax: bool = False
) -> ItemResponse:
    """Retrieve an item by ID"""
    item = Item(
        name=f"Item {item_id}",
        price=100.0,
        tax=10.0 if include_tax else None
    )
    total = item.price + (item.tax or 0)
    return ItemResponse(id=item_id, item=item, total_price=total)

@app.post("/items/")
def create_item(client: CogniteClient, item: Item) -> ItemResponse:
    """Create a new item"""
    new_id = 12345  # Your creation logic here
    total = item.price + (item.tax or 0)
    return ItemResponse(id=new_id, item=item, total_price=total)

@app.post("/process/batch")
def process_batch(client: CogniteClient, items: list[Item]) -> dict:
    """Process multiple items in batch"""
    total_value = sum(item.price + (item.tax or 0) for item in items)
    return {"processed_count": len(items), "total_value": total_value}

# Export the handler for Cognite Functions
handle = create_function_handle(app)
```

## MCP Integration

The framework includes built-in **Model Context Protocol (MCP)** support, enabling AI assistants to discover and use your Cognite Functions as tools.

### Using the MCP Integration

```python
from cognite_typed_functions import CogniteApp, create_function_handle
from cognite_typed_functions.mcp import create_mcp_server
from cognite_typed_functions.introspection import create_introspection_app

# Create your main business app
app = CogniteApp(title="Asset Management API", version="1.0.0")

# Define your business endpoints
@app.get("/items/{item_id}")
def get_item(client: CogniteClient, item_id: int) -> ItemResponse:
    """Retrieve an item by ID"""
    # Your implementation here

# Create MCP server from your app
mcp = create_mcp_server(app, "asset-management-tools")

# Use @mcp.tool() decorator to expose specific routes to AI
@mcp.tool()
@app.get("/items/{item_id}")  # This decorator makes the endpoint available to AI
def get_item_for_ai(client: CogniteClient, item_id: int) -> ItemResponse:
    """AI-accessible version of get_item"""
    return get_item(client, item_id)

# Create introspection app for debugging and monitoring
introspection = create_introspection_app()

# Compose all apps: MCP -> Introspection -> Main Business App
handle = create_function_handle(mcp, introspection, app)
```

This composition provides:

- **AI Integration**: `/__mcp_tools__` and `/__mcp_call__/*` endpoints
- **Human Debugging**: `/__schema__`, `/__routes__`, `/__health__` endpoints
- **Business Logic**: Your custom endpoints like `/items/{item_id}`
- **Unified Metadata**: All introspection shows "Asset Management API" as the main app

### MCP Features

- **Selective exposure**: Use `@mcp.tool()` to choose which endpoints are accessible to AI
- **Automatic schema generation**: AI gets JSON schemas for all parameters and responses
- **Built-in validation**: Input validation happens automatically
- **Tool discovery**: AI can discover available tools via `/__mcp_tools__` endpoint
- **Tool execution**: AI can call tools via `/__mcp_call__/{tool_name}` endpoints

### Built-in MCP Endpoints

- `/__mcp_tools__` - List all available MCP tools with schemas
- `/__mcp_call__/{tool_name}` - Execute a specific MCP tool

## Async Support

The framework fully supports both **synchronous** and **asynchronous** route handlers. This enables developers to write efficient concurrent code when needed, while maintaining simplicity for straightforward operations.

### Why Use Async?

Async handlers are particularly useful for:

- **Concurrent API calls** - Fetch data from multiple sources simultaneously
- **I/O-bound operations** - Database queries, file operations, network requests
- **Parallel processing** - Process multiple items concurrently
- **External service integration** - Call multiple external APIs in parallel

### Basic Async Usage

Simply declare your route handler as `async def` instead of `def`:

```python
import asyncio
from cognite_typed_functions import CogniteApp

app = CogniteApp(title="Async API", version="1.0.0")

# Synchronous handler (traditional)
@app.get("/items/{item_id}")
def get_item(client: CogniteClient, item_id: int) -> ItemResponse:
    """Synchronous data retrieval"""
    # Your sync logic here
    return ItemResponse(...)

# Asynchronous handler (new!)
@app.get("/items/{item_id}/async")
async def get_item_async(client: CogniteClient, item_id: int) -> ItemResponse:
    """Asynchronous data retrieval with concurrent operations"""
    # Use await for async operations
    result = await fetch_data_async(item_id)
    return ItemResponse(...)
```

### Concurrent Operations Example

The real power of async comes from running multiple operations concurrently:

```python
@app.get("/items/{item_id}/details")
async def get_item_with_details(client: CogniteClient, item_id: int) -> dict:
    """Fetch item data from multiple sources concurrently"""

    # Define async operations
    async def fetch_item_info():
        # Simulate API call
        await asyncio.sleep(0.1)
        return {"name": f"Item {item_id}", "price": 100.0}

    async def fetch_inventory():
        # Simulate another API call
        await asyncio.sleep(0.1)
        return {"stock": 50, "warehouse": "A"}

    async def fetch_reviews():
        # Simulate yet another API call
        await asyncio.sleep(0.1)
        return {"rating": 4.5, "count": 120}

    # Execute all operations concurrently (not sequentially!)
    item_info, inventory, reviews = await asyncio.gather(
        fetch_item_info(),
        fetch_inventory(),
        fetch_reviews()
    )

    return {
        "item": item_info,
        "inventory": inventory,
        "reviews": reviews
    }
```

### Batch Processing with Async

Process multiple items concurrently for better performance:

```python
@app.post("/process/batch/async")
async def process_batch_async(client: CogniteClient, items: list[Item]) -> dict:
    """Process multiple items concurrently"""

    async def process_item(item: Item) -> dict:
        """Process a single item asynchronously"""
        # Simulate async processing (e.g., API call, database query)
        await asyncio.sleep(0.01)
        total = item.price + (item.tax or 0)
        return {"name": item.name, "total": total}

    # Process all items concurrently
    results = await asyncio.gather(*[process_item(item) for item in items])

    total_value = sum(result["total"] for result in results)
    return {
        "processed_count": len(items),
        "total_value": total_value,
        "items": results
    }
```

### How It Works

The framework automatically detects whether your handler is sync or async:

- **Async handlers** (`async def`) are awaited directly for native async execution
- **Sync handlers** (`def`) are run on a thread pool to avoid blocking the event loop
- **MCP tools** support both sync and async handlers seamlessly
- **App composition** works with any mix of sync and async handlers

### Performance Considerations

**When async helps:**

- Multiple I/O operations that can run in parallel
- External API calls that can be concurrent
- Database queries that can be batched

**When sync is fine:**

- Simple CPU-bound calculations
- Single database/API call
- Straightforward data transformations

**Note:** Since Cognite Functions don't handle concurrent requests within the same process (each function call gets its own compute instance), async is primarily beneficial for **concurrent operations within a single request**, not for handling multiple requests simultaneously.

### Mixing Sync and Async

You can freely mix sync and async handlers in the same app:

```python
app = CogniteApp(title="Mixed API", version="1.0.0")

@app.get("/simple")
def simple_endpoint(client: CogniteClient) -> dict:
    """Simple sync endpoint"""
    return {"status": "ok"}

@app.get("/complex")
async def complex_endpoint(client: CogniteClient) -> dict:
    """Complex async endpoint with concurrent operations"""
    results = await asyncio.gather(
        fetch_data_1(),
        fetch_data_2(),
        fetch_data_3()
    )
    return {"results": results}

# Both work seamlessly in the same app!
handle = create_function_handle(app)
```

## Logging

The framework provides an enterprise-grade logging solution that works across all cloud providers (AWS Lambda, Azure Functions, GCP Cloud Run) through dependency injection.

### Why Use the Framework Logger?

According to the [Cognite Functions documentation](https://docs.cognite.com/cdf/functions/), the standard Python `logging` module is not recommended because it can interfere with the cloud provider's logging infrastructure. Instead, they recommend using `print()` statements.

Our framework solves this problem by providing an **isolated logger** that:

- ✅ Uses Python's standard `logging` module with familiar API (`logger.info()`, `logger.warning()`, etc.)
- ✅ Writes directly to stdout (captured by all cloud providers)
- ✅ Is completely isolated from other loggers (won't interfere with wrapper code)
- ✅ Supports log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Can be dependency-injected just like `client` and `secrets`
- ✅ Works with both sync and async handlers

### Basic Usage

Simply add `logger: logging.Logger` to your function signature:

```python
import logging
from cognite.client import CogniteClient
from cognite_typed_functions import CogniteApp

app = CogniteApp(title="My API", version="1.0.0")

@app.get("/items/{item_id}")
def get_item(client: CogniteClient, logger: logging.Logger, item_id: int) -> dict:
    """Retrieve an item with logging"""
    logger.info(f"Fetching item {item_id}")
    
    # Your logic here
    item = fetch_item(item_id)
    
    logger.debug(f"Item details: {item}")
    return {"id": item_id, "name": item.name}
```

### Log Levels

The logger supports all standard Python log levels:

```python
@app.post("/process/data")
def process_data(client: CogniteClient, logger: logging.Logger, data: dict) -> dict:
    """Process data with different log levels"""
    
    logger.debug("Detailed debug information")      # DEBUG: Detailed diagnostic info
    logger.info("Processing started")               # INFO: General informational messages
    logger.warning("Unexpected value encountered")  # WARNING: Warning messages
    logger.error("Processing failed")               # ERROR: Error messages
    logger.critical("System failure")               # CRITICAL: Critical errors
    
    return {"status": "processed"}
```

By default, the logger is configured at **INFO** level, meaning `DEBUG` messages won't appear in logs. You can see INFO, WARNING, ERROR, and CRITICAL messages.

### Async Handlers with Logger

The logger works seamlessly with async handlers:

```python
@app.post("/process/batch")
async def process_batch(
    client: CogniteClient,
    logger: logging.Logger,
    items: list[Item]
) -> dict:
    """Process multiple items with logging"""
    logger.info(f"Starting batch processing of {len(items)} items")
    
    async def process_item(item: Item) -> dict:
        # Logger is available in nested functions too
        logger.debug(f"Processing item: {item.name}")
        result = await process_async(item)
        return result
    
    results = await asyncio.gather(*[process_item(item) for item in items])
    
    logger.info(f"Batch processing complete. Processed {len(results)} items")
    return {"processed_count": len(results), "results": results}
```

### Logger Isolation

The framework logger is completely isolated from other logging systems:

- **Named logger**: Uses `"cognite_typed_functions.user"` namespace
- **No propagation**: `propagate=False` prevents interference with parent loggers
- **Separate handlers**: Has its own stdout handler, doesn't affect other loggers
- **Safe to use**: Won't interfere with wrapper code or cloud provider logging

This means you can safely use the logger without worrying about breaking the cloud provider's logging infrastructure or affecting other parts of the system.

### Dependency Injection

The logger is automatically injected when you declare it in your function signature:

```python
# Logger is optional - only injected if you declare it
@app.get("/no-logging")
def no_logging(client: CogniteClient) -> dict:
    """Handler without logging"""
    return {"status": "ok"}

@app.get("/with-logging")
def with_logging(client: CogniteClient, logger: logging.Logger) -> dict:
    """Handler with logging"""
    logger.info("This handler uses logging")
    return {"status": "ok"}

# You can mix logger with other dependencies
@app.get("/all-dependencies")
def all_dependencies(
    client: CogniteClient,
    logger: logging.Logger,
    secrets: dict[str, str],
    function_call_info: dict
) -> dict:
    """Handler with all available dependencies"""
    logger.info(f"Called by function {function_call_info['function_id']}")
    return {"status": "ok"}
```

### Advanced: Custom Logger Configuration

If you need custom logger configuration (e.g., different log level), you can create your own logger:

```python
from cognite_typed_functions import create_function_logger
import logging

# Create logger with DEBUG level
debug_logger = create_function_logger(logging.DEBUG)

# Use it in your handlers
@app.get("/debug-endpoint")
def debug_endpoint(client: CogniteClient, logger: logging.Logger) -> dict:
    """This will use the default INFO logger"""
    logger.debug("This won't appear")  # DEBUG messages filtered out
    logger.info("This will appear")
    return {"status": "ok"}
```

**Note:** The injected logger uses the default INFO level. For custom log levels, you would need to configure the logger before creating the function handle.

### Best Practices

1. **Use appropriate log levels**:
   - `DEBUG`: Detailed diagnostic information (usually filtered out in production)
   - `INFO`: General informational messages about normal operation
   - `WARNING`: Warning messages for unexpected but recoverable situations
   - `ERROR`: Error messages for failures that affect specific operations
   - `CRITICAL`: Critical errors that may cause the entire function to fail

2. **Don't log sensitive information**:

   ```python
   # ❌ Bad - logs sensitive data
   logger.info(f"User credentials: {username}:{password}")
   
   # ✅ Good - logs non-sensitive information
   logger.info(f"User {username} authenticated successfully")
   ```

3. **Use structured logging for complex data**:

   ```python
   # ✅ Good - structured information
   logger.info(f"Processed {count} items in {duration:.2f}s")
   logger.debug(f"Item details: {item.model_dump()}")
   ```

4. **Log at appropriate points**:

   ```python
   @app.post("/process")
   def process(client: CogniteClient, logger: logging.Logger, data: dict) -> dict:
       logger.info("Processing started")  # Entry point
       
       try:
           result = complex_operation(data)
           logger.info("Processing completed successfully")  # Success
           return result
       except Exception as e:
           logger.error(f"Processing failed: {e}")  # Errors
           raise
   ```

## API Reference

### CogniteApp

The main application class that provides FastAPI-style decorators.

```python
app = CogniteApp(title="My API", version="1.0.0")
```

#### Decorators

- `@app.get(path)` - Handle GET requests (data retrieval)
- `@app.post(path)` - Handle POST requests (create resources). Also to handle generic operations that don't fit REST semantics (batch processing, calculations, transformations)
- `@app.put(path)` - Handle PUT requests (update/replace resources)
- `@app.delete(path)` - Handle DELETE requests (remove resources)

#### When to Use Each Decorator

**Use `@app.get()`** for:

- Retrieving data: `@app.get("/assets/{asset_id}")`
- Listing resources: `@app.get("/assets")`
- Health checks: `@app.get("/health")`

**Use `@app.post()`** for:

- Creating new resources: `@app.post("/assets")`
- Uploading data: `@app.post("/files/upload")`
- Batch processing: `@app.post("/process/batch")`
- Complex calculations: `@app.post("/calculate/metrics")`
- Data transformations: `@app.post("/transform/timeseries")`
- Operations that don't fit CRUD patterns

**Use `@app.put()`** for:

- Updating existing resources: `@app.put("/assets/{asset_id}")`
- Replacing configurations: `@app.put("/settings")`

**Use `@app.delete()`** for:

- Removing resources: `@app.delete("/assets/{asset_id}")`
- Cleanup operations: `@app.delete("/cache")`

#### Parameters

All endpoint functions must accept `client: CogniteClient` as the first parameter. Additional parameters can be:

- **Path parameters**: `{item_id}` in the URL path
- **Query parameters**: URL query string parameters
- **Request body**: Pydantic models for POST/PUT requests

**Parameter Injection and Override Behavior:**

The framework automatically injects certain parameters into endpoint functions. Currently, this includes the `client: CogniteClient` parameter which is automatically provided as the first parameter to all endpoint functions.

If users provide parameters with the same names in their request arguments (through query parameters, path parameters, or request body), the framework will attempt to override the injected values with strict type validation. The provided values must be convertible to the expected parameter types, or a validation error will be raised.

```python
@app.get("/example/{count}")
def example_endpoint(client: CogniteClient, name: str, count: int) -> dict:
    # client is normally the injected CogniteClient instance

    # Parameter override examples:
    # {"name": "test", "count": "123"}         ✅ Works - valid conversions
    # {"name": "test", "count": "abc"}         ❌ ValidationError - cannot convert "abc" to int
    # {"client": "invalid", "name": "test"}    ❌ ValidationError - cannot convert string to CogniteClient

    return {"message": f"Hello {name}, count: {count}"}
```

### create_function_handle

Creates a handler function from one or more composed apps. This is the main entry point for converting your CogniteApp instances into a function compatible with Cognite Functions.

```python
from cognite_typed_functions import create_function_handle

# Single app
handle = create_function_handle(app)

# Multiple apps (composition)
handle = create_function_handle(mcp_app, introspection_app, main_app)
```

#### Function Signature

```python
def create_function_handle(*apps: CogniteApp) -> Handler:
    """Create handler for single app or composed apps.

    Args:
        apps: Single CogniteApp or sequence of CogniteApps to compose.
              For composed apps, routing tries each app left-to-right until one matches.

    Returns:
        Handler function compatible with Cognite Functions
    """
```

#### App Composition Rules

1. **Routing Order**: Apps are tried **left-to-right** for route matching
2. **Metadata Source**: The **last app** provides title/version for schemas and health checks
3. **Context Sharing**: All apps get composition context, can override method if they need it
4. **Simplicity**: Clean method calls, no complex protocols or type checking overhead

#### Composition Patterns

**System + Business Pattern:**

```python
# Introspection provides system endpoints, main_app provides business logic
handle = create_function_handle(introspection_app, main_app)
```

**Full Stack Pattern:**

```python
# Complete composition: AI tools + debugging + business logic
handle = create_function_handle(mcp_app, introspection_app, main_app)
```

**Development Pattern:**

```python
# Add debugging capabilities to any existing handler
debug_handle = create_function_handle(introspection_app, existing_app)
```

### Request Format

Cognite Functions receive requests in this format:

```python
{
    "path": "/items/123?include_tax=true&q=search",
    "method": "GET",
    "body": {...}  # Optional request body
}
```

### Response Format

All responses are wrapped in a structured format:

```python
# Success response
{
    "success": true,
    "data": {...}  # Your actual response data
}

# Error response
{
    "success": false,
    "error_type": "ValidationError",
    "message": "Input validation failed: 1 error(s)",
    "details": {"errors": [...]}
}
```

## Built-in Endpoints

### Core Introspection

The introspection endpoints work across **all composed apps**, providing a unified view of your entire function:

- **`/__schema__`** - Returns the complete OpenAPI 3.0 schema for **ALL composed apps**
  - Uses the **last app** (main business app) for title/version metadata
  - Includes routes from introspection, MCP, and business apps
  - Perfect for generating client SDKs or API documentation

- **`/__routes__`** - Returns a summary of all available routes from **ALL apps** with descriptions
  - Shows endpoints from every app in the composition
  - Includes method types, descriptions, and app attribution
  - Ideal for API discovery and debugging

- **`/__health__`** - Returns health status and comprehensive information about **ALL composed apps**
  - Lists all apps in the composition with their route counts
  - Uses main business app metadata for primary identification
  - Includes statistics across the entire composed function

- **`/__ping__`** - Simple connectivity check endpoint for monitoring and pre-warming

### Cross-App Introspection Benefits

When you compose apps like `create_function_handle(mcp, introspection, main_app)`:

```json
// /__schema__ response includes:
{
  "info": {
    "title": "Your Main App",      // From main_app (last in composition)
    "version": "1.0.0"
  },
  "paths": {
    "/__mcp_tools__": {...},       // From MCP app
    "/__schema__": {...},          // From introspection app
    "/your/business/route": {...}  // From main business app
  }
}
```

This **unified introspection** means you never lose track of your function's capabilities, regardless of how many apps you compose together.

### MCP Endpoints

- **`/__mcp_tools__`** - List all available MCP tools with their schemas
- **`/__mcp_call__/{tool_name}`** - Execute a specific MCP tool by name

## Type Safety

The framework provides comprehensive type safety:

- **Input validation**: Pydantic models validate request data
- **Output validation**: Response models ensure consistent output format
- **Type coercion**: Automatic conversion of string parameters to correct types
- **Error handling**: Structured error responses with detailed information

### Supported Type Conversions

The framework features a powerful **recursive type converter** that handles complex nested data structures automatically:

#### Basic Type Conversions

- `str` → `int` / `float` / `bool` (accepts "true", "1", "yes", "on")

#### Pydantic Model Conversions

- `dict` → `BaseModel` - Automatic instantiation with validation
- `list[dict]` → `list[BaseModel]` - Converts lists of dictionaries to model instances

#### Advanced Recursive Types

The converter can handle arbitrarily nested combinations:

```python
# Complex nested types supported out-of-the-box
dict[str, BaseModel]                    # Dict with model values
Optional[BaseModel]                     # Optional models
Union[BaseModel, str]                   # Union types with fallback
list[dict[str, BaseModel]]              # Super nested: list of dicts of models
dict[str, list[BaseModel]]              # Dict containing lists of models

# Real-world example
class User(BaseModel):
    name: str
    age: int

class Team(BaseModel):
    name: str
    leader: User                        # Nested model
    members: list[User]                 # List of models

@app.post("/teams")
def create_team(client: CogniteClient, team: Team) -> TeamResponse:
    # Input automatically converted:
    # {
    #   "name": "Engineering",
    #   "leader": {"name": "Alice", "age": 30},      # → User instance
    #   "members": [                                 # → list[User]
    #     {"name": "Bob", "age": 25},                # → User instance
    #     {"name": "Carol", "age": 28}               # → User instance
    #   ]
    # }
    return TeamResponse(id=team.name, members_count=len(team.members))
```

#### Error Handling with Path Information

Validation errors include precise paths for easy debugging:

```python
# Invalid nested data:
# {"teams": {"frontend": [{"name": "Alice"}]}}  # Missing 'age' field

# Error message:
# "Validation error for BaseModel at teams[frontend][0]: age field required"
```

#### Type Annotation Compatibility

The framework fully supports **both legacy and modern Python type annotation syntaxes**, ensuring compatibility across different Python versions and coding styles:

**Union Types:**

```python
# Both syntaxes work identically
from typing import Union

# Legacy syntax (all Python versions)
def process_data(client: CogniteClient, data: Union[User, str]) -> Response: ...

# Modern syntax (Python 3.10+)
def process_data(client: CogniteClient, data: User | str) -> Response: ...
```

**Optional Types:**

```python
# Both syntaxes work identically
from typing import Optional

# Legacy syntax
def get_user(client: CogniteClient, user: Optional[User]) -> Response: ...

# Modern syntax
def get_user(client: CogniteClient, user: User | None) -> Response: ...
```

**Collection Types:**

```python
# Both syntaxes work identically
from typing import List, Dict

# Legacy syntax
def process_items(client: CogniteClient, items: List[Item]) -> Dict[str, int]: ...

# Modern syntax (recommended)
def process_items(client: CogniteClient, items: list[Item]) -> dict[str, int]: ...
```

**Key Benefits:**

- ✅ **Seamless migration** - Mix and match syntaxes as needed
- ✅ **Team flexibility** - Support different developer preferences
- ✅ **Future-proof** - Modern syntax ready for Python 3.10+
- ✅ **Zero configuration** - Works automatically with any syntax

The framework automatically handles type introspection and conversion regardless of which syntax you use, making it easy to adopt modern type hints at your own pace.

## Architecture

The framework is organized into several modules:

- **`app.py`** - Core application class and request handling with FastAPI-style decorators
- **`models.py`** - Shared Pydantic models for responses, errors, and request parsing
- **`schema.py`** - OpenAPI schema generation utilities
- **`introspection.py`** - Core introspection endpoints (schema, routes, health)
- **`mcp.py`** - Model Context Protocol integration and AI tool exposure

### Key Components

1. **CogniteApp** - Main application class with FastAPI-style decorators
2. **create_function_handle(*apps)** - Creates composed handler from multiple apps
3. **App Composition System**:
   - **Method override**: Apps override `set_context()` if they need access
   - **Automatic context provision**: Context provided to all apps during composition
   - **Left-to-right routing**: Earlier apps in composition handle routes first
   - **Last-app metadata**: Uses final app for title/version in schemas
4. **SchemaGenerator** - Generates unified OpenAPI documentation across all apps
5. **Built-in Apps**:
   - **IntrospectionApp**: Provides `/__schema__`, `/__routes__`, `/__health__` endpoints
   - **MCPApp**: Provides `/__mcp_tools__`, `/__mcp_call__/*` endpoints
6. **Request Processing Pipeline**:
   - Parse request data and URL
   - Try each composed app in order (left-to-right evaluation)
   - Find matching route in current app
   - Validate and coerce parameters with recursive type conversion
   - Execute function with automatic error handling
   - Format response with structured success/error format

## Error Handling

The framework provides structured error handling for common scenarios:

- **RouteNotFound** - No matching route found
- **ValidationError** - Input validation failed
- **TypeConversionError** - Parameter type conversion failed
- **ExecutionError** - Function execution failed

All errors include detailed information to help with debugging.

## Extensibility and App Composition

> **Note:** This is an advanced feature for framework extensibility. Most developers won't need to use app composition directly - it's primarily used internally for features like MCP integration and introspection endpoints. For typical use cases, simply create one `CogniteApp` and add your routes.

The framework supports composing multiple apps together to create modular, enterprise-grade functions. This allows you to separate concerns and create reusable components.

### Composition Architecture

Apps are composed using **left-to-right evaluation** for routing, but the **last app** in the composition is treated as the main business app for metadata (title, version).

```python
from cognite_typed_functions import CogniteApp, create_function_handle
from cognite_typed_functions.introspection import create_introspection_app

# Create individual apps
introspection_app = create_introspection_app()  # System endpoints
main_app = CogniteApp("Asset Management API", "2.1.0")  # Business logic

@main_app.get("/assets/{asset_id}")
def get_asset(client: CogniteClient, asset_id: int) -> dict:
    return {"id": asset_id, "name": f"Asset {asset_id}"}

# Compose apps: introspection first for system endpoints, main app last for business logic
handle = create_function_handle(introspection_app, main_app)
```

### Key Composition Benefits

- **🔍 Cross-app introspection**: `/__schema__` and `/__routes__` show routes from ALL composed apps
- **📊 Unified metadata**: Uses the last app (main business app) for title/version in schemas
- **🎯 Routing precedence**: Earlier apps in composition handle routes first (system > business)
- **🧩 Modular design**: Separate system utilities from business logic
- **🔧 Easy extensibility**: Add new capabilities without modifying existing apps

### Composition Examples

**Basic Composition with Introspection:**

```python
# Introspection + Main App
handle = create_function_handle(introspection_app, main_app)

# Available endpoints:
# /__schema__   -> Schema for ALL apps (titled "Asset Management API")
# /__routes__   -> Routes from ALL apps
# /__health__   -> Health check with composed app info
# /assets/123   -> Your business endpoint
```

**Full Stack Composition (MCP + Introspection + Main):**

```python
from cognite_typed_functions.mcp import create_mcp_server

# Create all apps
mcp_app = create_mcp_server(main_app, "asset-tools")
introspection_app = create_introspection_app()
main_app = CogniteApp("Asset Management API", "2.1.0")

# Compose: MCP -> Introspection -> Main
handle = create_function_handle(mcp_app, introspection_app, main_app)

# Available endpoints:
# /__mcp_tools__     -> AI tool discovery
# /__mcp_call__/*    -> AI tool execution
# /__schema__        -> Complete API schema
# /__routes__        -> All routes from all apps
# /__health__        -> Composite health status
# /assets/123        -> Business endpoints
```

### Simple Yet Powerful Architecture

The composition system uses a simple, clean design:

- **Method override**: Apps can override `set_context()` if they need composition access
- **Automatic calling**: Context provided to all apps during composition
- **No complexity**: Simple method calls, no protocols or complex type checking

### Running the Example

The framework includes a complete example in `examples/handler.py` showing:

- FastAPI-style decorators with type validation
- MCP integration with `@mcp.tool()` decorator
- Built-in introspection endpoints

Key capabilities:

- **Retrieving the complete OpenAPI schema** - Never forget your function's interface again!
- **Listing available routes** - Discover all endpoints and their descriptions
- **Health check endpoint** - Monitor function status and metadata
- **MCP tool exposure** - AI-accessible function calls

### Function Introspection - No More "Black Box" Functions

One of the biggest pain points with standard Cognite Functions is that after deployment, they become "black boxes." Customers often can't remember:

- What parameters the function expects
- What the expected data format is
- What endpoints are available
- What the function actually does

Our framework solves this with built-in introspection endpoints:

```bash
# Get complete API documentation
curl "https://your-function-url" -d '{"path": "/__schema__", "method": "GET"}'

# List all available endpoints
curl "https://your-function-url" -d '{"path": "/__routes__", "method": "GET"}'

# Check function health and metadata
curl "https://your-function-url" -d '{"path": "/__health__", "method": "GET"}'
```

**This means:**

- ✅ **No more redeployments** just to check function signatures
- ✅ **AI tools can discover** and generate code for your functions
- ✅ **Team members can easily** understand and use deployed functions
- ✅ **Documentation stays in sync** with the actual implementation

## Deployment to Cognite Functions

This framework is fully compatible with [Cognite Functions deployment methods](https://docs.cognite.com/cdf/functions/). You can deploy using any of the standard approaches:

### Deploy from Folder

```python
from cognite.client import CogniteClient

client = CogniteClient(project="my-project", token="my-token")

func = client.functions.create(
    name="my-typed-function",
    external_id="my-typed-function",
    folder="path/to/typed-cognite-functions"  # This repository
)
```

### Deploy from Zip File

```python
func = client.functions.create(
    name="my-typed-function",
    external_id="my-typed-function",
    file_id=123456789  # Uploaded zip file ID
)
```

### Key Points

- ✅ **Same entry point**: Uses the standard `handle(client, data)` function internally
- ✅ **All features supported**: Scheduling, secrets, environment variables work as expected
- ✅ **Same security model**: Uses the same security model as Cognite Functions
- ✅ **Standard deployment**: Works with CDF UI, Python SDK, and API deployment methods

The framework simply provides a better developer experience on top of the existing Cognite Functions infrastructure!

## Limitations

- The framework do not support multiple body parameters. This might be supported in the future.

## Development

### Project Structure

```text
cognite-typed-functions/
├── src/
│   └── cognite_typed_functions/
│       ├── __init__.py
│       ├── app.py              # Core CogniteApp class and decorators
│       ├── convert.py          # Type conversion and argument processing utilities
│       ├── formatting.py       # Formatting utilities for docstrings and tool names
│       ├── models.py           # Pydantic models and type definitions
│       ├── routing.py          # Route matching and management
│       ├── schema.py           # OpenAPI schema generation
│       ├── introspection.py    # Built-in introspection endpoints
│       └── mcp.py              # Model Context Protocol integration
├── examples/
│   └── handler.py              # Complete example with MCP integration
├── tests/                      # Comprehensive test suite
│   ├── test_app.py
│   ├── test_convert.py                    # Core type conversion tests
│   ├── test_convert_edge_cases.py         # Edge cases and error handling
│   ├── test_convert_property_based.py     # Property-based testing with Hypothesis
│   ├── test_error_handling.py
│   ├── test_formatting.py
│   ├── test_handle_function.py
│   ├── test_introspection.py
│   ├── test_mcp.py
│   ├── test_models.py
│   └── test_routing.py
├── pyproject.toml              # Project configuration and dependencies
└── README.md
```

### Running Tests

To run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=cognite_typed_functions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Inspired by [FastAPI](https://fastapi.tiangolo.com/) for the decorator-based API design
- Built for [Cognite Data Fusion](https://www.cognite.com/) [Functions](https://docs.cognite.com/cdf/functions/) platform
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
