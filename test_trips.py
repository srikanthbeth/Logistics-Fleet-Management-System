from datetime import date, datetime, timedelta

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

    username = "trip_test_admin"
    email = "trip_test_admin@example.com"
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
# Vehicle Payload
# ============================================================

def vehicle_payload(vehicle_number):
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
# Driver Payload
# ============================================================

def driver_payload(
    email,
    license_number
):
    future_date = (
        date.today() + timedelta(days=365)
    ).isoformat()

    return {
        "name": "Trip Test Driver",
        "email": email,
        "phone": "9876543210",
        "license_number": license_number,
        "license_expiry": future_date,
        "experience": 5,
        "status": "Active"
    }


# ============================================================
# Create Vehicle Helper
# ============================================================

def create_vehicle(headers, vehicle_number):
    response = client.post(
        "/vehicles",
        json=vehicle_payload(vehicle_number),
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Create Driver Helper
# ============================================================

def create_driver(headers, email, license_number):
    response = client.post(
        "/drivers",
        json=driver_payload(
            email,
            license_number
        ),
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Trip Payload
# ============================================================

def trip_payload(
    vehicle_id,
    driver_id,
    source="Hyderabad",
    destination="Bangalore"
):
    start_date = datetime.now() + timedelta(days=1)
    expected_delivery_date = (
        start_date + timedelta(days=2)
    )

    return {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "source": source,
        "destination": destination,
        "start_date": start_date.isoformat(),
        "expected_delivery_date": (
            expected_delivery_date.isoformat()
        ),
        "distance": 570,
        "trip_status": "Scheduled"
    }


# ============================================================
# 1. CREATE TRIP
# ============================================================

def test_create_trip():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers,
        "TEST-TRIP-VH-CREATE"
    )

    driver_id = create_driver(
        headers,
        "trip_create@example.com",
        "TRIP-LIC-CREATE"
    )

    response = client.post(
        "/trips",
        json=trip_payload(
            vehicle_id,
            driver_id
        ),
        headers=headers
    )

    assert response.status_code == 201, (
        response.text
    )

    data = response.json()

    assert data["vehicle_id"] == vehicle_id
    assert data["driver_id"] == driver_id
    assert data["source"] == "Hyderabad"
    assert data["destination"] == "Bangalore"


# ============================================================
# 2. DUPLICATE TRIP
# ============================================================

def test_duplicate_trip():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers,
        "TEST-TRIP-VH-DUP"
    )

    driver_id = create_driver(
        headers,
        "trip_duplicate@example.com",
        "TRIP-LIC-DUP"
    )

    payload = trip_payload(
        vehicle_id,
        driver_id
    )

    first_response = client.post(
        "/trips",
        json=payload,
        headers=headers
    )

    assert first_response.status_code == 201, (
        first_response.text
    )

    # Vehicle and driver become Assigned after
    # first trip, so second creation should fail.
    second_response = client.post(
        "/trips",
        json=payload,
        headers=headers
    )

    assert second_response.status_code == 400, (
        second_response.text
    )

    data = second_response.json()

    assert data["success"] is False


# ============================================================
# 3. GET ALL TRIPS
# ============================================================

def test_get_all_trips():

    headers = get_auth_headers()

    response = client.get(
        "/trips",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert "total_records" in data
    assert "current_page" in data
    assert "limit" in data
    assert "data" in data

    assert isinstance(
        data["data"],
        list
    )


# ============================================================
# 4. GET TRIP BY ID
# ============================================================

def test_get_trip_by_id():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers,
        "TEST-TRIP-VH-GET"
    )

    driver_id = create_driver(
        headers,
        "trip_get@example.com",
        "TRIP-LIC-GET"
    )

    create_response = client.post(
        "/trips",
        json=trip_payload(
            vehicle_id,
            driver_id
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    trip_id = create_response.json()["id"]

    response = client.get(
        f"/trips/{trip_id}",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert data["id"] == trip_id
    assert data["vehicle_id"] == vehicle_id
    assert data["driver_id"] == driver_id


# ============================================================
# 5. TRIP NOT FOUND
# ============================================================

def test_trip_not_found():

    headers = get_auth_headers()

    response = client.get(
        "/trips/999999",
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False


# ============================================================
# 6. START TRIP
# ============================================================

def test_start_trip():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers,
        "TEST-TRIP-VH-START"
    )

    driver_id = create_driver(
        headers,
        "trip_start@example.com",
        "TRIP-LIC-START"
    )

    create_response = client.post(
        "/trips",
        json=trip_payload(
            vehicle_id,
            driver_id
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    trip_id = create_response.json()["id"]

    response = client.put(
        f"/trips/{trip_id}/start",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert data["id"] == trip_id
    assert data["trip_status"] == "Started"


# ============================================================
# 7. COMPLETE TRIP
# ============================================================

def test_complete_trip():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers,
        "TEST-TRIP-VH-COMPLETE"
    )

    driver_id = create_driver(
        headers,
        "trip_complete@example.com",
        "TRIP-LIC-COMPLETE"
    )

    create_response = client.post(
        "/trips",
        json=trip_payload(
            vehicle_id,
            driver_id
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    trip_id = create_response.json()["id"]

    start_response = client.put(
        f"/trips/{trip_id}/start",
        headers=headers
    )

    assert start_response.status_code == 200, (
        start_response.text
    )

    complete_response = client.put(
        f"/trips/{trip_id}/complete",
        headers=headers
    )

    assert complete_response.status_code == 200, (
        complete_response.text
    )

    data = complete_response.json()

    assert data["id"] == trip_id
    assert data["trip_status"] == "Delivered"


# ============================================================
# 8. CANCEL TRIP
# ============================================================

def test_cancel_trip():

    headers = get_auth_headers()

    vehicle_id = create_vehicle(
        headers,
        "TEST-TRIP-VH-CANCEL"
    )

    driver_id = create_driver(
        headers,
        "trip_cancel@example.com",
        "TRIP-LIC-CANCEL"
    )

    create_response = client.post(
        "/trips",
        json=trip_payload(
            vehicle_id,
            driver_id
        ),
        headers=headers
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    trip_id = create_response.json()["id"]

    response = client.put(
        f"/trips/{trip_id}/cancel",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert data["id"] == trip_id
    assert data["trip_status"] == "Cancelled"


# ============================================================
# 9. FILTER BY STATUS
# ============================================================

def test_filter_trip_by_status():

    headers = get_auth_headers()

    response = client.get(
        "/trips?trip_status=Scheduled",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert "data" in data

    for trip in data["data"]:
        assert trip["trip_status"] == "Scheduled"


# ============================================================
# 10. FILTER BY SOURCE
# ============================================================

def test_filter_trip_by_source():

    headers = get_auth_headers()

    response = client.get(
        "/trips?source=Hyderabad",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert "data" in data

    for trip in data["data"]:
        assert "hyderabad" in trip["source"].lower()


# ============================================================
# 11. FILTER BY DESTINATION
# ============================================================

def test_filter_trip_by_destination():

    headers = get_auth_headers()

    response = client.get(
        "/trips?destination=Bangalore",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert "data" in data

    for trip in data["data"]:
        assert "bangalore" in (
            trip["destination"].lower()
        )


# ============================================================
# 12. FILTER BY DATE
# ============================================================

def test_filter_trip_by_date():

    headers = get_auth_headers()

    trip_date = date.today() + timedelta(days=1)

    response = client.get(
        f"/trips?trip_date={trip_date.isoformat()}",
        headers=headers
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert "data" in data


# ============================================================
# 13. INVALID PAGE
# ============================================================

def test_invalid_page():

    headers = get_auth_headers()

    response = client.get(
        "/trips?page=0",
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
# 14. INVALID LIMIT
# ============================================================

def test_invalid_limit():

    headers = get_auth_headers()

    response = client.get(
        "/trips?limit=0",
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
# 15. START TRIP NOT FOUND
# ============================================================

def test_start_trip_not_found():

    headers = get_auth_headers()

    response = client.put(
        "/trips/999999/start",
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False


# ============================================================
# 16. COMPLETE TRIP NOT FOUND
# ============================================================

def test_complete_trip_not_found():

    headers = get_auth_headers()

    response = client.put(
        "/trips/999999/complete",
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False


# ============================================================
# 17. CANCEL TRIP NOT FOUND
# ============================================================

def test_cancel_trip_not_found():

    headers = get_auth_headers()

    response = client.put(
        "/trips/999999/cancel",
        headers=headers
    )

    assert response.status_code == 404, (
        response.text
    )

    data = response.json()

    assert data["success"] is False