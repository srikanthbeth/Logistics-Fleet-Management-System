from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ============================================================
# Authentication
# ============================================================

def get_auth_headers():
    """
    Register/login a test Admin user and return JWT headers.
    """

    username = "tracking_admin"
    email = "tracking_admin@test.com"
    password = "Test@12345"

    # Try login first
    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    # If user does not exist, register
    if login_response.status_code != 200:

        register_response = client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "Admin",
            },
        )

        assert register_response.status_code in [201, 400], (
            register_response.text
        )

        # Login after registration
        login_response = client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

    assert login_response.status_code == 200, (
        login_response.text
    )

    token = login_response.json().get("access_token")

    assert token is not None, login_response.text

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# Vehicle
# ============================================================

def create_vehicle(headers):

    unique_id = uuid4().hex[:8].upper()

    response = client.post(
        "/vehicles",
        json={
            "vehicle_number": f"TRK-TEST-{unique_id}",
            "vehicle_type": "Truck",
            "model": "Tata 407",
            "manufacturing_year": 2022,
            "capacity": 5000,
            "current_km": 10000,
            "status": "Available",
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Driver
# ============================================================

def create_driver(headers):

    unique_id = uuid4().hex[:8].lower()

    response = client.post(
        "/drivers",
        json={
            "name": f"Tracking Test Driver {unique_id}",
            "email": f"tracking_driver_{unique_id}@test.com",
            "phone": f"98765{unique_id[:5]}",
            "license_number": f"DL-TEST-{unique_id.upper()}",
            "license_expiry": "2030-12-31",
            "experience": 5,
            "status": "Active",
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Trip
# ============================================================

def create_trip(headers):

    vehicle_id = create_vehicle(headers)

    driver_id = create_driver(headers)

    start_date = datetime.now()

    expected_delivery_date = (
        start_date + timedelta(days=2)
    )

    response = client.post(
        "/trips",
        json={
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "source": "Hyderabad",
            "destination": "Bangalore",
            "start_date": start_date.isoformat(),
            "expected_delivery_date": (
                expected_delivery_date.isoformat()
            ),
            "distance": 570,
            "trip_status": "Scheduled",
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )

    return response.json()["id"]


# ============================================================
# Test Create Tracking
# ============================================================

def test_create_tracking():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Hyderabad",
            "status": "Started",
            "remarks": "Trip started",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )


# ============================================================
# Test Get Trip Tracking
# ============================================================

def test_get_trip_tracking():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    create_response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Hyderabad",
            "status": "Started",
            "remarks": "Trip started",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert create_response.status_code == 201, (
        create_response.text
    )

    response = client.get(
        f"/trips/{trip_id}/tracking",
        headers=headers,
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


# ============================================================
# Test Tracking Trip Not Found
# ============================================================

def test_tracking_trip_not_found():

    headers = get_auth_headers()

    response = client.get(
        "/trips/999999/tracking",
        headers=headers,
    )

    assert response.status_code == 404, (
        response.text
    )

    assert "Trip not found" in response.text


# ============================================================
# Test Create Tracking Trip Not Found
# ============================================================

def test_tracking_create_trip_not_found():

    headers = get_auth_headers()

    response = client.post(
        "/trips/999999/tracking",
        json={
            "location": "Hyderabad",
            "status": "Started",
            "remarks": "Invalid trip",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == 404, (
        response.text
    )

    assert "Trip not found" in response.text


# ============================================================
# Test Invalid Tracking Status
# ============================================================

def test_invalid_tracking_status():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Hyderabad",
            "status": "InvalidStatus",
            "remarks": "Invalid status",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code in [400, 422], (
        response.text
    )


# ============================================================
# Test Started Tracking
# ============================================================

def test_started_tracking():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Hyderabad",
            "status": "Started",
            "remarks": "Vehicle started",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )


# ============================================================
# Test In Transit Tracking
# ============================================================

def test_in_transit_tracking():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Kurnool",
            "status": "In Transit",
            "remarks": "Vehicle is in transit",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )


# ============================================================
# Test Delivered Tracking
# ============================================================

def test_delivered_tracking():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Bangalore",
            "status": "Delivered",
            "remarks": "Delivery completed",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )


# ============================================================
# Test Cancelled Tracking
# ============================================================

def test_cancelled_tracking():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    response = client.post(
        f"/trips/{trip_id}/tracking",
        json={
            "location": "Hyderabad",
            "status": "Cancelled",
            "remarks": "Trip cancelled",
            "timestamp": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == 201, (
        response.text
    )


# ============================================================
# Test Multiple Tracking Records
# ============================================================

def test_multiple_tracking_records():

    headers = get_auth_headers()

    trip_id = create_trip(headers)

    locations = [
        ("Hyderabad", "Started"),
        ("Kurnool", "In Transit"),
        ("Anantapur", "In Transit"),
        ("Bangalore", "Delivered"),
    ]

    for location, tracking_status in locations:

        response = client.post(
            f"/trips/{trip_id}/tracking",
            json={
                "location": location,
                "status": tracking_status,
                "remarks": (
                    f"Tracking at {location}"
                ),
                "timestamp": (
                    datetime.now().isoformat()
                ),
            },
            headers=headers,
        )

        assert response.status_code == 201, (
            response.text
        )

    response = client.get(
        f"/trips/{trip_id}/tracking",
        headers=headers,
    )

    assert response.status_code == 200, (
        response.text
    )

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 4