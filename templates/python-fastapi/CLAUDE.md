# Project: [Project Name]

## Overview

[Brief description of what this project does]

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy / SQLModel
- **Async**: asyncio with async SQLAlchemy
- **Testing**: pytest with pytest-asyncio
- **Package Manager**: Poetry / pip with requirements.txt

## Project Structure

```
app/
├── main.py              # FastAPI app initialization
├── config.py            # Settings and configuration
├── api/
│   ├── routes/          # API route handlers
│   ├── deps.py          # Dependency injection
│   └── middleware.py    # Custom middleware
├── core/
│   ├── security.py      # Auth and security utilities
│   └── exceptions.py    # Custom exceptions
├── models/              # SQLAlchemy/Pydantic models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
├── repositories/        # Data access layer
└── tests/               # Test files
```

## Development Commands

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
# or with Poetry: poetry install

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Type checking
mypy app/

# Linting
ruff check app/

# Format code
ruff format app/

# Run database migrations
alembic upgrade head
```

## Coding Conventions

### File Naming
- Use snake_case for files and directories
- Use snake_case for functions and variables
- Use PascalCase for classes

### Code Style
- Follow PEP 8 (enforced by ruff)
- Use type hints for all function parameters and returns
- Prefer f-strings for string formatting
- Max line length: 88 characters (black default)

### Async/Await
- Use async functions for I/O operations
- Use `async with` for database sessions
- Avoid blocking operations in async functions

### API Design
```python
# Use Pydantic models for request/response
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    ...
```

### Dependency Injection
```python
# Use FastAPI's Depends for DI
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    ...
```

## Important Patterns

### Service Layer
```python
# Business logic in services, not routes
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: UserCreate) -> User:
        # Business logic here
        ...
```

### Error Handling
```python
# Use HTTPException or custom exceptions
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
```

## Environment Variables

Required variables (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `ENVIRONMENT` - dev/staging/production
- `CORS_ORIGINS` - Allowed CORS origins

## Sensitive Areas

- `app/core/security.py` - Authentication and password hashing
- `alembic/versions/` - Database migrations
- `app/config.py` - Environment and secrets handling

## Common Issues

1. **Async session issues**: Use `async with` for sessions
2. **Circular imports**: Use `TYPE_CHECKING` for type hints
3. **Migration conflicts**: Never edit existing migrations
