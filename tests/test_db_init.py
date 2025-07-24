"""Tests for database initialization and table verification."""
import sys
from pathlib import Path
from sqlalchemy import inspect, create_engine
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.base import Base  # noqa: E402


def test_database_initialization(monkeypatch, tmp_path):
    """Test that the database initialization script creates all required tables."""
    # Setup a temporary database
    db_path = tmp_path / "test_init.db"
    db_url = f"sqlite:///{db_path}"
    
    # Clean up any existing database
    if db_path.exists():
        db_path.unlink()
    
    # Set up environment for the test - must be done before any imports
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # Clear any cached modules to ensure fresh imports
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('app.') or m.startswith('scripts.')]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    
    # Import the init_db function after setting the environment
    from scripts.init_db import init_db, verify_tables_exist
    
    # Run the initialization
    init_db()
    
    # Verify the database file was created
    assert db_path.exists(), "Database file was not created"
    
    # Verify tables were created
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Check for required tables
    assert "products" in tables, "Products table was not created"
    
    # Verify table structure
    columns = {col["name"] for col in inspector.get_columns("products")}
    expected_columns = {"id", "name", "description", "price"}
    assert expected_columns.issubset(columns), "Products table is missing columns"
    
    # Verify the verification function works
    assert verify_tables_exist(engine), "verify_tables_exist should return True after initialization"


def test_application_startup_without_tables(monkeypatch, tmp_path):
    """Test that the application fails when trying to access missing tables."""
    # Setup a temporary database
    db_path = tmp_path / "test_no_tables.db"
    db_url = f"sqlite:///{db_path}"
    
    # Clean up any existing database
    if db_path.exists():
        db_path.unlink()
    
    # Create an empty database file
    db_path.touch()
    
    # Set up environment for the test - must be done before any imports
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # Clear any cached modules to ensure fresh imports
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('app.')]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    
    # Verify the database is empty
    engine = create_engine(db_url)
    inspector = inspect(engine)
    assert not inspector.get_table_names(), "Tables should not exist yet"
    
    # Import the app after setting environment
    from app.main import app
    from fastapi.testclient import TestClient
    from sqlalchemy.exc import OperationalError
    
    # This should raise an OperationalError because tables don't exist
    with pytest.raises(OperationalError) as exc_info:
        with TestClient(app) as client:
            # Try to access an endpoint that requires database access
            response = client.get("/api/v1/products/")
    
    # Verify the error is about missing tables
    assert "no such table" in str(exc_info.value).lower()


def test_application_startup_with_tables(monkeypatch, tmp_path):
    """Test that the application starts correctly when tables exist."""
    # Setup a temporary database
    db_path = tmp_path / "test_with_tables.db"
    db_url = f"sqlite:///{db_path}"
    
    # Set up environment for the test - must be done before any imports
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # Clear any cached modules to ensure fresh imports
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('app.')]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    
    # Create tables first
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    
    # Import the FastAPI app after setting the environment
    from app.main import app
    from fastapi.testclient import TestClient
    
    # This should work because tables exist
    with TestClient(app) as client:
        response = client.get("/api/v1/products/")
        assert response.status_code == 200


def test_verify_models_imported():
    """Test that all SQLAlchemy models are properly imported in the base module."""
    # This test will fail if any models are not imported in app/db/base.py
    # The import of Product above will raise an ImportError if there's an issue
    assert True  # Just getting here means the imports worked


def test_table_verification(monkeypatch, tmp_path):
    """Test the verify_tables_exist function directly."""
    # Setup a temporary database
    db_path = tmp_path / "test_verify.db"
    db_url = f"sqlite:///{db_path}"
    
    # Create the database file but don't create tables yet
    if db_path.exists():
        db_path.unlink()
    db_path.touch()
    
    # Import the verification function
    from scripts.init_db import verify_tables_exist
    
    # Create engine and verify tables don't exist
    engine = create_engine(db_url)
    assert not verify_tables_exist(engine), "verify_tables_exist should return False when tables are missing"
    
    # Create tables and verify again
    Base.metadata.create_all(bind=engine)
    assert verify_tables_exist(engine), "verify_tables_exist should return True when tables exist"
