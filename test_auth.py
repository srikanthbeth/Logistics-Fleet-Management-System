# ==========================================
# Authentication Tests
# ==========================================

import uuid


# ==========================================
# Helper - Create Unique User Data
# ==========================================

def create_user_data():

    unique_id = uuid.uuid4().hex[:8]

    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "Test@12345",
        "role": "Driver"
    }


# ==========================================
# 1. Register User
# ==========================================

def test_register_user(client):

    user_data = create_user_data()

    response = client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]


# ==========================================
# 2. Duplicate Username
# ==========================================

def test_duplicate_username(client):

    user_data = create_user_data()

    first_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201

    duplicate_data = {
        "username": user_data["username"],
        "email": f"another_{uuid.uuid4().hex[:8]}@example.com",
        "password": "Test@12345",
        "role": "Driver"
    }

    second_response = client.post(
        "/auth/register",
        json=duplicate_data
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["success"] is False
    assert data["detail"] == "Username already exists"


# ==========================================
# 3. Duplicate Email
# ==========================================

def test_duplicate_email(client):

    user_data = create_user_data()

    first_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201

    duplicate_data = {
        "username": f"another_{uuid.uuid4().hex[:8]}",
        "email": user_data["email"],
        "password": "Test@12345",
        "role": "Driver"
    }

    second_response = client.post(
        "/auth/register",
        json=duplicate_data
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["success"] is False
    assert data["detail"] == "Email already exists"


# ==========================================
# 4. Invalid Role
# ==========================================

def test_invalid_role(client):

    user_data = create_user_data()

    user_data["username"] = f"invalidrole_{uuid.uuid4().hex[:8]}"
    user_data["email"] = f"invalidrole_{uuid.uuid4().hex[:8]}@example.com"
    user_data["role"] = "Customer"

    response = client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert "Invalid role" in data["detail"]


# ==========================================
# 5. Login Success
# ==========================================

def test_login_success(client):

    user_data = create_user_data()

    register_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


# ==========================================
# 6. Wrong Password
# ==========================================

def test_login_wrong_password(client):

    user_data = create_user_data()

    register_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": "WrongPassword@123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Invalid username or password"


# ==========================================
# 7. Nonexistent User
# ==========================================

def test_login_nonexistent_user(client):

    response = client.post(
        "/auth/login",
        json={
            "username": f"notfound_{uuid.uuid4().hex[:8]}",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Invalid username or password"


# ==========================================
# 8. Current User Without Token
# ==========================================

def test_current_user_without_token(client):

    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401


# ==========================================
# 9. Current User With Valid Token
# ==========================================

def test_current_user_with_valid_token(client):

    user_data = create_user_data()

    register_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]


# ==========================================
# 10. Invalid Token
# ==========================================

def test_current_user_invalid_token(client):

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401