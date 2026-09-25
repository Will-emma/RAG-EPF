import uuid

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    email = f"test-{uuid.uuid4()}@example.com"

    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    email = f"duplicate-{uuid.uuid4()}@example.com"

    payload = {
        "email": email,
        "password": "TestPassword123!",
    }

    first_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    second_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Un compte existe déjà avec cet email."

@pytest.mark.asyncio
async def test_login_success(client):
    email = f"login-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"

    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
 
 
 #Mauvais mot de passe   
@pytest.mark.asyncio
async def test_login_invalid_password(client):
    email = f"wrong-password-{uuid.uuid4()}@example.com"

    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "CorrectPassword123!",
        },
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Email ou mot de passe incorrect." 
    