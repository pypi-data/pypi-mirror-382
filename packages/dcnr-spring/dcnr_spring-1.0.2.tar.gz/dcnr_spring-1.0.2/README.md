# DCNR Spring API Documentation

The `dcnr_spring` is a comprehensive Python package providing utilities for application monitoring, database operations, security, subprocess management, and more. This package follows Spring Framework patterns and provides a robust foundation for enterprise Python applications.

## Package Overview

```python
import dcnr_spring

# Available modules
dcnr_spring.actuator      # Application health monitoring
dcnr_spring.coding        # Development utilities
dcnr_spring.database      # Database abstraction layer
dcnr_spring.monitor       # System monitoring and logging
dcnr_spring.notifications # Event notification system
dcnr_spring.requests      # Request handling utilities
dcnr_spring.security      # Security and encryption
dcnr_spring.subprocess    # Process management
dcnr_spring.utils         # General utilities
```

## spring.actuator

Provides monitoring status for application components. It maintains in-memory data that can be requested by external systems. It provides only the data backend - the interface with external systems (HTTP, RabbitMQ, etc.) must be implemented by the application.

### Functions

**`register_actuator_component(name: str, status_func: Callable[[], str], details_func: Callable[[], Dict] = None)`**
- Registers a component for health monitoring
- `name`: Component identifier
- `status_func`: Function returning component status (UP/DOWN/NA)
- `details_func`: Optional function returning additional component details

**`on_actuator_endpoint(name: str) -> Callable`**
- Decorator for registering actuator endpoints
- `name`: Endpoint name

**`on_actuator_root() -> Callable`**
- Decorator for the root actuator endpoint

**`is_ok(component_name: str) -> bool`**
- Checks if a component status is OK (UP)

**`get_actuator_components() -> Dict[str, Dict]`**
- Returns all registered components and their status

**`get_component_response(name: str) -> Dict`**
- Gets detailed response for a specific component

### Constants

- `STATUS_OK = "UP"` - Component is healthy
- `STATUS_FAIL = "DOWN"` - Component has issues
- `STATUS_UNKNOWN = "NA"` - Component status unknown

### Example

```python
from dcnr_spring.actuator import register_actuator_component, STATUS_OK, STATUS_FAIL

def database_health():
    try:
        # Check database connection
        return STATUS_OK
    except:
        return STATUS_FAIL

def database_details():
    return {"connection_pool": 5, "active_connections": 2}

register_actuator_component("database", database_health, database_details)
```

## spring.coding

Development utilities and decorators.

### Decorators

**`@deprecated(reason: str = None, version: str = None)`**
- Marks functions/classes as deprecated
- Issues warning when deprecated items are used
- `reason`: Optional deprecation reason
- `version`: Optional version when deprecated

### Example

```python
from dcnr_spring.coding import deprecated

@deprecated("Use new_function() instead", version="2.0")
def old_function():
    return "deprecated"
```

## spring.database

Database abstraction layer with ORM-like functionality supporting multiple backends.

### Core Classes

**`DatabaseEntity`**
- Base class for database entities
- Provides common database operations

**`Database`**
- Abstract base class for database implementations
- Defines standard interface for database operations

### Decorators

**`@dbtable(schema: str = None, table: str = None, repr: bool = True)`**
- Class decorator for database entities
- Automatically generates `__init__`, field metadata, and database operations
- `schema`: Database schema name
- `table`: Table name (defaults to class name)

**`dbfield(alias: str = None, primary: bool = False, nullable: bool = True, default: Any = None, dtype: str = None)`**
- Field descriptor for database columns
- `alias`: Database column name (if different from field name)
- `primary`: Mark as primary key
- `nullable`: Allow null values
- `default`: Default value
- `dtype`: Database data type

### Database Backends

**Memory Database**
```python
from dcnr_spring.database.memory import MemoryDatabase

db = MemoryDatabase()
```

**PostgreSQL Database**
```python
from dcnr_spring.database.postgres import PostgresDatabase

db = PostgresDatabase(connection_string="postgresql://...")
```

### Query Expressions

**`F(field_name: str)`**
- Creates field expressions for queries
- Supports comparison operators: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Supports logical operators: `&` (AND), `|` (OR)

**`Q(**kwargs)`**
- Creates query expressions from keyword arguments
- Combines multiple conditions with AND logic

### Example

```python
from dcnr_spring.database import DatabaseEntity, dbtable, dbfield
from dcnr_spring.database.memory import MemoryDatabase
from dcnr_spring.database.base.query_expression import F, Q

@dbtable(schema="app", table="users")
class User(DatabaseEntity):
    name: str = dbfield()
    email: str = dbfield(alias="email_address")
    age: int = dbfield(default=0)

# Database operations
db = MemoryDatabase()

# Insert
user = User(name="John", email="john@example.com", age30)
db.insert(user)

# Query with expressions
adults = db.find(User, F('age') >= 18)
active_users = db.find(User, F('status') == 'active', F('last_login') > yesterday)

# Complex queries
engineers = db.find(User, 
                   (F('department') == 'Engineering') & (F('experience') > 2))

# Delete operations
deleted_count = db.delete(User, F('age') < 18)

# Chaining with order and limit
top_users = db.find(User, F('score') > 100).order(score='desc').limit(10)
```

## spring.monitor

System monitoring and application telemetry.

### Client Monitoring

**PodHub Sync Functions**
- `set_application_name(name: str)` - Set application identifier
- `set_server_url(url: str)` - Set monitoring server URL  
- `start_pod_hub()` - Start monitoring client
- `stop_pod_hub()` - Stop monitoring client

**Live Data Logging**
- `livedata_log(tag: str, level: str, message: str, exception: Exception = None)` - Log application events
- `livedata_page()` - Get current live data page
- `livedata_setlimit(tag: str, limit: int)` - Set log retention limit

**Instance Management**
- `set_instance_status(status: str)` - Update instance status
- `get_instance_status() -> str` - Get current instance status

**System Information**
- `get_pip_packages()` - Get installed Python packages
- `get_logger_list()` - Get available loggers

**Performance Monitoring**
- `codepoint_log(point: str, message: str)` - Log performance checkpoint
- `codepoints_get_tree()` - Get performance data tree
- `codepoints_get_list()` - Get performance data list

### Server Monitoring

**PodHub Server Classes**
- `PodHubApplication` - Main monitoring application
- `PodHubInfo` - Information management
- `PodHubData` - Data storage and retrieval

**Server Functions**
- `register_endpoints(app)` - Register monitoring endpoints
- `get_app_pips(app_name: str)` - Get application packages
- `get_live_services()` - Get live service list
- `ai_get_app(query: str)` - AI-powered app information
- `get_app_instances(app_name: str)` - Get application instances

### Memory Monitoring

- `start_memory_watch()` - Start memory monitoring
- `stop_memory_watch()` - Stop memory monitoring  
- `add_threshold(threshold: int, callback: Callable)` - Add memory threshold
- `get_memory_usage() -> MemoryUsage` - Get current memory usage
- `hist_memory_max()` - Get historical memory maximum

### Thread Database

- `get_thread_record(thread_id: str)` - Get thread information
- `get_live_threads()` - Get active threads
- `save_thread_data(data: Dict)` - Save thread correlation data
- `get_thread_data(thread_id: str)` - Retrieve thread data

### Example

```python
from dcnr_spring.monitor.client import (
    set_application_name, start_pod_hub, livedata_log, 
    set_instance_status, codepoint_log
)

# Setup monitoring
set_application_name("my-app")
start_pod_hub()

# Log events
livedata_log("app", "INFO", "Application started")
set_instance_status("running")

# Performance monitoring
codepoint_log("startup", "Application initialization complete")
```

## spring.notifications

Event notification and messaging system with thread-safe operations.

### Notification Center

**`send(message: str, category: str = None, **kwargs)`**
- Send notification to registered handlers
- `message`: Notification message
- `category`: Optional message category
- `**kwargs`: Additional message data

**`register(handler: Callable, category: str = None)`**
- Register notification handler
- `handler`: Function to handle notifications
- `category`: Optional category filter

**`unregister(handler: Callable, category: str = None)`**
- Unregister notification handler

### Service Management

**`shutdown_service()`**
- Initiate graceful service shutdown
- Sends shutdown notifications to registered handlers

**`is_shutting_down() -> bool`**
- Check if service shutdown is in progress

### Test Mode

**`set_test_mode(enabled: bool)`**
- Enable/disable test mode
- Affects shutdown behavior and logging

**`get_test_mode() -> bool`**
- Check if test mode is enabled

### Thread-Safe Utilities

**`LockedValue[T]`**
- Thread-safe value container
- Provides atomic read/write operations with locking

### Example

```python
from dcnr_spring.notifications import send, register, shutdown_service

def error_handler(message, category=None, **kwargs):
    print(f"Error: {message}")

def info_handler(message, category=None, **kwargs):
    print(f"Info: {message}")

# Register handlers
register(error_handler, "error")
register(info_handler, "info")

# Send notifications
send("Application started", "info")
send("Database connection failed", "error", details={"host": "localhost"})

# Graceful shutdown
shutdown_service()
```

## spring.requests

Request handling and message service utilities.

### Request Logging

**`StreamLogger`**
- Logger that writes to string stream
- Useful for capturing log output in memory

### Message Services

**`MessageServiceClient`**
- Base class for message service implementations
- Provides common patterns for request/response handling

**`EmptyMessageService`**
- No-op implementation for testing
- Safe fallback when no real service is available

### Request Counting

**`@message_counter(name: str = None)`**
- Decorator for counting method calls
- `name`: Optional counter name (defaults to method name)

**`counter.get_count(name: str) -> int`**
- Get current count for named counter

**`counter.wait_for_empty(name: str, timeout: float = None) -> bool`**
- Wait for counter to reach zero
- Useful for ensuring all requests are processed

### Example

```python
from dcnr_spring.requests import StreamLogger, message_counter, counter

# Stream logging
logger = StreamLogger()
logger.info("Test message")
output = logger.getvalue()

# Request counting
@message_counter("api_calls")
def handle_request():
    # Process request
    pass

# Check counts
current_count = counter.get_count("api_calls")
counter.wait_for_empty("api_calls", timeout=30.0)
```

## spring.security

Security utilities and encryption functions.

### Encryption

**`ciphering.cipher(data: str, key: str) -> str`**
- Encrypt data using XOR cipher
- `data`: String to encrypt
- `key`: Encryption key
- Returns: Encrypted string

**`ciphering.decipher(encrypted: str, key: str) -> str`**
- Decrypt data using XOR cipher
- `encrypted`: Encrypted string
- `key`: Decryption key (must match encryption key)
- Returns: Decrypted string

### Example

```python
from dcnr_spring.security.ciphering import cipher, decipher

# Encrypt sensitive data
secret = "sensitive information"
key = "my-secret-key"
encrypted = cipher(secret, key)

# Decrypt when needed
decrypted = decipher(encrypted, key)
assert decrypted == secret
```

## spring.subprocess

Process management and subprocess utilities.

### Process Arguments

**`SubprocessArguments`**
- Container for subprocess arguments
- Handles serialization of complex data types

### Process Communication

**`SubprocessPickleRunner`**
- Executes functions in subprocess using pickle serialization
- Handles bidirectional communication

**`SubprocessPickle`**
- Manages pickle-based subprocess communication
- Provides high-level interface for process management

### Process Results

**`SubprocessResult`**
- Container for subprocess execution results
- Includes return value, stdout, stderr, and exit code

### Environment Detection

**`is_subprocess() -> bool`**
- Detect if current process is a subprocess
- Uses environment variable `SUBPROCESS_ENV_NAME`

**`SUBPROCESS_ENV_NAME = "DCNR_SPRING_SUBPROCESS"`**
- Environment variable name used for subprocess detection

### Example

```python
from dcnr_spring.subprocess import SubprocessPickleRunner, is_subprocess

def worker_function(data):
    # Process data in subprocess
    return data * 2

if not is_subprocess():
    runner = SubprocessPickleRunner()
    result = runner.execute(worker_function, args=[5])
    print(result.return_value)  # 10
```

## spring.utils

General utilities and helper classes.

### Thread-Safe Counter

**`SafeCounter`**
- Thread-safe counter implementation
- Supports increment, decrement, and atomic operations
- Methods:
  - `increment() -> int` - Increment and return new value
  - `decrement() -> int` - Decrement and return new value
  - `get() -> int` - Get current value
  - `set(value: int)` - Set value
  - `reset()` - Reset to zero

### Application Lifecycle

**`waitloop_start()`**
- Initialize application wait loop
- Used for graceful application lifecycle management

**`waitloop_is_at_exit() -> bool`**
- Check if application is in exit state
- Returns True when shutdown has been initiated

### File System Utilities

**`WorkingFileSpace`**
- Context manager for temporary directory management
- Automatically creates and cleans up working directories
- Methods:
  - `get_file_name(filename: str) -> str` - Get full path for file
  - `mkdir(dirname: str) -> str` - Create subdirectory
  - `exists(path: str) -> bool` - Check if path exists
  - `cleanup()` - Manual cleanup (automatic on exit)

### Example

```python
from dcnr_spring.utils import SafeCounter, WorkingFileSpace, waitloop_start

# Thread-safe counting
counter = SafeCounter()
counter.increment()  # Returns 1
current = counter.get()  # Returns 1

# Temporary workspace
with WorkingFileSpace(dirname="temp_work") as ws:
    file_path = ws.get_file_name("data.txt")
    subdir = ws.mkdir("subdirectory")
    # Directory automatically cleaned up on exit

# Application lifecycle
waitloop_start()
```

## Error Handling and Best Practices

### Exception Handling
All modules provide appropriate exception handling and error propagation. Use try-catch blocks for operations that may fail.

### Thread Safety
Components marked as thread-safe (SafeCounter, LockedValue, notification system) can be safely used in multi-threaded applications.

### Resource Management
Use context managers (WorkingFileSpace) and proper cleanup patterns. The package provides automatic resource management where possible.

### Testing
All modules include test mode support and utilities for unit testing. Use the test utilities in `dcnr_spring.notifications.testmode` for testing scenarios.

## Integration Examples

### Complete Application Setup

```python
from dcnr_spring.actuator import register_actuator_component, STATUS_OK
from dcnr_spring.database.memory import MemoryDatabase
from dcnr_spring.database import DatabaseEntity, dbtable, dbfield
from dcnr_spring.monitor.client import set_application_name, start_pod_hub
from dcnr_spring.notifications import register, send

# Database setup
@dbtable("app", "users")
class User(DatabaseEntity):
    name: str = dbfield()
    email: str = dbfield()

db = MemoryDatabase()

# Health monitoring
def db_health():
    return STATUS_OK if db else STATUS_FAIL

register_actuator_component("database", db_health)

# Application monitoring
set_application_name("my-application")
start_pod_hub()

# Event handling
def audit_handler(message, **kwargs):
    print(f"Audit: {message}")

register(audit_handler, "audit")

# Application ready
send("Application initialized", "audit")
```

This comprehensive API provides everything needed to build robust, monitorable, and maintainable Python applications following enterprise patterns.
