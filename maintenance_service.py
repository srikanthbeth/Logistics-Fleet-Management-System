from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import (
    create_maintenance,
    get_maintenance_records,
    get_maintenance_by_id,
    get_vehicle_maintenance,
    update_maintenance
)

from models import (
    Maintenance,
    Vehicle,
    Trip
)


ALLOWED_MAINTENANCE_STATUSES = {
    "Scheduled",
    "In Progress",
    "Completed"
}


ACTIVE_TRIP_STATUSES = {
    "Scheduled",
    "Started",
    "In Transit"
}


# ==========================================
# Create Maintenance
# ==========================================

def create_maintenance_service(
    db: Session,
    maintenance_data
):

    # --------------------------------------
    # Check Vehicle
    # --------------------------------------

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id ==
            maintenance_data.vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    # --------------------------------------
    # Validate Status
    # --------------------------------------

    if (
        maintenance_data.status
        not in ALLOWED_MAINTENANCE_STATUSES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid maintenance status. "
                "Allowed statuses: Scheduled, "
                "In Progress, Completed"
            )
        )

    # --------------------------------------
    # Validate Service Cost
    # --------------------------------------

    if maintenance_data.service_cost <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Service cost must be greater than 0"
            )
        )

    # --------------------------------------
    # Validate Current KM
    # --------------------------------------

    if maintenance_data.current_km < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Current KM cannot be negative"
            )
        )

    # --------------------------------------
    # Check Active Trip
    # --------------------------------------

    active_trip = (
        db.query(Trip)
        .filter(
            Trip.vehicle_id ==
            maintenance_data.vehicle_id,
            Trip.trip_status.in_(
                ACTIVE_TRIP_STATUSES
            )
        )
        .first()
    )

    if active_trip:
        raise HTTPException(
            status_code=400,
            detail=(
                "Vehicle has an active trip "
                "and cannot be sent for maintenance"
            )
        )

    # --------------------------------------
    # If maintenance starts immediately
    # --------------------------------------

    if maintenance_data.status == "In Progress":

        if vehicle.status == "Assigned":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Assigned vehicle cannot "
                    "start maintenance"
                )
            )

        if vehicle.status == "Inactive":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Inactive vehicle cannot "
                    "start maintenance"
                )
            )

        vehicle.status = "Maintenance"

    # --------------------------------------
    # If already completed
    # --------------------------------------

    if maintenance_data.status == "Completed":

        if vehicle.status == "Assigned":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Assigned vehicle cannot "
                    "complete maintenance"
                )
            )

        vehicle.status = "Available"

    # --------------------------------------
    # Create record
    # --------------------------------------

    maintenance = create_maintenance(
        db,
        maintenance_data
    )

    db.commit()
    db.refresh(maintenance)

    return maintenance


# ==========================================
# Get All Maintenance
# ==========================================

def get_all_maintenance_service(
    db: Session
):
    return get_maintenance_records(db)


# ==========================================
# Get Maintenance By Vehicle
# ==========================================

def get_vehicle_maintenance_service(
    db: Session,
    vehicle_id: int
):

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

    return get_vehicle_maintenance(
        db,
        vehicle_id
    )


# ==========================================
# Update Maintenance
# ==========================================

def update_maintenance_service(
    db: Session,
    maintenance_id: int,
    update_data
):

    maintenance = get_maintenance_by_id(
        db,
        maintenance_id
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id ==
            maintenance.vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    update_values = update_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------
    # Validate status
    # --------------------------------------

    if "status" in update_values:

        new_status = update_values["status"]

        if (
            new_status
            not in ALLOWED_MAINTENANCE_STATUSES
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid maintenance status. "
                    "Allowed statuses: Scheduled, "
                    "In Progress, Completed"
                )
            )

        # -------------------------------
        # Start maintenance
        # -------------------------------

        if new_status == "In Progress":

            active_trip = (
                db.query(Trip)
                .filter(
                    Trip.vehicle_id ==
                    maintenance.vehicle_id,
                    Trip.trip_status.in_(
                        ACTIVE_TRIP_STATUSES
                    )
                )
                .first()
            )

            if active_trip:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Vehicle has an active trip "
                        "and cannot enter maintenance"
                    )
                )

            if vehicle.status == "Assigned":
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Assigned vehicle cannot "
                        "start maintenance"
                    )
                )

            vehicle.status = "Maintenance"

        # -------------------------------
        # Complete maintenance
        # -------------------------------

        elif new_status == "Completed":

            vehicle.status = "Available"

    # --------------------------------------
    # Validate cost
    # --------------------------------------

    if "service_cost" in update_values:

        if update_values["service_cost"] <= 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Service cost must be greater than 0"
                )
            )

    # --------------------------------------
    # Validate KM
    # --------------------------------------

    if "current_km" in update_values:

        if update_values["current_km"] < 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Current KM cannot be negative"
                )
            )

    # --------------------------------------
    # Update
    # --------------------------------------

    maintenance = update_maintenance(
        db,
        maintenance,
        update_data
    )

    db.commit()
    db.refresh(maintenance)

    return maintenance


# ==========================================
# Get Maintenance By ID
# ==========================================

def get_maintenance_service(
    db: Session,
    maintenance_id: int
):

    maintenance = get_maintenance_by_id(
        db,
        maintenance_id
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    return maintenance