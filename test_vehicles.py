from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ============================================================
# Authentication Helper
# ============================================================

def get_auth_headers():
    """
    Register a test Admin user and return JWT authorization headers.
    """

    username = "vehicle_test_admin"
    email = "vehicle_test_admin@example.com"
    password = "Test@12345"

    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "role": "Admin"
    }

    register_response = client.post(
        "/auth/register",
        json=register_data
    )

    # User may already exist from a previous test run
    assert register_response.status_code in [201, 400], (
        register_response.text
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200, (
        login_response.text
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# Vehicle Test Data
# ============================================================

def vehicle_payload(
    vehicle_number="TEST-VH-001"
):
    return {
        "vehicle_number": vehicle_number,
        "vehicle_type": "Truck",
        "model": "Tata 407",
        "manufacturing_year": 2022,
        "current_km": 25000,
        "capacity": 5000,
        "status": "Available"
    }


# ============================================================
# 1. CREATE VEHICLE
# ============================================================

def test_create_vehicle():

    headers = get_auth_headers()

    response = client.post(
        "/vehicles",
        json=vehicle_payload(
            "TEST-VH-CREATE"
        ),
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["vehicle_number"] == "TEST-VH-CREATE"
    assert data["vehicle_type"] == "Truck"
    assert data["capacity"] == 5000


# ============================================================
# 2. DUPLICATE VEHICLE
# ============================================================

def test_duplicate_vehicle():

    headers = get_auth_headers()

    payload = vehicle_payload(
        "TEST-VH-DUPLICATE"
    )

    first_response = client.post(
        "/vehicles",
        json=payload,
        headers=headers
    )

    assert first_response.status_code in [
        201,
        400
    ], first_response.text

    second_response = client.post(
        "/vehicles",
        json=payload,
        headers=headers
    )

    assert second_response.status_code == 400, (
        second_response.text
    )

    data = second_response.json()

    assert data["success"] is False


# ============================================================
# 3. GET ALL VEHICLES
# ============================================================

def test_get_all_vehicles():

    headers = get_auth_headers()

    response = client.get(
        "/vehicles",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    # Pagination response
    assert "total_records" in data
    assert "current_page" in data
    assert "limit" in data
    assert "data" in data

    assert isinstance(
        data["data"],
        list
    )


# ============================================================
# 4. GET VEHICLE BY ID
# ============================================================

def test_get_vehicle_by_id():

    headers = get_auth_headers()

    create_response = client.post(
        "/vehicles",
        json=vehicle_payload(
            "TEST-VH-GET"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    vehicle_id = create_response.json()["id"]

    response = client.get(
        f"/vehicles/{vehicle_id}",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert data["id"] == vehicle_id
    assert data["vehicle_number"] == "TEST-VH-GET"


# ============================================================
# 5. VEHICLE NOT FOUND
# ============================================================

def test_vehicle_not_found():

    headers = get_auth_headers()

    response = client.get(
        "/vehicles/999999",
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False


# ============================================================
# 6. UPDATE VEHICLE
# ============================================================

def test_update_vehicle():

    headers = get_auth_headers()

    create_response = client.post(
        "/vehicles",
        json=vehicle_payload(
            "TEST-VH-UPDATE"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    vehicle_id = create_response.json()["id"]

    update_data = {
        "vehicle_type": "Van",
        "model": "Updated Model",
        "manufacturing_year": 2023,
        "current_km": 30000,
        "capacity": 6000,
        "status": "Available"
    }

    response = client.put(
        f"/vehicles/{vehicle_id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert data["id"] == vehicle_id
    assert data["vehicle_type"] == "Van"
    assert data["capacity"] == 6000


# ============================================================
# 7. INVALID VEHICLE STATUS
# ============================================================

def test_invalid_vehicle_status():

    headers = get_auth_headers()

    payload = vehicle_payload(
        "TEST-VH-INVALID-STATUS"
    )

    payload["status"] = "INVALID_STATUS"

    response = client.post(
        "/vehicles",
        json=payload,
        headers=headers
    )

    assert response.status_code == 422, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"
    assert "errors" in data


# ============================================================
# 8. INVALID PAGE
# ============================================================

def test_invalid_page():

    headers = get_auth_headers()

    response = client.get(
        "/vehicles?page=0",
        headers=headers
    )

    # Pydantic/FastAPI query validation
    # is handled globally as 422
    assert response.status_code == 422, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"
    assert "errors" in data


# ============================================================
# 9. INVALID LIMIT
# ============================================================

def test_invalid_limit():

    headers = get_auth_headers()

    response = client.get(
        "/vehicles?limit=0",
        headers=headers
    )

    # Pydantic/FastAPI query validation
    # is handled globally as 422
    assert response.status_code == 422, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"
    assert "errors" in data


# ============================================================
# 10. DELETE VEHICLE
# ============================================================

def test_delete_vehicle():

    headers = get_auth_headers()

    create_response = client.post(
        "/vehicles",
        json=vehicle_payload(
            "TEST-VH-DELETE"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    vehicle_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/vehicles/{vehicle_id}",
        headers=headers
    )

    assert delete_response.status_code in [
        200,
        204
    ], delete_response.text

    # Verify vehicle no longer exists
    get_response = client.get(
        f"/vehicles/{vehicle_id}",
        headers=headers
    )

    assert get_response.status_code == 404, (
        get_response.text
    )