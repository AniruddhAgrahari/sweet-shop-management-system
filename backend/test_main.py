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
    # 1. Login as Admin
    client.post("/auth/register", json={"username": "admin_create", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_create", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 2. Create Sweet
    response = client.post(
        "/sweets/",
        json={"name": "Wonka Bar", "category": "Chocolate", "price": 5.0, "quantity": 100},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Wonka Bar"
    assert "id" in data

def test_read_sweets(client):
    # 1. Login as Admin to create sweet
    client.post("/auth/register", json={"username": "admin_read", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_read", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 2. Create a sweet first
    client.post(
        "/sweets/",
        json={"name": "Test Sweet", "category": "Test", "price": 1.0, "quantity": 10},
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.get("/sweets/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_sweet(client):
    # 1. Login as Admin
    client.post("/auth/register", json={"username": "admin_update", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_update", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 2. Create sweet
    create_res = client.post(
        "/sweets/",
        json={"name": "Update Test", "price": 10.0, "quantity": 5, "category": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    sweet_id = create_res.json()["id"]

    # 3. Update it
    update_res = client.put(
        f"/sweets/{sweet_id}",
        json={"name": "Update Test", "price": 50.0, "quantity": 5, "category": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["price"] == 50.0

def test_delete_sweet(client):
    # 1. Create Admin User & Login
    client.post("/auth/register", json={"username": "admin_delete", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_delete", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 2. Create sweet (using token)
    create_res = client.post(
        "/sweets/",
        json={"name": "Delete Test", "price": 10.0, "quantity": 5, "category": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    sweet_id = create_res.json()["id"]

    # 3. Delete it (with token)
    delete_res = client.delete(
        f"/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_res.status_code == 200

    # 4. Verify it's gone
    get_res = client.get(f"/sweets/{sweet_id}")
    assert get_res.status_code == 404

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    # Ensure the password saved in DB is NOT "secret123" (it should be hashed)
    assert data["password_hash"] != "secret123"


def test_login_user(client):
    # 1. Register a user first
    client.post(
        "/auth/register",
        json={"username": "loginuser", "password": "password123"}
    )

    # 2. Login with correct credentials (form data, not json!)
    response = client.post(
        "/auth/login",
        data={"username": "loginuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_purchase_sweet(client):
    # 1. Login as Admin
    client.post("/auth/register", json={"username": "admin_purchase", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_purchase", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 2. Create sweet
    create_res = client.post(
        "/sweets/",
        json={"name": "Purchase Test", "price": 2.0, "quantity": 5, "category": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    sweet_id = create_res.json()["id"]

    # 3. Purchase one
    purchase_res = client.post(f"/sweets/{sweet_id}/purchase")
    assert purchase_res.status_code == 200
    assert purchase_res.json()["remaining_stock"] == 4

    # 4. Verify stock in DB
    get_res = client.get(f"/sweets/{sweet_id}")
    assert get_res.json()["quantity"] == 4

def test_purchase_out_of_stock(client):
    # 1. Login as Admin
    client.post("/auth/register", json={"username": "admin_empty", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_empty", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 2. Create sweet with 0 quantity
    create_res = client.post(
        "/sweets/",
        json={"name": "Empty Test", "price": 2.0, "quantity": 0, "category": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    sweet_id = create_res.json()["id"]

    # 3. Try to purchase
    purchase_res = client.post(f"/sweets/{sweet_id}/purchase")
    assert purchase_res.status_code == 400
    assert purchase_res.json()["detail"] == "Out of stock"

def test_search_sweets(client):
    # 1. Login as Admin
    client.post("/auth/register", json={"username": "admin_search", "password": "adminpass", "role": "admin"})
    login_res = client.post("/auth/login", data={"username": "admin_search", "password": "adminpass"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create specific sweets for testing
    client.post("/sweets/", json={"name": "Jelly Bean Mix", "category": "Jelly", "price": 2.50, "quantity": 50}, headers=headers)
    client.post("/sweets/", json={"name": "Gummy Bear", "category": "Gummy", "price": 4.00, "quantity": 50}, headers=headers)
    client.post("/sweets/", json={"name": "Chocolate Bar", "category": "Chocolate", "price": 8.00, "quantity": 50}, headers=headers)

    # Test 1: Search by name (partial match)
    response_name = client.get("/sweets/search?name=jelly")
    assert response_name.status_code == 200
    assert len(response_name.json()) == 1
    assert response_name.json()[0]["name"] == "Jelly Bean Mix"

    # Test 2: Search by price range (min_price)
    response_price_min = client.get("/sweets/search?min_price=5.0")
    assert response_price_min.status_code == 200
    assert len(response_price_min.json()) == 1
    assert response_price_min.json()[0]["name"] == "Chocolate Bar"

    # Test 3: Search by category
    response_category = client.get("/sweets/search?category=gummy")
    assert response_category.status_code == 200
    assert len(response_category.json()) == 1
    assert response_category.json()[0]["name"] == "Gummy Bear"

def test_restock_sweet_admin_only(client):
    # 1. Create Admin User & Login (to create sweet)
    client.post("/auth/register", json={"username": "admin_restock", "password": "adminpass", "role": "admin"})
    admin_login = client.post("/auth/login", data={"username": "admin_restock", "password": "adminpass"})
    admin_token = admin_login.json()["access_token"]

    # 2. Create a sweet to restock
    create_res = client.post(
        "/sweets/", 
        json={"name": "Low Stock", "category": "Test", "price": 1.0, "quantity": 1},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    sweet_id = create_res.json()["id"]

    # 3. Register a regular user
    client.post("/auth/register", json={"username": "customer", "password": "custpass", "role": "customer"})
    
    # 4. Login as regular user to get token
    login_res = client.post("/auth/login", data={"username": "customer", "password": "custpass"})
    customer_token = login_res.json()["access_token"]

    # 5. Attempt Restock as CUSTOMER (Should Fail 403)
    customer_restock = client.post(
        f"/sweets/{sweet_id}/restock?quantity=10",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert customer_restock.status_code == 403 # Forbidden!
    
    # 6. Attempt Restock as ADMIN (Should Succeed 200)
    admin_restock = client.post(
        f"/sweets/{sweet_id}/restock?quantity=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_restock.status_code == 200
    assert admin_restock.json()["new_stock"] == 11
