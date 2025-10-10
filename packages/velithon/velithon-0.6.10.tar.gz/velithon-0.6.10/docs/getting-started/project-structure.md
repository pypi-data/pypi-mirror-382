# Project Structure

Learn how to organize your Velithon applications for maintainability, scalability, and team collaboration. This guide covers best practices for structuring projects from simple APIs to large enterprise applications.

## 🏗️ Basic Project Structure

For small to medium applications, here's the recommended structure:

```
my-velithon-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── tasks.py
│   ├── routers/             # Route handlers
│   │   ├── __init__.py
│   │   ├── api.py           # API version router
│   │   ├── users.py
│   │   └── tasks.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── email.py
│   ├── middleware/          # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── rate_limit.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── security.py
│       └── validators.py
├── tests/                   # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_main.py
│   └── test_routers/
├── static/                  # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── templates/               # Jinja2 templates
├── uploads/                 # File uploads
├── logs/                    # Application logs
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── .gitignore
└── README.md
```

## 🏢 Enterprise Project Structure

For large applications with multiple teams and microservices:

```
enterprise-velithon-app/
├── src/
│   ├── core/                # Core framework extensions
│   │   ├── __init__.py
│   │   ├── database.py      # Database connections
│   │   ├── cache.py         # Redis/cache utilities
│   │   ├── security.py      # Security utilities
│   │   └── config.py        # Base configuration
│   ├── apps/                # Application modules
│   │   ├── auth/            # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routers.py
│   │   │   ├── services.py
│   │   │   └── middleware.py
│   │   ├── users/           # User management
│   │   ├── orders/          # Order management
│   │   └── payments/        # Payment processing
│   ├── shared/              # Shared utilities
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── dependencies.py
│   │   ├── schemas.py       # Shared Pydantic models
│   │   └── constants.py
│   └── main.py              # Main application
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                 # Deployment scripts
├── docker/                  # Docker configurations
├── docs/                    # Documentation
├── migrations/              # Database migrations
├── monitoring/              # Monitoring configs
└── deployment/              # K8s, Terraform, etc.
```

## 📁 File Organization Guidelines

### 1. Application Entry Point (`main.py`)

```python title="app/main.py"
"""Main application entry point for Velithon RSGI app."""

from velithon import Velithon
from velithon.middleware.logging import LoggingMiddleware
from velithon.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import api_router
from app.middleware.auth import AuthenticationMiddleware

def create_app() -> Velithon:
    """Application factory pattern."""
    app = Velithon(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        middleware=[
            LoggingMiddleware(),
            CORSMiddleware(
                allow_origins=settings.BACKEND_CORS_ORIGINS,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
            AuthenticationMiddleware(),
        ]
    )
    
    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app

app = create_app()

if __name__ == "__main__":
    app._serve(
        app="app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=1,
        log_level="DEBUG" if settings.DEBUG else "INFO",
        reload=settings.DEBUG
    )
```

### 2. Configuration (`config.py`)

```python title="app/config.py"
"""Application configuration using Pydantic settings."""

import os
from typing import List, Optional
from pydantic import BaseSettings, AnyHttpUrl, validator

class Settings(BaseSettings):
    # Basic settings
    PROJECT_NAME: str = "Velithon API"
    DESCRIPTION: str = "High-performance RSGI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: List[str]) -> List[str]:
        if isinstance(v, str) and v.startswith("["):
            return eval(v)
        elif isinstance(v, (list, str)):
            return [str(origin).strip("/") for origin in v]
        raise ValueError(v)
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3. Router Organization (`routers/`)

```python title="app/routers/__init__.py"
"""Router initialization and organization."""

from velithon.routing import Router
from app.routers import users, tasks, auth

api_router = Router()

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
```

```python title="app/routers/api.py"
"""API version router for better versioning."""

from velithon.routing import Router
from app.routers import v1

api_router = Router()

# Version-specific routers
api_router.include_router(v1.router, prefix="/v1")

# You can add v2, v3, etc. here
# api_router.include_router(v2.router, prefix="/v2")
```

### 4. Model Organization (`models/`)

```python title="app/models/__init__.py"
"""Model exports for easy importing."""

from .users import User, UserCreate, UserUpdate, UserInDB
from .tasks import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from .auth import Token, TokenPayload, LoginRequest

__all__ = [
    # Users
    "User", "UserCreate", "UserUpdate", "UserInDB",
    # Tasks  
    "Task", "TaskCreate", "TaskUpdate", "TaskStatus", "TaskPriority",
    # Auth
    "Token", "TokenPayload", "LoginRequest",
]
```

### 5. Service Layer (`services/`)

```python title="app/services/__init__.py"
"""Service layer for business logic."""

from .database import DatabaseService
from .auth import AuthService
from .email import EmailService
from .cache import CacheService

__all__ = [
    "DatabaseService",
    "AuthService", 
    "EmailService",
    "CacheService",
]
```

## 🔧 Dependency Injection Organization

### Central DI Container

```python title="app/dependencies.py"
"""Central dependency injection configuration."""

from typing import Generator
from velithon.di import Provide, ServiceContainer, SingletonProvider, FactoryProvider
from app.services import DatabaseService, AuthService, CacheService
from app.config import settings

# Service container setup
class AppContainer(ServiceContainer):
    database_service = SingletonProvider(DatabaseService)
    auth_service = SingletonProvider(AuthService)
    cache_service = SingletonProvider(CacheService)

container = AppContainer()

# Dependency providers
def get_database() -> DatabaseService:
    """Get database service instance."""
    return container.database_service

def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    return container.auth_service

def get_cache() -> CacheService:
    """Get cache service instance."""
    return container.cache_service

# Usage in routers
DatabaseDep = Provide[container.database_service]
AuthDep = Provide[container.auth_service]
CacheDep = Provide[container.cache_service]
```

## 🧪 Testing Structure

### Test Organization

```python title="tests/conftest.py"
"""Pytest configuration and fixtures."""

import pytest
import httpx
from app.main import create_app
from app.services.database import DatabaseService

@pytest.fixture
def app():
    """Create test application."""
    return create_app()

@pytest.fixture
async def client(app):
    """Create test client using httpx."""
    # Note: Velithon doesn't have a built-in TestClient
    # Use httpx for testing HTTP endpoints
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def db_service():
    """Create test database service."""
    return DatabaseService()

@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    return {"Authorization": "Bearer test-token"}
```

```python title="tests/test_routers/test_tasks.py"
"""Test task router endpoints."""

import pytest
import httpx
from app.models.tasks import TaskCreate

@pytest.mark.asyncio
async def test_create_task(client: httpx.AsyncClient, auth_headers: dict):
    """Test task creation."""
    task_data = {
        "title": "Test Task", 
        "description": "Test Description",
        "priority": "high"
    }
    
    response = await client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_tasks(client: httpx.AsyncClient, auth_headers: dict):
    """Test getting tasks."""
    response = await client.get("/api/v1/tasks/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "count" in data
```

## 🚀 Deployment Structure

### Docker Configuration

```dockerfile title="Dockerfile"
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["velithon", "run", "--app", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml title="docker-compose.yml"
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/velithon
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: velithon
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 📦 Package Management

### Requirements Files

```txt title="requirements.txt"
# Core framework
velithon>=0.6.0

# Database
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0

# Cache
redis>=5.0.0

# Security
passlib>=1.7.4
python-jose>=3.3.0
bcrypt>=4.1.0

# Utilities
python-multipart>=0.0.20
python-dotenv>=1.0.0
```

```txt title="requirements-dev.txt"
# Include production requirements
-r requirements.txt

# Development tools
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.8.0
pre-commit>=3.6.0
```

## 🔄 Best Practices

### 1. Import Organization

```python
# Standard library imports
import os
import sys
from typing import List, Optional

# Third-party imports
from pydantic import BaseModel
from velithon import Velithon
from velithon.responses import JSONResponse

# Local imports
from app.config import settings
from app.models import User
from app.services import DatabaseService
```

### 2. Error Handling

```python title="app/exceptions.py"
"""Custom exceptions and error handling."""

from velithon.responses import JSONResponse
from velithon.exceptions import HTTPException

class TaskNotFoundError(HTTPException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=404,
            detail=f"Task with id {task_id} not found"
        )

# Error handling should be done in your route handlers
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    try:
        task = get_task_from_db(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task
    except TaskNotFoundError as exc:
        return JSONResponse(
            content={"error": exc.detail},
            status_code=exc.status_code
        )
```
```

### 3. Environment Configuration

```bash title=".env"
# Application
PROJECT_NAME="Velithon Task API"
VERSION="1.0.0"
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:pass@localhost/velithon

# Redis
REDIS_URL=redis://localhost:6379

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://myapp.com"]
```

## 📚 Summary

A well-organized Velithon project should have:

- ✅ **Clear separation** of concerns (models, routers, services)
- ✅ **Dependency injection** for loose coupling
- ✅ **Configuration management** with environment variables  
- ✅ **Comprehensive testing** structure
- ✅ **Docker support** for deployment
- ✅ **Proper error handling** and logging
- ✅ **Type hints** throughout the codebase

This structure scales from small APIs to large enterprise applications while maintaining code quality and team productivity.

**[Learn Core Concepts →](../user-guide/core-concepts.md)**
