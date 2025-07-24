from fastapi.testclient import TestClient


def test_create_product(client: TestClient):
    response = client.post(
        "/api/v1/products/",
        json={"name": "Test Product", "description": "A test product", "price": 9.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert "id" in data


def test_read_product(client: TestClient):
    # First create a product to read
    response = client.post(
        "/api/v1/products/",
        json={"name": "Another Product", "description": "Another test", "price": 19.99},
    )
    product_id = response.json()["id"]

    # Now read it
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Another Product"
    assert data["id"] == product_id


def test_read_all_products(client: TestClient):
    client.post("/api/v1/products/", json={"name": "Prod 1", "price": 10})
    client.post("/api/v1/products/", json={"name": "Prod 2", "price": 20})

    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_update_product(client: TestClient):
    response = client.post("/api/v1/products/", json={"name": "Original Name", "price": 50})
    product_id = response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 50  # Price should be unchanged


def test_update_product_with_invalid_data(client: TestClient):
    """Test updating a product with invalid data (null values for required fields)."""
    # First create a product
    response = client.post("/api/v1/products/", json={"name": "Test Product", "price": 100})
    product_id = response.json()["id"]
    
    # Try to update with null name - should return 422
    response = client.put(
        f"/api/v1/products/{product_id}",
        json={"name": None, "description": "Name set to null"},
    )
    assert response.status_code == 422
    assert "Required field 'name' cannot be null or empty" in response.json()["detail"]
    
    # Try to update with null price - should return 422
    response = client.put(
        f"/api/v1/products/{product_id}",
        json={"description": "Price set to null", "price": None},
    )
    assert response.status_code == 422
    assert "Required field 'price' cannot be null or empty" in response.json()["detail"]


def test_delete_product(client: TestClient):
    response = client.post("/api/v1/products/", json={"name": "To Be Deleted", "price": 1})
    product_id = response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 200

    # Verify it's gone
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 404