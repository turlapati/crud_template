# Architecture Documentation

## Overview

This FastAPI CRUD template features **dual CRUD implementations** - both SQLAlchemy ORM and raw SQL template approaches. The application follows clean architecture principles with clear separation of concerns, allowing seamless switching between CRUD implementations via environment variables.

## Project Structure

```
crud_template/
├── app/
│   ├── api/                        # API layer
│   │   ├── deps.py                 # Dependency injection
│   │   └── v1/                     # API version 1
│   │       ├── api.py              # Main API router
│   │       └── routers/            # Individual route handlers
│   │           └── products.py
│   ├── core/                       # Core configuration
│   │   └── config.py               # Application settings
│   ├── crud/                       # Data access layer (dual implementation)
│   │   ├── base.py                 # Generic ORM CRUD operations
│   │   ├── template_base.py        # Generic template CRUD operations
│   │   ├── crud_product.py         # Product ORM CRUD
│   │   └── template_crud_product.py # Product template CRUD
│   ├── db/                         # Database configuration
│   │   ├── base.py                 # SQLAlchemy base and model imports
│   │   └── session.py              # Database session management
│   ├── models/                     # SQLAlchemy models
│   │   └── product.py              # Product model definition
│   ├── schemas/                    # Pydantic schemas
│   │   └── product.py              # Product request/response schemas
│   ├── services/                   # Business logic layer
│   │   └── product_service.py      # Product business logic
│   └── main.py                     # FastAPI application entry point
├── tests/                          # Test suite
├── docs/                           # Documentation
└── requirements files              # Dependencies
```

## Architecture Layers

### 1. API Layer (`app/api/`)
- **Purpose**: HTTP request/response handling
- **Components**:
  - Route handlers in `routers/`
  - Dependency injection in `deps.py`
  - API versioning support

### 2. Service Layer (`app/services/`)
- **Purpose**: Business logic and validation
- **Responsibilities**:
  - Complex business rules
  - Cross-cutting concerns
  - Service orchestration
  - Error handling with proper HTTP status codes

### 3. CRUD Layer (`app/crud/`) - Dual Implementation
- **Purpose**: Data access abstraction with two approaches
- **ORM Implementation** (`base.py`, `crud_product.py`):
  - SQLAlchemy ORM-based operations
  - Type-safe model interactions
  - Automatic relationship handling
- **Template Implementation** (`template_base.py`, `template_crud_product.py`):
  - Raw SQL with parameterized queries
  - Direct database control
  - Performance optimization potential
- **Switching**: Use `CRUD_IMPL` environment variable (`"orm"` or `"template"`)

### 4. Model Layer (`app/models/`)
- **Purpose**: Data structure definition
- **Components**:
  - SQLAlchemy ORM models
  - Database table definitions
  - Relationships and constraints

### 5. Schema Layer (`app/schemas/`)
- **Purpose**: Data validation and serialization
- **Components**:
  - Pydantic models for request/response
  - Data validation rules
  - API documentation generation

## Key Design Patterns

### 1. Dependency Injection
- FastAPI's dependency system used throughout
- Database sessions injected via `get_db()`
- Services injected via `get_product_service()`

### 2. Repository Pattern
- CRUD classes abstract database operations
- Generic base class for common operations
- Model-specific extensions for custom queries

### 3. Service Layer Pattern
- Business logic separated from API handlers
- Centralized error handling
- Reusable business operations

### 4. Schema Separation
- Clear separation between internal models and API schemas
- Request/response validation
- Automatic API documentation

## Database Design

### Current Schema
- **Products Table**:
  - `id`: Primary key (Integer, auto-increment)
  - `name`: Product name (String, 100 chars, indexed, not null)
  - `description`: Product description (String, 255 chars, nullable)
  - `price`: Product price (Float, not null)

### Database Configuration
- SQLite for development (configurable via `DATABASE_URL`)
- SQLAlchemy ORM with declarative base
- Automatic table creation on startup
- Connection pooling and session management

## API Design

### RESTful Endpoints
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/` - List products (with pagination)
- `GET /api/v1/products/{id}` - Get specific product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Response Patterns
- Consistent JSON responses
- Proper HTTP status codes
- Error responses with detail messages
- Pagination support for list endpoints

## Configuration Management

### Settings System
- Pydantic Settings for configuration
- Environment variable support
- `.env` file loading
- Validation and type checking
- Default values for development

### Key Configuration Areas
- Database connection
- CORS settings (prepared for frontend)
- Security settings (JWT ready)
- API versioning

## Testing Strategy

### Test Structure
- Pytest framework
- FastAPI TestClient for integration tests
- Isolated test database
- Fixture-based test data setup

### Test Coverage Areas
- API endpoint testing
- CRUD operations
- Business logic validation
- Error handling scenarios

## Code Quality and Resolved Issues

### Issues Addressed During Development

#### Critical Bug Fixes
- **Method Name Mismatch**: Fixed service layer calling incorrect CRUD method (`get_by_name` vs `find_by_name`)
- **Database Connection Management**: Made connection args conditional based on database type for better portability
- **Error Handling**: Added existence checks in CRUD operations to prevent AttributeErrors
- **Input Validation**: Added price validation to prevent negative values
- **Test Isolation**: Implemented proper test isolation using temporary SQLite files

### Code Quality Assessment

#### Strengths
- **Clean Architecture**: Well-separated concerns with clear layer boundaries
- **Type Safety**: Comprehensive type annotations throughout
- **Modern Python**: Uses current best practices (Pydantic v2, SQLAlchemy 2.0)
- **Testing**: Comprehensive test coverage with proper isolation
- **Configuration**: Robust settings management with validation
- **Documentation**: Good docstrings and comprehensive project documentation

#### Maintainability Score: 8/10
- Clear project structure and consistent naming conventions
- Good separation of concerns and comprehensive tests
- Type safety and modern Python practices
- Areas for future enhancement clearly identified

## Security Considerations

### Current Implementation
- Basic input validation via Pydantic
- SQL injection protection via SQLAlchemy ORM
- Prepared for JWT authentication

### Future Security Enhancements
- Authentication middleware
- Authorization controls
- Rate limiting
- Input sanitization
- CORS configuration
