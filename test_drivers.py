from datetime import date, timedelta

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ============================================================
# Helper: Register + Login
# ============================================================

def get_auth_headers():
    username = "driver_test_admin"
    password = "Test@12345"
    email = "driver_test_admin@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": "Admin",
        },
    )

    # User may already exist from another test run.
    assert register_response.status_code in [201, 400]

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# Helper: Driver Data
# ============================================================

def driver_payload(
    license_number="TEST-LIC-001",
    email="driver001@example.com",
    name="Test Driver",
):
    return {
        "name": name,
        "email": email,
        "phone": "9876543210",
        "license_number": license_number,
        "license_expiry": str(
            date.today() + timedelta(days=365)
        ),
        "experience": 5.0,
        "status": "Active",
    }


# ============================================================
# 1. Create Driver
# ============================================================

def test_create_driver():
    headers = get_auth_headers()

    response = client.post(
        "/drivers",
        json=driver_payload(
            license_number="TEST-LIC-CREATE",
            email="create_driver@example.com",
            name="Create Driver",
        ),
        headers=headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["name"] == "Create Driver"
    assert data["email"] == "create_driver@example.com"
    assert data["license_number"] == "TEST-LIC-CREATE"
    assert data["status"] == "Active"
    assert "id" in data
    assert "created_at" in data


# ============================================================
# 2. Duplicate Driver / License
# ============================================================

def test_duplicate_driver():
    headers = get_auth_headers()

    payload = driver_payload(
        license_number="TEST-LIC-DUPLICATE",
        email="duplicate_driver@example.com",
        name="Duplicate Driver",
    )

    first_response = client.post(
        "/drivers",
        json=payload,
        headers=headers,
    )

    assert first_response.status_code in [201, 400], (
        first_response.text
    )

    second_response = client.post(
        "/drivers",
        json={
            **payload,
            "email": "duplicate_driver2@example.com",
        },
        headers=headers,
    )

    assert second_response.status_code == 400, (
        second_response.text
    )

    data = second_response.json()

    assert data["success"] is False
    assert "license" in data["detail"].lower()


# ============================================================
# 3. Get All Drivers
# ============================================================

def test_get_all_drivers():
    headers = get_auth_headers()

    # Create a driver so that the response contains data.
    create_response = client.post(
        "/drivers",
        json=driver_payload(
            license_number="TEST-LIC-LIST",
            email="list_driver@example.com",
            name="List Driver",
        ),
        headers=headers,
    )

    assert create_response.status_code in [201, 400]

    response = client.get(
        "/drivers",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "total_records" in data
    assert "current_page" in data
    assert "limit" in data
    assert "data" in data

    assert isinstance(data["data"], list)


# ============================================================
# 4. Get Driver By ID
# ============================================================

def test_get_driver_by_id():
    headers = get_auth_headers()

    create_response = client.post(
        "/drivers",
        json=driver_payload(
            license_number="TEST-LIC-GET",
            email="get_driver@example.com",
            name="Get Driver",
        ),
        headers=headers,
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    driver_id = create_response.json()["id"]

    response = client.get(
        f"/drivers/{driver_id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == driver_id
    assert data["name"] == "Get Driver"


# ============================================================
# 5. Driver Not Found
# ============================================================

def test_driver_not_found():
    headers = get_auth_headers()

    response = client.get(
        "/drivers/999999999",
        headers=headers,
    )

    assert response.status_code == 404, response.text

    data = response.json()

    assert data["success"] is False
    assert "driver not found" in data["detail"].lower()


# ============================================================
# 6. Update Driver
# ============================================================

def test_update_driver():
    headers = get_auth_headers()

    create_response = client.post(
        "/drivers",
        json=driver_payload(
            license_number="TEST-LIC-UPDATE",
            email="update_driver@example.com",
            name="Before Update",
        ),
        headers=headers,
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    driver_id = create_response.json()["id"]

    update_response = client.put(
        f"/drivers/{driver_id}",
        json={
            "name": "Updated Driver",
            "phone": "9123456789",
            "experience": 8.0,
            "status": "Inactive",
        },
        headers=headers,
    )

    assert update_response.status_code == 200, (
        update_response.text
    )

    data = update_response.json()

    assert data["id"] == driver_id
    assert data["name"] == "Updated Driver"
    assert data["phone"] == "9123456789"
    assert data["experience"] == 8.0
    assert data["status"] == "Inactive"

# ============================================================
# 7. Search Driver By Name
# ============================================================

def test_search_driver():
    headers = get_auth_headers()

    create_response = client.post(
        "/drivers",
        json=driver_payload(
            license_number="TEST-LIC-SEARCH",
            email="search_driver@example.com",
            name="Unique Search Driver",
        ),
        headers=headers,
    )

    assert create_response.status_code in [201, 400], (
        create_response.text
    )

    response = client.get(
        "/drivers",
        params={
            "name": "Unique Search"
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "data" in data
    assert isinstance(data["data"], list)


# ============================================================
# 8. Filter Driver By Status
# ============================================================

def test_filter_driver_by_status():
    headers = get_auth_headers()

    create_response = client.post(
        "/drivers",
        json=driver_payload(
            license_number="TEST-LIC-FILTER",
            email="filter_driver@example.com",
            name="Filter Driver",
        ),
        headers=headers,
    )

    assert create_response.status_code in [201, 400], (
        create_response.text
    )

    response = client.get(
        "/drivers",
        params={
            "status": "Active"
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "data" in data
    assert isinstance(data["data"], list)

    for driver in data["data"]:
        assert driver["status"] == "Active"


# ============================================================
# 9. Invalid Page
# ============================================================

def test_invalid_page():
    headers = get_auth_headers()

    response = client.get(
        "/drivers",
        params={
            "page": 0
        },
        headers=headers,
    )

    # FastAPI Query(ge=1) produces 422
    assert response.status_code == 422, response.text

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"


# ============================================================
# 10. Invalid Limit
# ============================================================

def test_invalid_limit():
    headers = get_auth_headers()

    response = client.get(
        "/drivers",
        params={
            "limit": 0
        },
        headers=headers,
    )

    # FastAPI Query(ge=1) produces 422
    assert response.status_code == 422, response.text

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"