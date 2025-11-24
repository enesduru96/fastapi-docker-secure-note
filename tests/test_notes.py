import pytest
from httpx import AsyncClient
import uuid


async def get_auth_headers(client: AsyncClient, username: str = None):
    if not username:
        username = f"user_{uuid.uuid4()}"

    email = f"{username}@{uuid.uuid4()}.com"
    password = "testpassword123"

    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "username": username},
    )

    response = await client.post(
        "/auth/token", data={"username": email, "password": password}
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_note(client: AsyncClient):
    headers = await get_auth_headers(client)

    payload = {
        "title": "Test title with PyTest",
        "content": "This note was created by PyTest.",
        "is_public": False,
    }

    response = await client.post("/notes/", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_read_my_notes(client: AsyncClient):
    headers = await get_auth_headers(client)

    await client.post(
        "/notes/",
        json={"title": "Note 1", "content": "A", "is_public": False},
        headers=headers,
    )
    await client.post(
        "/notes/",
        json={"title": "Note 2", "content": "B", "is_public": True},
        headers=headers,
    )

    response = await client.get("/notes/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Note 1"


@pytest.mark.asyncio
async def test_public_feed_privacy(client: AsyncClient):
    headers_a = await get_auth_headers(client, username="writer_user1")

    await client.post(
        "/notes/",
        json={"title": "Private Title", "content": "...", "is_public": False},
        headers=headers_a,
    )
    await client.post(
        "/notes/",
        json={"title": "Public Title", "content": "...", "is_public": True},
        headers=headers_a,
    )

    headers_b = await get_auth_headers(client, username="reader_user2")

    response = await client.get("/notes/public", headers=headers_b)

    assert response.status_code == 200
    data = response.json()

    titles = [note["title"] for note in data]
    assert "Public Title" in titles
    assert "Private Title" not in titles

    public_note = next(n for n in data if n["title"] == "Public Title")
    assert public_note["owner_username"] == "writer_user1"


@pytest.mark.asyncio
async def test_search_notes(client: AsyncClient):
    headers = await get_auth_headers(client)
    
    unique_keyword = f"search_term_{uuid.uuid4()}"
    
    await client.post(
        "/notes/", 
        json={
            "title": f"My {unique_keyword} Note", 
            "content": "Content here...", 
            "is_public": False
        }, 
        headers=headers
    )
    
    res1 = await client.get("/notes/search", params={"q": unique_keyword}, headers=headers)
    assert res1.status_code == 200
    assert len(res1.json()) > 0
    assert unique_keyword in res1.json()[0]["title"]
    
    res2 = await client.get("/notes/search", params={"q": "Some_Unrelated_Nonexistent_Content"}, headers=headers)
    assert res2.status_code == 200
    assert len(res2.json()) == 0