import requests

# Register a test user
response = requests.post(
    "http://127.0.0.1:8000/auth/register",
    json={"username": "loginuser", "password": "password123"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
