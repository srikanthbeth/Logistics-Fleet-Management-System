from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Vehicle

from crud import (
    create_vehicle,
    delete_vehicle,
    get_vehicle_by_id,
    get_vehicle_by_number,
    get_vehicles,
    update_vehicle
)


ALLOWED_VEHICLE_STATUSES = {
    "Available",
    "Assigned",
    "Maintenance",
    "Inactive"
}


# ==========================================
# Create Vehicle
# ==========================================

def create_vehicle_service(
    db: Session,
    vehicle_data
):

    existing_vehicle = get_vehicle_by_number(
        db,
        vehicle_data.vehicle_number
    )

    if existing_vehicle:
        raise HTTPException(
            status_code=400,
            detail="Vehicle number already exists"
        )

    if vehicle_data.status not in ALLOWED_VEHICLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid vehicle status. "
                "Allowed statuses: "
                "Available, Assigned, "
                "Maintenance, Inactive"
            )
        )

    return create_vehicle(
        db,
        vehicle_data
    )


# ==========================================
# Get All Vehicles
# ==========================================

def get_all_vehicles_service(
    db: Session
):
    return get_vehicles(db)


# ==========================================
# Get Vehicle By ID
# ==========================================

def get_vehicle_service(
    db: Session,
    vehicle_id: int
):

    vehicle = get_vehicle_by_id(
        db,
        vehicle_id
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    return vehicle


# ==========================================
# Update Vehicle
# ==========================================

def update_vehicle_service(
    db: Session,
    vehicle_id: int,
    vehicle_data
):

    vehicle = get_vehicle_by_id(
        db,
        vehicle_id
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    update_data = vehicle_data.model_dump(
        exclude_unset=True
    )

    if "vehicle_number" in update_data:

        existing_vehicle = get_vehicle_by_number(
            db,
            update_data["vehicle_number"]
        )

        if (
            existing_vehicle
            and existing_vehicle.id != vehicle_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Vehicle number already exists"
            )

    if "status" in update_data:

        if (
            update_data["status"]
            not in ALLOWED_VEHICLE_STATUSES
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid vehicle status. "
                    "Allowed statuses: "
                    "Available, Assigned, "
                    "Maintenance, Inactive"
                )
            )

    return update_vehicle(
        db,
        vehicle,
        update_data
    )


# ==========================================
# Delete Vehicle
# ==========================================

def delete_vehicle_service(
    db: Session,
    vehicle_id: int
):

    vehicle = get_vehicle_by_id(
        db,
        vehicle_id
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    if vehicle.status == "Assigned":
        raise HTTPException(
            status_code=400,
            detail="Assigned vehicle cannot be deleted"
        )

    delete_vehicle(
        db,
        vehicle
    )

    return {
        "message": "Vehicle deleted successfully"
    }


# ==========================================
# Vehicle Search, Filtering & Pagination
# ==========================================

def get_vehicles_filtered_service(
    db: Session,
    status: str | None = None,
    vehicle_type: str | None = None,
    page: int = 1,
    limit: int = 10
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than or equal to 1"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than or equal to 1"
        )

    query = db.query(Vehicle)

    if status:
        query = query.filter(
            Vehicle.status == status
        )

    if vehicle_type:
        query = query.filter(
            Vehicle.vehicle_type == vehicle_type
        )

    total_records = query.count()

    offset = (page - 1) * limit

    vehicles = (
        query
        .order_by(Vehicle.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total_records": total_records,
        "current_page": page,
        "limit": limit,
        "data": vehicles
    }