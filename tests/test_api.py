import pytest
from httpx import AsyncClient

# Helper to create user and get token
async def create_user_and_login(client: AsyncClient, email: str, password: str):
    username = email.split("@")[0]
    response = await client.post("/api/v1/register", json={"email": email, "password": password, "username": username})
    assert response.status_code == 201
    
    login_res = await client.post("/api/v1/login/access-token", data={"username": username, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return token

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    token = await create_user_and_login(client, "test@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.post(
        "/api/v1/tasks/",
        json={"title": "Test Task", "priority": "high"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert "id" in data

@pytest.mark.asyncio
async def test_read_tasks_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_own_task(client: AsyncClient):
    # User 1
    token = await create_user_and_login(client, "user1@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create
    res = await client.post("/api/v1/tasks/", json={"title": "Task 1"}, headers=headers)
    assert res.status_code == 201
    task_id = res.json()["id"]
    
    # Update
    res = await client.put(f"/api/v1/tasks/{task_id}", json={"title": "Updated Task 1"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Task 1"

@pytest.mark.asyncio
async def test_update_other_user_task_forbidden(client: AsyncClient):
    # User A creates task
    token_a = await create_user_and_login(client, "usera@example.com", "password123")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res = await client.post("/api/v1/tasks/", json={"title": "Users A Task"}, headers=headers_a)
    assert res.status_code == 201
    task_id = res.json()["id"]
    
    # User B tries to update
    token_b = await create_user_and_login(client, "userb@example.com", "password123")
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    res = await client.put(f"/api/v1/tasks/{task_id}", json={"title": "Hacked"}, headers=headers_b)
    assert res.status_code == 403
