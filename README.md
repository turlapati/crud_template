# FastAPI CRUD Template

A production-ready FastAPI template with **dual CRUD implementations** - both SQLAlchemy ORM and raw SQL template approaches. Switch between implementations using environment variables for performance comparison and learning.

## Key Features

- **Dual CRUD Implementation**: Switch between ORM and raw SQL via `CRUD_IMPL` environment variable
- **Clean Architecture**: Well-separated layers (API, Service, CRUD, Models)
- **Modern FastAPI**: Latest FastAPI with automatic API documentation
- **Type Safety**: Full type hints throughout the codebase
- **Database Integration**: SQLAlchemy ORM with SQLite (easily configurable)
- **Pydantic V2**: Modern validation and serialization with `model_dump()`
- **Comprehensive Testing**: 35 tests covering both CRUD implementations
- **Zero Warnings**: Clean codebase with no deprecation warnings
- **Production Ready**: Robust error handling and constraint management

## Prerequisites

- Python 3.12 or higher
- pip or uv package manager

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd crud_template

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# OR if using uv:
uv sync
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env  # Create this file if it doesn't exist

# Edit .env file with your settings
PROJECT_NAME="My CRUD API"
DATABASE_URL="sqlite:///./my_app.db"
```

### 3. Choose CRUD Implementation

This template supports two CRUD implementations:

```bash
# Use SQLAlchemy ORM (default)
export CRUD_IMPL="orm"
# OR
unset CRUD_IMPL

# Use raw SQL templates
export CRUD_IMPL="template"
```

### 4. Initialize the Database

```bash
# Initialize the database tables
python scripts/init_db.py
```

This will create all the necessary database tables. You only need to run this:
- When setting up the application for the first time
- After adding new models to the application
- After resetting the database

### 5. Run the Application

```bash
# Start the development server
uvicorn app.main:app --reload

# The API will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### 6. Test the API

```bash
# Run all tests (ORM implementation - default)
pytest

# Test template CRUD implementation
CRUD_IMPL="template" pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_products.py -v
```

**Test Results**: All 35 tests pass for both CRUD implementations with zero warnings.

## API Usage Examples

### Create a Product
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "description": "High-performance laptop",
       "price": 999.99
     }'
```

### Get All Products
```bash
curl "http://localhost:8000/api/v1/products/"
```

### Get Specific Product
```bash
curl "http://localhost:8000/api/v1/products/1"
```

### Update Product
```bash
curl -X PUT "http://localhost:8000/api/v1/products/1" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Laptop",
       "price": 899.99
     }'
```

### Delete Product
```bash
curl -X DELETE "http://localhost:8000/api/v1/products/1"
```

## Project Structure

```
crude_template/
├── app/
│   ├── api/                            # API layer
│   │   ├── deps.py                     # Dependencies
│   │   └── v1/                         # API version 1
│   │       ├── api.py                  # Main router
│   │       └── routers/                # Route handlers
│   ├── core/                           # Core configuration
│   │   └── config.py                   # Settings
│   ├── crud/                           # Data access layer (dual implementation)
│   │   ├── base.py                     # Generic ORM CRUD operations
│   │   ├── template_base.py            # Generic template CRUD operations
│   │   ├── crud_product.py             # Product ORM CRUD
│   │   └── template_crud_product.py    # Product template CRUD
│   ├── db/                             # Database setup
│   │   ├── base.py                     # SQLAlchemy base
│   │   └── session.py                  # DB sessions
│   ├── models/                         # Database models
│   │   └── product.py                  # Product model
│   ├── schemas/                        # Pydantic schemas
│   │   └── product.py                  # Product schemas
│   ├── services/                       # Business logic
│   │   └── product_service.py
│   └── main.py                         # FastAPI app
├── tests/                              # Test suite
├── docs/                               # Documentation
└── requirements.txt                    # Dependencies
```

## Customization Guide

### Adding a New Model

1. **Create the SQLAlchemy Model** (`app/models/your_model.py`):
```python
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
```

2. **Create Pydantic Schemas** (`app/schemas/your_model.py`):
```python
from pydantic import BaseModel
from typing import Optional

class YourModelBase(BaseModel):
    name: str

class YourModelCreate(YourModelBase):
    pass

class YourModelUpdate(YourModelBase):
    name: Optional[str] = None

class YourModel(YourModelBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

3. **Create CRUD Operations** (`app/crud/crud_your_model.py`):
```python
from app.crud.base import CRUDBase
from app.models.your_model import YourModel
from app.schemas.your_model import YourModelCreate, YourModelUpdate

class CRUDYourModel(CRUDBase[YourModel, YourModelCreate, YourModelUpdate]):
    pass

your_model = CRUDYourModel(YourModel)
```

4. **Create Service Layer** (`app/services/your_model_service.py`):
```python
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud import crud_your_model
from app.schemas.your_model import YourModelCreate, YourModelUpdate

class YourModelService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_item(self, item: YourModelCreate):
        return crud_your_model.your_model.create(self.db, obj_in=item)
    
    # Add other business logic methods...
```

5. **Create API Router** (`app/api/v1/routers/your_model.py`):
```python
from fastapi import APIRouter, Depends
from app.schemas.your_model import YourModel, YourModelCreate
from app.api import deps
from app.services.your_model_service import YourModelService

router = APIRouter()

@router.post("/", response_model=YourModel)
def create_item(item: YourModelCreate, service: YourModelService = Depends(deps.get_your_model_service)):
    return service.create_item(item)
```

6. **Register the Router** (`app/api/v1/api.py`):
```python
from .routers import your_model
api_router.include_router(your_model.router, prefix="/your-model", tags=["your-model"])
```

### Database Configuration

**SQLite (Default)**:
```env
DATABASE_URL=sqlite:///./app.db
```

**PostgreSQL**:
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

**MySQL**:
```env
DATABASE_URL=mysql://user:password@localhost/dbname
```

**Oracle**:
```env
DATABASE_URL=oracle://user:password@localhost:1521/xe
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_products.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Writing Tests
Tests are located in the `tests/` directory. The template includes:
- API endpoint tests
- Database operation tests
- Business logic tests

Example test:
```python
def test_create_product(client: TestClient):
    response = client.post(
        "/api/v1/products/",
        json={"name": "Test Product", "price": 9.99},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/architecture.md)**: Detailed architecture overview and code quality assessment
- **[Future Tasks](docs/future_tasks.md)**: Enhancement roadmap and improvement areas

## Production Deployment

### Environment Variables
Create a production `.env` file:
```env
PROJECT_NAME="Production API"
DATABASE_URL="postgresql://user:pass@db:5432/prod_db"
SECRET_KEY="your-secret-key-here"
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Server
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - The database toolkit
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation library
- [Pytest](https://pytest.org/) - Testing framework

---

**Happy coding!**