import pytest
from httpx import AsyncClient
import uuid

def random_email():
    return f"test_{uuid.uuid4()}@example.com"

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    email = random_email()
    response = client.post("/auth/register", json={
        "email": email,
        "password": "strongpassword123",
        "username": f"user_{uuid.uuid4()}"
    })
    
    assert response.status_code == 201
    assert response.json()["email"] == email


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    email = random_email()
    user_data = {
        "email": email,
        "password": "123",
        "username": f"user_{uuid.uuid4()}"
    }
    
    res1 = client.post("/auth/register", json=user_data)
    assert res1.status_code == 201
    
    res2 = client.post("/auth/register", json=user_data)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already registered."



@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):

    email = random_email()
    password = "mypassword"
    username = f"user_{uuid.uuid4()}"
    
    client.post("/auth/register", json={
        "email": email, "password": password, "username": username
    })
    
    response = client.post("/auth/token", data={
        "username": email,
        "password": password
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"