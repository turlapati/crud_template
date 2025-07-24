import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path to allow absolute imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import app modules after path setup
# This is the crucial part: import all models to ensure they are registered on the Base metadata
# before any tables are created.
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import product  # noqa: E402


@pytest.fixture(scope="function")
def db_session():
    """Fixture to create a test database session.
    
    Each test gets a fresh database with all tables created.
    """
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)  # Close the file descriptor, we only need the path
    
    try:
        # Create engine with the temporary database
        test_database_url = f"sqlite:///{db_path}"
        engine = create_engine(test_database_url, connect_args={"check_same_thread": False})
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create session factory
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create a new session
        db = TestingSessionLocal()
        
        try:
            yield db
        finally:
            db.close()
            engine.dispose()
    finally:
        # Clean up the temporary database file
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture to create a TestClient with the database dependency overridden.
    
    Each test gets a fresh TestClient with its own isolated database session.
    """
    def override_get_db():
        """Override the get_db dependency to use the test database session."""
        try:
            yield db_session
        finally:
            # Session cleanup is handled by the db_session fixture
            pass

    # Override the database dependency for testing
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    test_client = TestClient(app)
    
    try:
        yield test_client
    finally:
        # Clean up dependency overrides
        del app.dependency_overrides[get_db]