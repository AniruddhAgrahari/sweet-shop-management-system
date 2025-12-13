from fastapi.testclient import TestClient
# We are importing 'app' from main, but main.py doesn't exist yet!
# This is intentional for TDD.
from main import app 

client = TestClient(app)

def test_read_root():
    """
    Test that the root endpoint returns a welcome message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Sweet Shop API"}

# Test creating a new sweet
# Send a POST request to "/sweets/" with json data: name="Wonka Bar", category="Chocolate", price=5.0, quantity=100
# Assert status code is 200 or 201
# Assert the returned json name is "Wonka Bar"