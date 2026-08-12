from datetime import date

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ============================================================
# Authentication
# ============================================================

def get_auth_headers():
    """
    Register/login an Admin test user and return JWT headers.
    """

    username = "dashboard_admin"
    email = "dashboard_admin@test.com"
    password = "Test@12345"

    # --------------------------------------------------------
    # Try login first
    # --------------------------------------------------------

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    # --------------------------------------------------------
    # Register if user doesn't exist
    # --------------------------------------------------------

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

        # Login again
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

    token = login_response.json()["access_token"]

    assert token is not None

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# Dashboard
# ============================================================

def test_get_dashboard():

    headers = get_auth_headers()

    response = client.get(
        "/dashboard",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "total_vehicles" in data
    assert "available_vehicles" in data
    assert "vehicles_under_maintenance" in data

    assert "total_drivers" in data
    assert "active_drivers" in data

    assert "total_trips" in data
    assert "completed_trips" in data
    assert "cancelled_trips" in data

    assert "total_fuel_expenses" in data
    assert "total_maintenance_expenses" in data


# ============================================================
# Vehicle Expense Report
# ============================================================

def test_vehicle_expense_report():

    headers = get_auth_headers()

    response = client.get(
        "/dashboard/vehicle-expenses",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)

    # If vehicles exist, validate structure
    if data:

        vehicle = data[0]

        assert "vehicle_id" in vehicle
        assert "vehicle_number" in vehicle
        assert "fuel_expense" in vehicle
        assert "maintenance_expense" in vehicle
        assert "total_expense" in vehicle

        assert vehicle["fuel_expense"] >= 0
        assert vehicle["maintenance_expense"] >= 0
        assert vehicle["total_expense"] >= 0


# ============================================================
# Driver Trip Report
# ============================================================

def test_driver_trip_report():

    headers = get_auth_headers()

    response = client.get(
        "/dashboard/driver-trips",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)

    # If drivers exist, validate structure
    if data:

        driver = data[0]

        assert "driver_id" in driver
        assert "driver_name" in driver
        assert "total_trips" in driver
        assert "completed_trips" in driver
        assert "cancelled_trips" in driver
        assert "active_trips" in driver

        assert driver["total_trips"] >= 0
        assert driver["completed_trips"] >= 0
        assert driver["cancelled_trips"] >= 0
        assert driver["active_trips"] >= 0


# ============================================================
# Monthly Fuel Report
# ============================================================

def test_monthly_fuel_report():

    headers = get_auth_headers()

    response = client.get(
        "/dashboard/monthly-fuel",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)

    # If fuel records exist, validate structure
    if data:

        report = data[0]

        assert "year" in report
        assert "month" in report
        assert "total_fuel_expense" in report

        assert report["year"] >= 2000
        assert 1 <= report["month"] <= 12
        assert report["total_fuel_expense"] >= 0


# ============================================================
# Monthly Maintenance Report
# ============================================================

def test_monthly_maintenance_report():

    headers = get_auth_headers()

    response = client.get(
        "/dashboard/monthly-maintenance",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)

    # If maintenance records exist, validate structure
    if data:

        report = data[0]

        assert "year" in report
        assert "month" in report
        assert "total_maintenance_expense" in report

        assert report["year"] >= 2000
        assert 1 <= report["month"] <= 12
        assert report["total_maintenance_expense"] >= 0


# ============================================================
# Unauthorized Dashboard Access
# ============================================================

def test_dashboard_without_authentication():

    response = client.get(
        "/dashboard"
    )

    assert response.status_code == 401, response.text


# ============================================================
# Unauthorized Vehicle Expense Report
# ============================================================

def test_vehicle_expense_without_authentication():

    response = client.get(
        "/dashboard/vehicle-expenses"
    )

    assert response.status_code == 401, response.text


# ============================================================
# Unauthorized Driver Trip Report
# ============================================================

def test_driver_trip_without_authentication():

    response = client.get(
        "/dashboard/driver-trips"
    )

    assert response.status_code == 401, response.text


# ============================================================
# Unauthorized Monthly Fuel Report
# ============================================================

def test_monthly_fuel_without_authentication():

    response = client.get(
        "/dashboard/monthly-fuel"
    )

    assert response.status_code == 401, response.text


# ============================================================
# Unauthorized Monthly Maintenance Report
# ============================================================

def test_monthly_maintenance_without_authentication():

    response = client.get(
        "/dashboard/monthly-maintenance"
    )

    assert response.status_code == 401, response.text