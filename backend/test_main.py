# Import FastAPI, Depends, and HTTPException
from fastapi import FastAPI, Depends, HTTPException
from main import app

# We don't need to create a client here because the fixture in conftest.py handles it,
# but we import it to keep the linter happy if needed.

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Sweet Shop API"}

def test_create_sweet(client):
    response = client.post(
        "/sweets/",
        json={"name": "Wonka Bar", "category": "Chocolate", "price": 5.0, "quantity": 100}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Wonka Bar"
    assert "id" in data

def test_read_sweets(client):
    # Create a sweet first
    client.post(
        "/sweets/",
        json={"name": "Test Sweet", "category": "Test", "price": 1.0, "quantity": 10}
    )
    response = client.get("/sweets/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_sweet(client):
    # 1. Create sweet
    create_res = client.post(
        "/sweets/",
        json={"name": "Update Test", "price": 10.0, "quantity": 5, "category": "Test"}
    )
    sweet_id = create_res.json()["id"]

    # 2. Update it
    update_res = client.put(
        f"/sweets/{sweet_id}",
        json={"name": "Update Test", "price": 50.0, "quantity": 5, "category": "Test"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["price"] == 50.0

def test_delete_sweet(client):
    # 1. Create sweet
    create_res = client.post(
        "/sweets/",
        json={"name": "Delete Test", "price": 10.0, "quantity": 5, "category": "Test"}
    )
    sweet_id = create_res.json()["id"]

    # 2. Delete it
    delete_res = client.delete(f"/sweets/{sweet_id}")
    assert delete_res.status_code == 200

    # 3. Verify it's gone
    get_res = client.get(f"/sweets/{sweet_id}")
    assert get_res.status_code == 404