"""
Extended test cases for Products API to improve code coverage.

These tests focus on error handling, edge cases, validation,
and comprehensive API functionality testing.
"""

from fastapi.testclient import TestClient


class TestProductValidation:
    """Test input validation and business rules."""
    
    def test_create_product_negative_price(self, client: TestClient):
        """Test that negative prices are rejected."""
        response = client.post(
            "/api/v1/products/",
            json={"name": "Invalid Product", "price": -10.99},
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("Price must be greater than 0" in str(error) for error in error_detail)
    
    def test_create_product_zero_price(self, client: TestClient):
        """Test that zero price is rejected."""
        response = client.post(
            "/api/v1/products/",
            json={"name": "Free Product", "price": 0},
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("Price must be greater than 0" in str(error) for error in error_detail)
    
    def test_create_product_missing_name(self, client: TestClient):
        """Test that missing name is rejected."""
        response = client.post(
            "/api/v1/products/",
            json={"price": 10.99},
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("name" in str(error).lower() for error in error_detail)
    
    def test_create_product_missing_price(self, client: TestClient):
        """Test that missing price is rejected."""
        response = client.post(
            "/api/v1/products/",
            json={"name": "Product Without Price"},
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("price" in str(error).lower() for error in error_detail)
    
    def test_create_product_duplicate_name(self, client: TestClient):
        """Test that duplicate product names are rejected."""
        # Create first product
        response1 = client.post(
            "/api/v1/products/",
            json={"name": "Unique Product", "price": 10.99},
        )
        assert response1.status_code == 201
        
        # Try to create second product with same name
        response2 = client.post(
            "/api/v1/products/",
            json={"name": "Unique Product", "price": 15.99},
        )
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
    
    def test_create_product_empty_name(self, client: TestClient):
        """Test that empty name is rejected."""
        response = client.post(
            "/api/v1/products/",
            json={"name": "", "price": 10.99},
        )
        assert response.status_code == 422


class TestProductErrorHandling:
    """Test error handling for various scenarios."""
    
    def test_get_nonexistent_product(self, client: TestClient):
        """Test getting a product that doesn't exist."""
        response = client.get("/api/v1/products/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_nonexistent_product(self, client: TestClient):
        """Test updating a product that doesn't exist."""
        response = client.put(
            "/api/v1/products/99999",
            json={"name": "Updated Name", "price": 25.99},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_nonexistent_product(self, client: TestClient):
        """Test deleting a product that doesn't exist."""
        response = client.delete("/api/v1/products/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_invalid_product_id_format(self, client: TestClient):
        """Test using invalid product ID format."""
        response = client.get("/api/v1/products/invalid-id")
        assert response.status_code == 422
    
    def test_malformed_json_create(self, client: TestClient):
        """Test creating product with malformed JSON."""
        response = client.post(
            "/api/v1/products/",
            content='{"name": "Test", "price":}',  # Malformed JSON
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


class TestProductUpdateValidation:
    """Test update operation validation."""
    
    def test_update_product_negative_price(self, client: TestClient):
        """Test updating product with negative price."""
        # Create product first
        response = client.post(
            "/api/v1/products/",
            json={"name": "Test Product", "price": 10.99},
        )
        product_id = response.json()["id"]
        
        # Try to update with negative price
        response = client.put(
            f"/api/v1/products/{product_id}",
            json={"price": -5.99},
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("Price must be greater than 0" in str(error) for error in error_detail)
    
    def test_update_product_partial(self, client: TestClient):
        """Test partial update of product."""
        # Create product first
        response = client.post(
            "/api/v1/products/",
            json={"name": "Original Product", "description": "Original desc", "price": 10.99},
        )
        product_id = response.json()["id"]
        
        # Update only name
        response = client.put(
            f"/api/v1/products/{product_id}",
            json={"name": "Updated Product"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["description"] == "Original desc"  # Should remain unchanged
        assert data["price"] == 10.99  # Should remain unchanged


class TestProductPagination:
    """Test pagination and query parameters."""
    
    def test_get_products_with_pagination(self, client: TestClient):
        """Test products list with pagination parameters."""
        # Create multiple products
        for i in range(5):
            client.post(
                "/api/v1/products/",
                json={"name": f"Product {i}", "price": 10.0 + i},
            )
        
        # Test with limit
        response = client.get("/api/v1/products/?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Test with skip
        response = client.get("/api/v1/products/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_products_invalid_pagination(self, client: TestClient):
        """Test products list with invalid pagination parameters."""
        # Test with negative skip
        response = client.get("/api/v1/products/?skip=-1")
        assert response.status_code == 422
        
        # Test with negative limit
        response = client.get("/api/v1/products/?limit=-1")
        assert response.status_code == 422
    
    def test_get_products_empty_result(self, client: TestClient):
        """Test getting products when none exist."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestProductResponseStructure:
    """Test API response structure and content."""
    
    def test_create_product_response_structure(self, client: TestClient):
        """Test that create response has correct structure."""
        response = client.post(
            "/api/v1/products/",
            json={"name": "Test Product", "description": "Test desc", "price": 19.99},
        )
        assert response.status_code == 201
        data = response.json()
        
        # Check required fields
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "price" in data
        
        # Check data types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["price"], float)
        assert data["description"] is None or isinstance(data["description"], str)
        
        # Check values
        assert data["name"] == "Test Product"
        assert data["description"] == "Test desc"
        assert data["price"] == 19.99
    
    def test_get_product_response_structure(self, client: TestClient):
        """Test that get response has correct structure."""
        # Create product first
        create_response = client.post(
            "/api/v1/products/",
            json={"name": "Test Product", "price": 19.99},
        )
        product_id = create_response.json()["id"]
        
        # Get the product
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure matches create response
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "price" in data
        assert data["id"] == product_id


class TestProductBusinessLogic:
    """Test business logic and service layer functionality."""
    
    def test_product_name_uniqueness_case_sensitive(self, client: TestClient):
        """Test that product name uniqueness is case-sensitive."""
        # Create product with lowercase name
        response1 = client.post(
            "/api/v1/products/",
            json={"name": "test product", "price": 10.99},
        )
        assert response1.status_code == 201
        
        # Try to create product with uppercase name (should succeed)
        response2 = client.post(
            "/api/v1/products/",
            json={"name": "TEST PRODUCT", "price": 15.99},
        )
        assert response2.status_code == 201
    
    def test_product_description_optional(self, client: TestClient):
        """Test that description is optional."""
        response = client.post(
            "/api/v1/products/",
            json={"name": "Product Without Description", "price": 10.99},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None
    
    def test_product_update_preserves_unspecified_fields(self, client: TestClient):
        """Test that update preserves fields not specified in request."""
        # Create product with all fields
        response = client.post(
            "/api/v1/products/",
            json={"name": "Original", "description": "Original desc", "price": 10.99},
        )
        product_id = response.json()["id"]
        
        # Update only description
        response = client.put(
            f"/api/v1/products/{product_id}",
            json={"description": "Updated desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Original"  # Should be preserved
        assert data["description"] == "Updated desc"  # Should be updated
        assert data["price"] == 10.99  # Should be preserved


class TestAPIEndpoints:
    """Test various API endpoint behaviors."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_invalid_endpoint(self, client: TestClient):
        """Test accessing invalid endpoint."""
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test using wrong HTTP method."""
        response = client.patch("/api/v1/products/1")  # PATCH not implemented
        assert response.status_code == 405
