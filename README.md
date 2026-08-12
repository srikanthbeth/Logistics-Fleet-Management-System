# 🚚 Logistics Fleet Management System

A complete backend application built with **FastAPI** for managing vehicles, drivers, trips, delivery tracking, fuel expenses, vehicle maintenance, dashboards, and reports.

---

# Features

## Authentication

- User Registration
- User Login
- JWT Authentication
- Password Hashing
- OAuth2 Authentication
- Role-Based Authorization
- Current User Information

### Roles

- Admin
- Fleet Manager
- Driver

---

# Vehicle Management

- Create Vehicle
- View All Vehicles
- View Vehicle by ID
- Update Vehicle
- Delete Vehicle
- Search Vehicles
- Vehicle Status Management
- Duplicate Vehicle Validation
- Pagination Support

---

# Driver Management

- Create Driver
- View All Drivers
- View Driver by ID
- Update Driver
- Search Driver
- Filter Driver by Status
- Duplicate Driver Validation
- Pagination Support

---

# Trip Management

- Create Trip
- View All Trips
- View Trip by ID
- Start Trip
- Complete Trip
- Cancel Trip
- Filter Trips by Status
- Filter Trips by Source
- Filter Trips by Destination
- Filter Trips by Date
- Duplicate Trip Validation
- Pagination Support

### Trip Status

- Scheduled
- Started
- In Transit
- Delivered
- Cancelled

---

# Delivery Tracking

- Add Trip Tracking
- View Trip Tracking History
- Track Trip Status
- Validate Trip Before Tracking
- Prevent Tracking on Completed Trips
- Invalid Tracking Status Validation
- Multiple Tracking Records

### Tracking Status

- Scheduled
- Started
- In Transit
- Delivered
- Cancelled

---

# Fuel Management

- Add Fuel Record
- View All Fuel Records
- Vehicle Validation
- Trip Validation
- Vehicle and Trip Relationship Validation
- Fuel Type Validation
- Fuel Quantity Validation
- Fuel Price Validation
- Automatic Total Cost Calculation

### Supported Fuel Types

- Petrol
- CNG
- Electric

---

# Vehicle Maintenance

- Create Maintenance Record
- View All Maintenance Records
- View Maintenance by ID
- Start Maintenance
- Complete Maintenance
- Update Maintenance Cost
- Vehicle Validation
- Maintenance Status Validation
- Service Cost Validation
- Current KM Validation

---

# Dashboard & Reports

## Admin Dashboard

- Total Vehicles
- Available Vehicles
- Vehicles Under Maintenance
- Total Drivers
- Active Drivers
- Total Trips
- Completed Trips
- Cancelled Trips
- Total Fuel Expenses
- Total Maintenance Expenses

## Reports

- Vehicle-wise Expense Report
- Driver-wise Trip Report
- Monthly Fuel Expense Report
- Monthly Maintenance Expense Report

---

# Technology Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT
- OAuth2
- Uvicorn
- Pytest
- Alembic
- Swagger UI

---

# Project Structure

```text
logistics_fleet/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── oauth2.py
├── exceptions.py
│
├── services/
│   ├── auth_service.py
│   ├── vehicle_service.py
│   ├── driver_service.py
│   ├── trip_service.py
│   ├── tracking_service.py
│   ├── fuel_service.py
│   ├── maintenance_service.py
│   └── dashboard_service.py
│
├── routers/
│   ├── auth.py
│   ├── vehicles.py
│   ├── drivers.py
│   ├── trips.py
│   ├── tracking.py
│   ├── fuel.py
│   ├── maintenance.py
│   └── dashboard.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_dashboard.py
│   ├── test_drivers.py
│   ├── test_fuel.py
│   ├── test_maintenance.py
│   ├── test_tracking.py
│   ├── test_trips.py
│   └── test_vehicles.py
│
├── alembic/
│   └── versions/
│
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# Installation

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

### Windows

```powershell
venv\Scripts\activate
```

## Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# PostgreSQL Database

Create a PostgreSQL database for the project.

Example:

```text
Database: logistics_fleet
Host: localhost
Port: 5432
```

Configure the database connection in your project configuration.

Example:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/logistics_fleet"
```

> Do not commit database passwords or secret keys to GitHub.

---

# Database Migration

Create a migration:

```powershell
alembic revision --autogenerate -m "initial migration"
```

Apply migrations:

```powershell
alembic upgrade head
```

---

# Run the Application

Start the FastAPI server:

```powershell
uvicorn main:app --reload
```

Application URL:

```text
http://127.0.0.1:8000
```

---

# API Documentation

## Swagger UI

```text
http://127.0.0.1:8000/docs
```

## ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# Authentication

## Register User

### POST

```text
/auth/register
```

### Request Body

```json
{
  "username": "admin_user",
  "email": "admin@example.com",
  "password": "Admin@12345",
  "role": "Admin"
}
```

### Response

```text
201 Created
```

---

# Login

### POST

```text
/auth/login
```

### Request Body

```json
{
  "username": "admin_user",
  "password": "Admin@12345"
}
```

### Response

```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "token_type": "bearer"
}
```

---

# Swagger Authorization

Open:

```text
http://127.0.0.1:8000/docs
```

Click:

```text
Authorize 🔒
```

Enter your registered:

```text
Username: admin_user
Password: Admin@12345
```

Click:

```text
Authorize
```

After successful authorization, Swagger sends the JWT token automatically with protected API requests.

---

# Current User

### GET

```text
/auth/me
```

Example response:

```json
{
  "id": 1,
  "username": "admin_user",
  "email": "admin@example.com",
  "role": "Admin",
  "is_active": true,
  "created_at": "2026-08-11T10:00:00+05:30"
}
```

---

# API Endpoints

## Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/token
GET  /auth/me
```

## Vehicles

```text
POST   /vehicles
GET    /vehicles
GET    /vehicles/{vehicle_id}
PUT    /vehicles/{vehicle_id}
DELETE /vehicles/{vehicle_id}
```

## Drivers

```text
POST /drivers
GET  /drivers
GET  /drivers/{driver_id}
PUT  /drivers/{driver_id}
```

## Trips

```text
POST /trips
GET  /trips
GET  /trips/{trip_id}
POST /trips/{trip_id}/start
POST /trips/{trip_id}/complete
POST /trips/{trip_id}/cancel
```

## Tracking

```text
POST /trips/{trip_id}/tracking
GET  /trips/{trip_id}/tracking
```

## Fuel

```text
POST /fuel
GET  /fuel
```

## Maintenance

```text
POST /maintenance
GET  /maintenance
GET  /maintenance/{maintenance_id}
PUT  /maintenance/{maintenance_id}
```

## Dashboard & Reports

```text
GET /dashboard
GET /dashboard/vehicle-expenses
GET /dashboard/driver-trips
GET /dashboard/monthly-fuel
GET /dashboard/monthly-maintenance
```

---

# Complete Workflow Demonstration

Demonstrate the complete workflow:

**Register → Login → Add Vehicle → Add Driver → Create Trip → Start Trip → Add Tracking → Complete Trip → Add Fuel → Add Maintenance → Dashboard → Reports**

---

# Example Workflow

## 1. Register Admin

```json
{
  "username": "admin_user",
  "email": "admin@example.com",
  "password": "Admin@12345",
  "role": "Admin"
}
```

---

## 2. Login

```json
{
  "username": "admin_user",
  "password": "Admin@12345"
}
```

---

## 3. Add Vehicle

```json
{
  "vehicle_number": "AP39AB1234",
  "vehicle_type": "Truck",
  "model": "Tata 407",
  "status": "Available"
}
```

---

## 4. Add Driver

```json
{
  "name": "Ravi Kumar",
  "phone": "9876543210",
  "license_number": "DL123456789",
  "status": "Active"
}
```

---

## 5. Create Trip

```json
{
  "vehicle_id": 1,
  "driver_id": 1,
  "source": "Hyderabad",
  "destination": "Bangalore",
  "trip_date": "2026-08-12T10:00:00"
}
```

---

## 6. Start Trip

```text
POST /trips/1/start
```

---

## 7. Add Tracking

```json
{
  "status": "In Transit"
}
```

---

## 8. Complete Trip

```text
POST /trips/1/complete
```

---

## 9. Add Fuel

Example:

```json
{
  "vehicle_id": 1,
  "trip_id": 1,
  "fuel_type": "Petrol",
  "quantity": 50,
  "price_per_unit": 100
}
```

The total fuel cost is calculated automatically.

---

## 10. Add Maintenance

Example:

```json
{
  "vehicle_id": 1,
  "service_type": "Engine Service",
  "service_date": "2026-08-12T10:00:00",
  "service_cost": 5000
}
```

---

## 11. Dashboard

```text
GET /dashboard
```

The dashboard provides fleet-level operational and expense information.

---

## 12. Reports

### Vehicle Expense Report

```text
GET /dashboard/vehicle-expenses
```

### Driver Trip Report

```text
GET /dashboard/driver-trips
```

### Monthly Fuel Report

```text
GET /dashboard/monthly-fuel
```

### Monthly Maintenance Report

```text
GET /dashboard/monthly-maintenance
```

---

# Testing

Run all tests:

```powershell
python -m pytest -v
```

Run tests with short traceback:

```powershell
python -m pytest -v --tb=short
```

Run an individual test file:

```powershell
python -m pytest tests/test_auth.py -v
```

Example:

```powershell
python -m pytest tests/test_tracking.py -v --tb=short
```

---

# Test Results

The complete automated test suite contains:

```text
91 tests
```

Latest result:

```text
91 passed, 1 warning
```

Test modules:

```text
test_auth.py
test_dashboard.py
test_drivers.py
test_fuel.py
test_maintenance.py
test_tracking.py
test_trips.py
test_vehicles.py
```

---

# Testing Coverage

## Authentication

- User registration
- Duplicate username
- Duplicate email
- Invalid role
- Successful login
- Wrong password
- Non-existent user
- Missing authentication token
- Valid JWT token
- Invalid JWT token

## Vehicles

- Create vehicle
- Duplicate vehicle
- Get vehicles
- Get vehicle by ID
- Vehicle not found
- Update vehicle
- Invalid vehicle status
- Pagination
- Delete vehicle

## Drivers

- Create driver
- Duplicate driver
- Get drivers
- Get driver by ID
- Driver not found
- Update driver
- Search driver
- Filter by status
- Pagination

## Trips

- Create trip
- Duplicate trip
- Get trips
- Get trip by ID
- Start trip
- Complete trip
- Cancel trip
- Filter by status
- Filter by source
- Filter by destination
- Filter by date
- Pagination
- Not-found scenarios

## Fuel

- Create fuel record
- Get fuel records
- Vehicle validation
- Trip validation
- Vehicle/trip mismatch
- Fuel type validation
- Quantity validation
- Price validation
- Total cost calculation
- Petrol
- CNG
- Electric

## Maintenance

- Create maintenance
- Get maintenance
- Get maintenance by ID
- Vehicle validation
- Status validation
- Service cost validation
- Current KM validation
- Start maintenance
- Complete maintenance
- Update maintenance cost

## Tracking

- Create tracking
- Get tracking history
- Trip not found
- Invalid tracking status
- Scheduled tracking
- Started tracking
- In Transit tracking
- Delivered tracking
- Cancelled tracking
- Multiple tracking records

## Dashboard & Reports

- Dashboard
- Vehicle expense report
- Driver trip report
- Monthly fuel report
- Monthly maintenance report
- Authentication validation

---

# Error Handling

The application provides structured API error responses.

Example:

```json
{
  "success": false,
  "detail": "Vehicle not found"
}
```

The system validates:

- Authentication
- Authorization
- Duplicate records
- Invalid IDs
- Invalid statuses
- Vehicle existence
- Driver existence
- Trip existence
- Vehicle/trip relationships
- Fuel quantity
- Fuel price
- Maintenance cost
- Pagination parameters
- Tracking status

---

# Security

- JWT-based authentication
- OAuth2 password flow
- Password hashing
- Role-based authorization
- Protected API endpoints
- Database credentials should be kept private
- Secret keys should not be committed to GitHub

---

# Requirements

Generate the requirements file:

```powershell
pip freeze > requirements.txt
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# Final Verification

Before submission, run:

```powershell
python -m pytest -v
```

Expected:

```text
91 passed
```

Start the application:

```powershell
uvicorn main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Then demonstrate:

```text
Register
→ Login / Authorize
→ Add Vehicle
→ Add Driver
→ Create Trip
→ Start Trip
→ Add Tracking
→ Complete Trip
→ Add Fuel
→ Add Maintenance
→ Dashboard
→ Reports
```

---

# Project Status

**Completed**

- ✅ Authentication
- ✅ JWT Authorization
- ✅ Role-Based Authorization
- ✅ Vehicle Management
- ✅ Driver Management
- ✅ Trip Management
- ✅ Delivery Tracking
- ✅ Fuel Management
- ✅ Vehicle Maintenance
- ✅ Dashboard
- ✅ Reports
- ✅ Swagger API Documentation
- ✅ Automated Testing
- ✅ 91/91 Tests Passing

---

# Author

**Srikanth Bethamcharla**

**Logistics Fleet Management System**

Built with **FastAPI + PostgreSQL + SQLAlchemy + JWT + Pytest**
