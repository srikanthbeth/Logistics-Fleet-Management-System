from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from datetime import date

from sqlalchemy import func

from crud import (
    create_trip,
    get_trip_by_id,
    get_trips,
    update_trip_status
)

from models import (
    Driver,
    Vehicle,
    Trip
)


ALLOWED_TRIP_STATUSES = {
    "Scheduled",
    "Started",
    "In Transit",
    "Delivered",
    "Cancelled"
}


ACTIVE_TRIP_STATUSES = {
    "Scheduled",
    "Started",
    "In Transit"
}


# ==========================================
# Create Trip
# ==========================================

def create_trip_service(
    db: Session,
    trip_data
):

    # --------------------------------------
    # Check Vehicle
    # --------------------------------------

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == trip_data.vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    # Vehicle under maintenance
    if vehicle.status == "Maintenance":
        raise HTTPException(
            status_code=400,
            detail=(
                "Vehicle under maintenance "
                "cannot be assigned to a trip"
            )
        )

    # Inactive vehicle
    if vehicle.status == "Inactive":
        raise HTTPException(
            status_code=400,
            detail=(
                "Inactive vehicle cannot "
                "be assigned to a trip"
            )
        )

    # Already assigned
    if vehicle.status == "Assigned":
        raise HTTPException(
            status_code=400,
            detail=(
                "Vehicle already has an active trip"
            )
        )

    # --------------------------------------
    # Check Driver
    # --------------------------------------

    driver = (
        db.query(Driver)
        .filter(
            Driver.id == trip_data.driver_id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    # Inactive driver
    if driver.status == "Inactive":
        raise HTTPException(
            status_code=400,
            detail=(
                "Inactive driver cannot "
                "be assigned to a trip"
            )
        )

    # Already assigned
    if driver.status == "Assigned":
        raise HTTPException(
            status_code=400,
            detail=(
                "Driver already has an active trip"
            )
        )

    # --------------------------------------
    # License Expiry
    # --------------------------------------

    now = datetime.now()

    license_expiry = driver.license_expiry

    if license_expiry.tzinfo is not None:
        now = datetime.now(
            license_expiry.tzinfo
        )

    if license_expiry <= now:
        raise HTTPException(
            status_code=400,
            detail=(
                "Driver license has expired "
                "and cannot be assigned"
            )
        )

    # --------------------------------------
    # Date Validation
    # --------------------------------------

    if (
        trip_data.expected_delivery_date
        <= trip_data.start_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Expected delivery date must "
                "be after start date"
            )
        )

    # --------------------------------------
    # Distance Validation
    # --------------------------------------

    if trip_data.distance <= 0:
        raise HTTPException(
            status_code=400,
            detail="Distance must be greater than 0"
        )

    # --------------------------------------
    # Create Trip
    # --------------------------------------

    trip = create_trip(
        db,
        trip_data
    )

    # --------------------------------------
    # Automatically assign vehicle
    # --------------------------------------

    vehicle.status = "Assigned"

    # --------------------------------------
    # Automatically assign driver
    # --------------------------------------

    driver.status = "Assigned"

    db.commit()
    db.refresh(trip)

    return trip


# ==========================================
# Get All Trips
# ==========================================

def get_all_trips_service(
    db: Session
):
    return get_trips(db)


# ==========================================
# Get Trip By ID
# ==========================================

def get_trip_service(
    db: Session,
    trip_id: int
):
    trip = get_trip_by_id(
        db,
        trip_id
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip


# ==========================================
# Start Trip
# ==========================================

def start_trip_service(
    db: Session,
    trip_id: int
):

    trip = get_trip_by_id(
        db,
        trip_id
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    if trip.trip_status != "Scheduled":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only scheduled trips "
                "can be started"
            )
        )

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == trip.vehicle_id
        )
        .first()
    )

    driver = (
        db.query(Driver)
        .filter(
            Driver.id == trip.driver_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    if vehicle.status == "Maintenance":
        raise HTTPException(
            status_code=400,
            detail=(
                "Vehicle is under maintenance"
            )
        )

    if driver.status == "Inactive":
        raise HTTPException(
            status_code=400,
            detail=(
                "Inactive driver cannot "
                "start a trip"
            )
        )

    return update_trip_status(
        db,
        trip,
        "Started"
    )


# ==========================================
# Complete Trip
# ==========================================

def complete_trip_service(
    db: Session,
    trip_id: int
):

    trip = get_trip_by_id(
        db,
        trip_id
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    if trip.trip_status not in {
        "Started",
        "In Transit"
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only started or in-transit "
                "trips can be completed"
            )
        )

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == trip.vehicle_id
        )
        .first()
    )

    driver = (
        db.query(Driver)
        .filter(
            Driver.id == trip.driver_id
        )
        .first()
    )

    trip.trip_status = "Delivered"

    # Vehicle becomes available
    if vehicle:
        vehicle.status = "Available"

        vehicle.current_km = (
            vehicle.current_km
            + trip.distance
        )

    # Driver becomes available
    if driver:
        driver.status = "Active"

    db.commit()
    db.refresh(trip)

    return trip


# ==========================================
# Cancel Trip
# ==========================================

def cancel_trip_service(
    db: Session,
    trip_id: int
):

    trip = get_trip_by_id(
        db,
        trip_id
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    if trip.trip_status in {
        "Delivered",
        "Cancelled"
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Completed or cancelled trips "
                "cannot be cancelled again"
            )
        )

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == trip.vehicle_id
        )
        .first()
    )

    driver = (
        db.query(Driver)
        .filter(
            Driver.id == trip.driver_id
        )
        .first()
    )

    trip.trip_status = "Cancelled"

    # Release vehicle
    if vehicle:
        vehicle.status = "Available"

    # Release driver
    if driver:
        driver.status = "Active"

    db.commit()
    db.refresh(trip)

    return trip

# ==========================================
# Trip Search, Filtering & Pagination
# ==========================================

def get_trips_filtered_service(
    db: Session,
    trip_status: str | None = None,
    source: str | None = None,
    destination: str | None = None,
    trip_date: date | None = None,
    page: int = 1,
    limit: int = 10
):

    query = db.query(Trip)

    # --------------------------------------
    # Filter by trip status
    # --------------------------------------

    if trip_status:
        query = query.filter(
            Trip.trip_status == trip_status
        )

    # --------------------------------------
    # Filter by source
    # --------------------------------------

    if source:
        query = query.filter(
            Trip.source.ilike(
                f"%{source}%"
            )
        )

    # --------------------------------------
    # Filter by destination
    # --------------------------------------

    if destination:
        query = query.filter(
            Trip.destination.ilike(
                f"%{destination}%"
            )
        )

    # --------------------------------------
    # Filter by date
    # --------------------------------------

    if trip_date:

        query = query.filter(
            func.date(
                Trip.start_date
            ) == trip_date
        )

    # --------------------------------------
    # Total records
    # --------------------------------------

    total_records = query.count()

    # --------------------------------------
    # Pagination
    # --------------------------------------

    offset = (page - 1) * limit

    trips = (
        query
        .order_by(Trip.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total_records": total_records,
        "current_page": page,
        "limit": limit,
        "data": trips
    }