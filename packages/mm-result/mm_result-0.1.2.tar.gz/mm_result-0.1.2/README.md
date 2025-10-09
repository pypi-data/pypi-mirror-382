# mm-result

Functional error handling for Python using Result types inspired by Rust.

A `Result[T]` represents either a successful value (`Ok`) or an error (`Err`), enabling functional programming patterns for error handling without exceptions. Each result can optionally carry additional metadata in the `extra` field for context like performance metrics, HTTP details, or debugging information.

## Quick Start

```python
from mm_result import Result
import time

def fetch_user_data(user_id: int) -> Result[dict]:
    start_time = time.time()

    if user_id <= 0:
        return Result.err("Invalid user ID", extra={
            "user_id": user_id,
            "validation_rule": "user_id > 0"
        })

    # Simulate API call
    if user_id == 999:
        return Result.err("User not found", extra={
            "user_id": user_id,
            "response_time_ms": round((time.time() - start_time) * 1000),
            "status_code": 404
        })

    user_data = {"id": user_id, "name": f"User {user_id}"}
    return Result.ok(user_data, extra={
        "response_time_ms": round((time.time() - start_time) * 1000),
        "cache_hit": False,
        "status_code": 200
    })

# Using explicit success checking
result = fetch_user_data(123)
if result.is_ok():
    user = result.unwrap()
    print(f"Success: {user['name']}")
    print(f"Response time: {result.extra['response_time_ms']}ms")
else:
    error = result.unwrap_err()
    print(f"Error: {error}")
    if "status_code" in result.extra:
        print(f"HTTP Status: {result.extra['status_code']}")
```

## Core Features

### Creating Results

```python
# Success values
result = Result.ok(42)
result = Result.ok(None)  # Ok with None value
result = Result.ok("data", extra={"metadata": "info"})

# Error values
result = Result.err("Something went wrong")
result = Result.err("Network timeout", extra={"retry_count": 3, "endpoint": "/api/users"})
result = Result.err(ValueError("Bad input"))  # From exception
result = Result.err(("Custom error", exc))    # Custom message + exception
```

### Checking Results

```python
result = Result.ok(42)

result.is_ok()    # True
result.is_err()   # False

if result.is_ok():  # Explicit way to check success
    print("Success!")
```

### Extracting Values

```python
result = Result.ok(42)

# Extract value (raises RuntimeError if error)
value = result.unwrap()                    # 42
value = result.unwrap("Custom message")    # With custom error message

# Extract value with fallback
value = result.unwrap_or(0)               # 42, or 0 if error

# Extract error (raises RuntimeError if success)
error = Result.err("oops").unwrap_err() # "oops"

# Get either value or error
content = result.value_or_error()         # Returns T | str
```

### Transforming Results

```python
# Map over success values
result = Result.ok(5)
doubled = result.map(lambda x: x * 2)     # Result.ok(10)

# Chain operations
result = Result.ok(5)
chained = result.chain(lambda x: Result.ok(x * 2))  # Result.ok(10)

# Async versions
async def async_double(x):
    return x * 2

doubled = await result.map_async(async_double)
```

### Error Handling with Extra Data

The `extra` field allows attaching arbitrary metadata:

```python
# HTTP request context
result = Result.err("Network timeout", extra={
    "status_code": 408,
    "response_time_ms": 5000,
    "retry_count": 3,
    "endpoint": "/api/data"
})

# Performance metrics
result = Result.ok(data, extra={
    "cache_hit": True,
    "query_time_ms": 15,
    "server": "prod-01"
})

# Exception details (automatic)
try:
    risky_operation()
except Exception as e:
    result = Result.err(e)  # Auto-captures exception + traceback in extra
```

### JSON Serialization

By default, `Result.to_dict()` may contain non-serializable objects like exceptions. Use `safe_exception=True` for JSON-safe output:

```python
import json

try:
    data = json.loads("invalid json")
except json.JSONDecodeError as e:
    result = Result.err(e)

# This would fail - exception objects aren't JSON serializable
# json.dumps(result.to_dict())  # TypeError!

# This works - converts exceptions to strings
safe_dict = result.to_dict(safe_exception=True)
json_string = json.dumps(safe_dict)  # ✅ Success

# safe_dict contains:
# {
#     "value": None,
#     "error": "JSONDecodeError: Expecting value...",
#     "extra": {"exception": "Expecting value..."}  # String, not object
#     # "traceback" is removed completely
# }
```

## Advanced Usage

### Exception Safety

Operations like `map()` and `chain()` automatically catch exceptions:

```python
def might_fail(x):
    if x < 0:
        raise ValueError("Negative input")
    return x * 2

result = Result.ok(-5)
safe_result = result.map(might_fail)  # Captures exception safely
# safe_result.is_err() == True
# safe_result.extra["exception"] contains the ValueError
```

### Working with Copies

```python
original = Result.ok(42, extra={"version": "1.0"})

# Create new result with different value, preserving extra
new_result = original.with_value("hello")
# new_result.unwrap() == "hello"
# new_result.extra == {"version": "1.0"}

# Create error from success, preserving extra
error_result = original.with_error("Something failed")
```

### Type Guards

```python
from mm_result import is_ok, is_err

def process_result(result: Result[int]) -> None:
    if is_ok(result):
        # Type checker knows result.value is int, not int | None
        value: int = result.value

    if is_err(result):
        # Type checker knows result.error is str, not str | None
        error: str = result.error
```

## Decorators

### @returns_result

Automatically wrap functions to return `Result[T]` and catch exceptions:

```python
from mm_result import returns_result

@returns_result
def divide(a: int, b: int) -> float:
    return a / b

result = divide(10, 2)   # Result.ok(5.0)
result = divide(10, 0)   # Result.err(ZeroDivisionError(...))

if result.is_ok():
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.unwrap_err()}")
    # Exception details automatically captured in result.extra
```

### @async_returns_result

Async version for coroutines:

```python
from mm_result import async_returns_result
import httpx

@async_returns_result
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

result = await fetch_data("https://api.example.com")
if result.is_ok():
    data = result.unwrap()
    print(f"Fetched: {data}")
else:
    print(f"Request failed: {result.unwrap_err()}")
```

## Pydantic Integration

When installed with `pip install mm-result[pydantic]`:

```python
from pydantic import BaseModel
from mm_result import Result

class ApiResponse(BaseModel):
    result: Result[dict]
    timestamp: str

# Serialization
response = ApiResponse(
    result=Result.ok({"key": "value"}),
    timestamp="2024-01-01T00:00:00Z"
)
data = response.model_dump()
# {
#     "result": {"value": {"key": "value"}, "error": None, "extra": None},
#     "timestamp": "2024-01-01T00:00:00Z"
# }

# Deserialization
response2 = ApiResponse.model_validate(data)
assert response2.result.is_ok()
assert response2.result.unwrap() == {"key": "value"}
```

## API Reference

### Result[T]

#### Class Methods
- `Result.ok(value: T, extra: dict = None) -> Result[T]` - Create success result
- `Result.err(error: str | Exception | tuple, extra: dict = None) -> Result[T]` - Create error result

#### Instance Methods
- `is_ok() -> bool` - Check if result is success
- `is_err() -> bool` - Check if result is error
- `unwrap(message_prefix: str = None, include_error: bool = True) -> T` - Extract value or raise
- `unwrap_or(default: T) -> T` - Extract value or return default
- `unwrap_err() -> str` - Extract error message or raise
- `value_or_error() -> T | str` - Extract value or error
- `map(fn: Callable[[T], U]) -> Result[U]` - Transform success value
- `chain(fn: Callable[[T], Result[U]]) -> Result[U]` - Chain operations
- `map_async(fn: Callable[[T], Awaitable[U]]) -> Result[U]` - Async transform
- `chain_async(fn: Callable[[T], Awaitable[Result[U]]]) -> Result[U]` - Async chain
- `with_value(value: U) -> Result[U]` - Copy with new value
- `with_error(error) -> Result[T]` - Copy as error
- `to_dict(safe_exception: bool = False) -> dict[str, Any]` - Dictionary representation

#### Type Guards
- `is_ok(result: Result[T]) -> TypeGuard[OkResult[T]]` - Type-safe check for Ok result
- `is_err(result: Result[T]) -> TypeGuard[ErrResult[T]]` - Type-safe check for Err result

#### Decorators
- `@returns_result` - Wrap function to return `Result[T]` and auto-catch exceptions
- `@async_returns_result` - Async version of `@returns_result`

#### Custom Exceptions
- `UnwrapError` - Raised when `unwrap()` is called on an Err result
- `UnwrapErrError` - Raised when `unwrap_err()` is called on an Ok result
