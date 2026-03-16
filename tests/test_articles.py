import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_post_as_editor_success(editor_token, client):
    payload = {
        "title": "Тестовая статья 2025",
        "content": "<p>Это проверочный контент статьи.</p>",
        "status": "draft",
        "categories": [],
        "tags": [],
    }

    response = client.post(
        "/posts", json=payload, headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["title"] == payload["title"]
    assert data["status"] == "draft"
    assert "id" in data
    assert "slug" in data
    assert isinstance(data["id"], int)


@pytest.mark.asyncio
async def test_create_post_unauth(client):
    payload = {"title": "Без авторизации", "content": "текст", "status": "draft"}
    response = client.post("/posts", json=payload)
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_create_post_as_viewer_forbidden(viewer_token, client):
    payload = {"title": "Запрещено", "content": "..."}

    response = client.post(
        "/posts", json=payload, headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_get_single_post_by_id(editor_token, test_post, client):
    response = client.get(
        f"/posts/{test_post.id}", headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == test_post.id
    assert "title" in data
    assert "content" in data


@pytest.mark.asyncio
async def test_get_nonexist_post(editor_token, client):
    response = client.get(
        "/posts/66666", headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert response.status_code == 404, response.text
