import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.product import Product
from app.db.base import Base

def test_simple_db_access(client: TestClient, db_session: Session):
    """Test that we can access the database and that the tables are created."""
    # Get the project root directory (parent of tests directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "test_output.txt")
    
    # Open a file to write the output to
    with open(output_file, "w") as f:
        # Write information about the database session
        f.write(f"Database session: {db_session}\n")
        f.write(f"Database session engine: {db_session.bind}\n")
        
        # Write information about the Base class
        f.write(f"Base class: {Base}\n")
        f.write(f"Base metadata: {Base.metadata}\n")
        f.write(f"Base metadata tables: {Base.metadata.tables.keys()}\n")
        
        # Check if the tables are created
        tables = db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        table_names = [table[0] for table in tables]
        f.write(f"Tables in the database: {table_names}\n")
        assert "products" in table_names
        
        # Try to insert a record into the products table
        product = Product(name="Test Product", description="A test product", price=9.99)
        db_session.add(product)
        db_session.commit()
        
        # Verify that the record was inserted
        products = db_session.query(Product).all()
        f.write(f"Products in the database: {products}\n")
        f.write(f"Product 1 name: {products[0].name}\n")
        assert len(products) == 1
        assert products[0].name == "Test Product"
        
        try:
            # Try to use the FastAPI test client to make a request to the API endpoint
            f.write("Making request to API endpoint...\n")
            response = client.post(
                "/api/v1/products/",
                json={"name": "Test Product 2", "description": "Another test product", "price": 19.99},
            )
            f.write(f"Response status code: {response.status_code}\n")
            f.write(f"Response body: {response.text}\n")
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Product 2"
            assert "id" in data
        except Exception as e:
            f.write(f"Exception: {e}\n")
            import traceback
            f.write(traceback.format_exc())
            raise