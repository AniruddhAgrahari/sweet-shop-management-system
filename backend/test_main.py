# Import client from conftest (actually pytest handles this automatically, just pass client as arg)

# Define test_create_sweet(client):
#   Post to /sweets/ with name="Test", price=1.0, quantity=10, category="Test"
#   Assert 200 OK and data["name"] == "Test"

def test_create_sweet(client):
    response = client.post(
        "/sweets/",
        json={"name": "Test", "price": 1.0, "quantity": 10, "category": "Test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"

# Define test_read_sweets(client):
#   Post a sweet first
#   Get /sweets/
#   Assert 200 OK and len(response.json()) > 0

def test_read_sweets(client):
    client.post(
        "/sweets/",
        json={"name": "Test", "price": 1.0, "quantity": 10, "category": "Test"}
    )
    response = client.get("/sweets/")
    assert response.status_code == 200
    assert len(response.json()) > 0