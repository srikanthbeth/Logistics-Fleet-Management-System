import uuid
from datetime import datetime, timedelta

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

    unique_id = uuid.uuid4().hex[:8]

    username = f"fuel_admin_{unique_id}"
    email = f"fuel_admin_{unique_id}@example.com"
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

    assert register_response.status_code == 201, (
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

def create_vehicle(headers):
    """
    Create a vehicle for fuel testing.
    """

    vehicle_number = (
        f"FUEL-VH-{uuid.uuid4().hex[:8]}"
    )

    payload = {
        "vehicle_number": vehicle_number,
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

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Driver Helper
# ============================================================

def create_driver(headers):
    """
    Create a driver for trip creation.
    """

    unique_id = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Fuel Test Driver {unique_id}",
        "email": f"fuel_driver_{unique_id}@example.com",
        "phone": "9876543210",
        "license_number": f"FUEL-LIC-{unique_id}",
        "license_expiry": (
            datetime.now() + timedelta(days=365)
        ).date().isoformat(),
        "experience": 5,
        "status": "Active"
    }

    response = client.post(
        "/drivers",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Trip Helper
# ============================================================

def create_trip(headers):
    """
    Create a vehicle + driver + trip for fuel testing.
    """

    vehicle_id = create_vehicle(headers)

    driver_id = create_driver(headers)

    start_date = (
        datetime.now() + timedelta(days=1)
    )

    expected_delivery_date = (
        datetime.now() + timedelta(days=3)
    )

    trip_payload = {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "source": "Hyderabad",
        "destination": "Bangalore",
        "start_date": start_date.isoformat(),
        "expected_delivery_date": (
            expected_delivery_date.isoformat()
        ),
        "distance": 570
    }

    response = client.post(
        "/trips",
        json=trip_payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    trip_id = response.json()["id"]

    return vehicle_id, trip_id


# ============================================================
# Fuel Payload Helper
# ============================================================

def fuel_payload(
    vehicle_id,
    trip_id
):
    return {
        "vehicle_id": vehicle_id,
        "trip_id": trip_id,
        "fuel_type": "Diesel",
        "quantity": 100,
        "price_per_litre": 95,
        "fuel_date": datetime.now().isoformat()
    }


# ============================================================
# 1. CREATE FUEL RECORD
# ============================================================

def test_create_fuel():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["vehicle_id"] == vehicle_id
    assert data["trip_id"] == trip_id
    assert data["fuel_type"] == "Diesel"

    # 100 × 95 = 9500
    assert data["total_cost"] == 9500


# ============================================================
# 2. GET ALL FUEL RECORDS
# ============================================================

def test_get_all_fuel():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    create_response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    response = client.get(
        "/fuel",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


# ============================================================
# 3. VEHICLE NOT FOUND
# ============================================================

def test_fuel_vehicle_not_found():

    headers = get_auth_headers()

    _, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        999999,
        trip_id
    )

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Vehicle not found"


# ============================================================
# 4. TRIP NOT FOUND
# ============================================================

def test_fuel_trip_not_found():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        999999
    )

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Trip not found"


# ============================================================
# 5. TRIP DOES NOT BELONG TO VEHICLE
# ============================================================

def test_fuel_trip_vehicle_mismatch():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    another_vehicle_id = create_vehicle(
        headers
    )

    payload = fuel_payload(
        another_vehicle_id,
        trip_id
    )

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 400, (
        response.text
    )

    data = response.json()

    assert data["success"] is False

    assert data["detail"] == (
        "Trip does not belong to "
        "the selected vehicle"
    )


# ============================================================
# 6. INVALID FUEL TYPE
# ============================================================

def test_invalid_fuel_type():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["fuel_type"] = "Kerosene"

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 400, (
        response.text
    )

    data = response.json()

    assert data["success"] is False

    assert data["detail"] == (
        "Invalid fuel type. Allowed types: "
        "Diesel, Petrol, CNG, Electric"
    )


# ============================================================
# 7. INVALID FUEL QUANTITY
# ============================================================

def test_invalid_fuel_quantity():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["quantity"] = 0

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    # Quantity is validated by Pydantic schema
    assert response.status_code == 422, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"
    assert "errors" in data


# ============================================================
# 8. INVALID FUEL PRICE
# ============================================================

def test_invalid_fuel_price():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["price_per_litre"] = 0

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    # Price is validated by Pydantic schema
    assert response.status_code == 422, (
        response.text
    )

    data = response.json()

    assert data["success"] is False
    assert data["detail"] == "Validation error"
    assert "errors" in data


# ============================================================
# 9. TOTAL COST CALCULATION
# ============================================================

def test_fuel_total_cost_calculation():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["quantity"] = 50
    payload["price_per_litre"] = 100

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["quantity"] == 50
    assert data["price_per_litre"] == 100

    # 50 × 100 = 5000
    assert data["total_cost"] == 5000


# ============================================================
# 10. PETROL FUEL
# ============================================================

def test_petrol_fuel():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["fuel_type"] = "Petrol"

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["fuel_type"] == "Petrol"


# ============================================================
# 11. CNG FUEL
# ============================================================

def test_cng_fuel():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["fuel_type"] = "CNG"

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["fuel_type"] == "CNG"


# ============================================================
# 12. ELECTRIC FUEL
# ============================================================

def test_electric_fuel():

    headers = get_auth_headers()

    vehicle_id, trip_id = create_trip(
        headers
    )

    payload = fuel_payload(
        vehicle_id,
        trip_id
    )

    payload["fuel_type"] = "Electric"

    response = client.post(
        "/fuel",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["fuel_type"] == "Electric"