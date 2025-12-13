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