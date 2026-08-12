import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ============================================================
# Authentication Helper
# ============================================================

def get_auth_headers():
    username = "maintenance_test_admin"
    email = "maintenance_test_admin@example.com"
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
# Vehicle Helper
# ============================================================

def create_vehicle():

    headers = get_auth_headers()

    payload = {
        "vehicle_number": "MAINT-VH-001",
        "vehicle_type": "Truck",
        "model": "Tata 407",
        "manufacturing_year": 2022,
        "current_km": 25000,
        "capacity": 5000,
        "status": "Available"
    }

    response = client.post(
        "/vehicles",
        json=payload,
        headers=headers
    )

    # Vehicle may already exist
    if response.status_code == 400:
        get_response = client.get(
            "/vehicles",
            headers=headers
        )

        assert get_response.status_code == 200

        vehicles = get_response.json()["data"]

        for vehicle in vehicles:
            if vehicle["vehicle_number"] == "MAINT-VH-001":
                return vehicle["id"]

    assert response.status_code == 201, response.text

    return response.json()["id"]


# ============================================================
# Maintenance Payload
# ============================================================

def maintenance_payload(
    vehicle_id,
    status="Scheduled",
    service_cost=5000,
    current_km=25000,
    service_type="Engine Service",
    service_date="2026-08-10"
):
    return {
        "vehicle_id": vehicle_id,
        "service_type": service_type,
        "service_date": service_date,
        "description": "Regular vehicle maintenance",
        "service_cost": service_cost,
        "current_km": current_km,
        "status": status
    }


# ============================================================
# 1. CREATE MAINTENANCE
# ============================================================

def test_create_maintenance():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    response = client.post(
        "/maintenance",
        json=maintenance_payload(
            vehicle_id
        ),
        headers=headers
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["vehicle_id"] == vehicle_id
    assert data["service_type"] == "Engine Service"
    assert data["service_cost"] == 5000
    assert data["current_km"] == 25000
    assert data["status"] == "Scheduled"


# ============================================================
# 2. GET ALL MAINTENANCE
# ============================================================

def test_get_all_maintenance():

    headers = get_auth_headers()

    response = client.get(
        "/maintenance",
        headers=headers
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 3. GET MAINTENANCE BY ID
# ============================================================

def test_get_maintenance_by_id():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    create_response = client.post(
        "/maintenance",
        json=maintenance_payload(
            vehicle_id,
            service_type="Brake Service"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    maintenance_id = create_response.json()["id"]

    response = client.get(
        f"/maintenance/{maintenance_id}",
        headers=headers
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == maintenance_id
    assert data["vehicle_id"] == vehicle_id
    assert data["service_type"] == "Brake Service"


# ============================================================
# 4. MAINTENANCE NOT FOUND
# ============================================================

def test_maintenance_not_found():

    headers = get_auth_headers()

    response = client.get(
        "/maintenance/999999",
        headers=headers
    )

    assert response.status_code == 404, response.text

    data = response.json()

    assert data["success"] is False


# ============================================================
# 5. VEHICLE NOT FOUND
# ============================================================

def test_maintenance_vehicle_not_found():

    headers = get_auth_headers()

    payload = maintenance_payload(
        vehicle_id=999999
    )

    response = client.post(
        "/maintenance",
        json=payload,
        headers=headers
    )

    assert response.status_code == 404, response.text

    data = response.json()

    assert data["success"] is False


# ============================================================
# 6. INVALID MAINTENANCE STATUS
# ============================================================

def test_invalid_maintenance_status():

    headers = get_auth_headers()

    payload = maintenance_payload(
        "TEST-MAINT-INVALID-STATUS"
    )

    payload["status"] = "INVALID_STATUS"

    response = client.post(
        "/maintenance",
        json=payload,
        headers=headers
    )

    # Pydantic schema validation happens before
    # the service layer, therefore 422 is expected.
    assert response.status_code == 422, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"
    assert "errors" in data

    # Verify validation error is related to status
    assert any(
        error["loc"][-1] == "status"
        for error in data["errors"]
    )


# ============================================================
# 7. INVALID SERVICE COST
# ============================================================

def test_invalid_service_cost():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    payload = maintenance_payload(
        vehicle_id=vehicle_id,
        service_cost=0
    )

    response = client.post(
        "/maintenance",
        json=payload,
        headers=headers
    )

    assert response.status_code == 422 or response.status_code == 400, (
        response.text
    )


# ============================================================
# 8. INVALID CURRENT KM
# ============================================================

def test_invalid_current_km():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    payload = maintenance_payload(
        vehicle_id=vehicle_id,
        current_km=-100
    )

    response = client.post(
        "/maintenance",
        json=payload,
        headers=headers
    )

    assert response.status_code == 400 or response.status_code == 422, (
        response.text
    )


# ============================================================
# 9. START MAINTENANCE
# ============================================================

def test_start_maintenance():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    create_response = client.post(
        "/maintenance",
        json=maintenance_payload(
            vehicle_id=vehicle_id,
            status="Scheduled",
            service_type="Oil Change"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    maintenance_id = create_response.json()["id"]

    response = client.put(
        f"/maintenance/{maintenance_id}",
        json={
            "status": "In Progress"
        },
        headers=headers
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["status"] == "In Progress"


# ============================================================
# 10. COMPLETE MAINTENANCE
# ============================================================

def test_complete_maintenance():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    create_response = client.post(
        "/maintenance",
        json=maintenance_payload(
            vehicle_id=vehicle_id,
            status="Scheduled",
            service_type="Full Service"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    maintenance_id = create_response.json()["id"]

    # Start maintenance
    start_response = client.put(
        f"/maintenance/{maintenance_id}",
        json={
            "status": "In Progress"
        },
        headers=headers
    )

    assert start_response.status_code == 200, (
        start_response.text
    )

    # Complete maintenance
    response = client.put(
        f"/maintenance/{maintenance_id}",
        json={
            "status": "Completed"
        },
        headers=headers
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["status"] == "Completed"


# ============================================================
# 11. UPDATE MAINTENANCE COST
# ============================================================

def test_update_maintenance_cost():

    headers = get_auth_headers()

    vehicle_id = create_vehicle()

    create_response = client.post(
        "/maintenance",
        json=maintenance_payload(
            vehicle_id=vehicle_id,
            service_cost=5000,
            service_type="Tyre Service"
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    maintenance_id = create_response.json()["id"]

    response = client.put(
        f"/maintenance/{maintenance_id}",
        json={
            "service_cost": 7500
        },
        headers=headers
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == maintenance_id
    assert data["service_cost"] == 7500


# ============================================================
# 12. UPDATE MAINTENANCE NOT FOUND
# ============================================================

def test_update_maintenance_not_found():

    headers = get_auth_headers()

    response = client.put(
        "/maintenance/999999",
        json={
            "service_cost": 7500
        },
        headers=headers
    )

    assert response.status_code == 404, response.text

    data = response.json()

    assert data["success"] is False