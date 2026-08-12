from fastapi import HTTPException

from sqlalchemy.orm import Session

from crud import (
    create_fuel,
    get_fuel_records,
    get_vehicle_fuel_history
)

from models import (
    Fuel,
    Trip,
    Vehicle
)


# ==========================================
# Allowed Fuel Types
# ==========================================

ALLOWED_FUEL_TYPES = {
    "Diesel",
    "Petrol",
    "CNG",
    "Electric"
}


# ==========================================
# Create Fuel
# ==========================================

def create_fuel_service(
    db: Session,
    fuel_data
):
    # --------------------------------------
    # Check Vehicle
    # --------------------------------------

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == fuel_data.vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    # --------------------------------------
    # Check Trip
    # --------------------------------------

    trip = (
        db.query(Trip)
        .filter(
            Trip.id == fuel_data.trip_id
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    # --------------------------------------
    # Check Trip belongs to Vehicle
    # --------------------------------------

    if trip.vehicle_id != fuel_data.vehicle_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Trip does not belong to "
                "the selected vehicle"
            )
        )

    # --------------------------------------
    # Validate Fuel Type
    # --------------------------------------

    if fuel_data.fuel_type not in ALLOWED_FUEL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid fuel type. Allowed types: "
                "Diesel, Petrol, CNG, Electric"
            )
        )

    # --------------------------------------
    # Validate Quantity
    # --------------------------------------

    if fuel_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Fuel quantity must be greater than 0"
        )

    # --------------------------------------
    # Validate Price
    # --------------------------------------

    if fuel_data.price_per_litre <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Price per litre must be "
                "greater than 0"
            )
        )

    # --------------------------------------
    # Calculate Total Cost
    # --------------------------------------

    total_cost = (
        fuel_data.quantity
        * fuel_data.price_per_litre
    )

    # --------------------------------------
    # Create Fuel Record
    # --------------------------------------

    return create_fuel(
        db,
        fuel_data,
        total_cost
    )


# ==========================================
# Get All Fuel
# ==========================================

def get_all_fuel_service(
    db: Session
):
    return get_fuel_records(db)


# ==========================================
# Vehicle Fuel History
# ==========================================

def get_vehicle_fuel_history_service(
    db: Session,
    vehicle_id: int
):
    # Check vehicle exists
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    return get_vehicle_fuel_history(
        db,
        vehicle_id
    )