# Python Skill

Idiomatic Python patterns, type hints, tooling, and best practices for modern Python development.

## Activation

Use this skill when working on Python projects — writing new code, adding type hints, debugging, or setting up tooling.

---

## Tooling

| Tool | Purpose | Command |
|------|---------|---------|
| `uv` | Package manager (preferred) | `uv add <pkg>`, `uv run <cmd>` |
| `pip` | Package manager (fallback) | `pip install <pkg>` |
| `ruff` | Lint + format (fast, preferred) | `ruff check .`, `ruff format .` |
| `black` | Formatter (older standard) | `black .` |
| `mypy` | Static type checking | `mypy .` |
| `pyright` | Type checking (faster) | `pyright` |
| `pytest` | Testing | `pytest` |
| `flake8` | Linting (older) | `flake8 .` |

**Package management preference:** `uv` > `pip`. Check for `pyproject.toml` or `uv.lock` to confirm.

---

## Type Hints

Always add type hints. They enable mypy/pyright and improve readability.

```python
# Function signatures
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}!\n" * times).strip()

# Variables (use when type isn't obvious)
users: list[User] = []
lookup: dict[str, int] = {}

# Optional values
from typing import Optional
def find_user(id: int) -> Optional[User]:  # or: User | None (Python 3.10+)
    ...

# Union types (Python 3.10+)
def process(value: int | str | None) -> str:
    ...

# Generics
from typing import TypeVar, Generic
T = TypeVar('T')

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### Common type imports

```python
from typing import (
    Any, Optional, Union,
    List, Dict, Tuple, Set,  # use lowercase list/dict/tuple/set in Python 3.9+
    Callable, Iterator, Generator,
    TypeVar, Generic, Protocol,
    TYPE_CHECKING,
)
from collections.abc import Sequence, Mapping, Iterable

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from mymodule import HeavyClass
```

---

## Error Handling

```python
# Specific exceptions — never bare except
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except (ValueError, TypeError) as e:
    raise RuntimeError(f"Invalid input: {e}") from e

# Custom exceptions
class AppError(Exception):
    """Base exception for this application."""

class NotFoundError(AppError):
    def __init__(self, resource: str, id: int) -> None:
        super().__init__(f"{resource} with id={id} not found")
        self.resource = resource
        self.id = id

# Context managers for cleanup
with open(path) as f:
    data = f.read()
# file auto-closed even on exception
```

---

## Async (asyncio)

```python
import asyncio
from typing import AsyncIterator

# Basic async function
async def fetch_data(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

# Parallel execution
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3),
)

# Async context manager
class DatabaseConnection:
    async def __aenter__(self) -> 'DatabaseConnection':
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

# Use asyncio.run() at the entry point
if __name__ == '__main__':
    asyncio.run(main())
```

---

## Common Patterns

### Dataclasses

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.email = self.email.lower()
```

### Pydantic (for validation + serialization)

```python
from pydantic import BaseModel, field_validator

class UserRequest(BaseModel):
    name: str
    email: str
    age: int

    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Age must be positive')
        return v

user = UserRequest(name="Alice", email="alice@example.com", age=30)
user_dict = user.model_dump()
user_json = user.model_dump_json()
```

### Context managers

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)

with managed_resource() as r:
    use(r)
```

### List/dict comprehensions

```python
# Prefer comprehensions over map/filter for clarity
squares = [x**2 for x in range(10) if x % 2 == 0]
lookup = {user.id: user for user in users}
unique = {item.lower() for item in strings}

# Generator expressions for large sequences (lazy evaluation)
total = sum(x**2 for x in range(1_000_000))
```

---

## Code Style (Ruff/Black)

```python
# Line length: 88 chars (black default) or 100 chars
# Strings: double quotes (black enforces this)
# Trailing commas in multi-line collections

# Good multi-line formatting
def complex_function(
    first_argument: str,
    second_argument: int,
    third_argument: list[str],
) -> dict[str, Any]:
    return {
        "key": first_argument,
        "value": second_argument,
    }
```

---

## Testing with pytest

```python
import pytest
from unittest.mock import patch, MagicMock

def test_basic():
    assert add(2, 3) == 5

def test_raises():
    with pytest.raises(ValueError, match="must be positive"):
        validate_age(-1)

@pytest.fixture
def db():
    conn = create_test_db()
    yield conn
    conn.close()

def test_with_fixture(db):
    db.insert(User(id=1, name="Alice"))
    assert db.find(1).name == "Alice"

@pytest.mark.asyncio
async def test_async():
    result = await fetch_data()
    assert result is not None

# Parametrize
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert square(input) == expected
```

---

## FastAPI Patterns

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, name=user.name)
```
