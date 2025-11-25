import pytest
import uuid
from httpx import AsyncClient
from app import redis_client
from app.crypto import decrypt_text

from app.models import Note
from sqlmodel import select

from sqlmodel.ext.asyncio.session import AsyncSession

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
async def test_search_pagination_limit(client: AsyncClient):
    headers = await get_auth_headers(client)
    unique_tag = f"pagetest_{uuid.uuid4()}"

    for i in range(15):
        await client.post(
            "/notes/", 
            json={"title": f"{unique_tag} Note {i}", "content": "...", "is_public": True},
            headers=headers
        )
    
    res_limit = await client.get("/notes/search", params={"q": unique_tag, "limit": 5}, headers=headers)
    assert res_limit.status_code == 200
    assert len(res_limit.json()) == 5
    
    res_offset = await client.get("/notes/search", params={"q": unique_tag, "offset": 10}, headers=headers)
    assert len(res_offset.json()) == 5
    
    res_abuse = await client.get("/notes/search", params={"q": unique_tag, "limit": 1000}, headers=headers)
    assert res_abuse.status_code == 200
    assert len(res_abuse.json()) <= 200



@pytest.mark.asyncio
async def test_public_feed_caching(client: AsyncClient):
    headers = await get_auth_headers(client)
    redis = redis_client.get_redis_pool()
    CACHE_KEY = "public_notes_feed"

    await redis.delete(CACHE_KEY)

    await client.post(
        "/notes/", 
        json={"title": "Cache Test Note", "content": "...", "is_public": True}, 
        headers=headers
    )
    
    res1 = await client.get("/notes/public", headers=headers)
    assert res1.status_code == 200
    
    is_cached = await redis.exists(CACHE_KEY)
    assert is_cached == 1, "Public feed was not cached"

    await client.post(
        "/notes/", 
        json={"title": "New Note", "content": "...", "is_public": True}, 
        headers=headers
    )

    is_cached_after = await redis.exists(CACHE_KEY)
    assert is_cached_after == 0, "Cache was not deleted properly"
    
    
@pytest.mark.asyncio
async def test_encryption_at_rest(client: AsyncClient, session: AsyncSession):
    headers = await get_auth_headers(client)
    
    original_title = "Top Secret Title"
    original_content = "Bank password 123456"
    
    create_res = await client.post(
        "/notes/",
        json={"title": original_title, "content": original_content, "is_public": False},
        headers=headers
    )
    assert create_res.status_code == 201
    note_id = create_res.json()["id"]
    
    session.expire_all()

    statement = select(Note).where(Note.id == note_id)
    result = await session.exec(statement)
    db_note = result.first()

    assert db_note.title != original_title
    assert db_note.content != original_content
    
    assert decrypt_text(db_note.title) == original_title
    assert decrypt_text(db_note.content) == original_content

    print(f"\n🔒 Encrypted DB Data: {db_note.content[:15]}...")