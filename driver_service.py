from datetime import datetime, timezone

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models import Driver

from crud import (
    create_driver,
    get_driver_by_email,
    get_driver_by_id,
    get_driver_by_license,
    get_drivers,
    update_driver
)


ALLOWED_DRIVER_STATUSES = {
    "Active",
    "Assigned",
    "Inactive",
}


# ==========================================
# Validate License Expiry
# ==========================================

def validate_license_expiry(
    license_expiry
):
    now = datetime.now(timezone.utc)

    # Handle timezone-naive datetime
    if license_expiry.tzinfo is None:
        now = datetime.now()

    if license_expiry <= now:
        raise HTTPException(
            status_code=400,
            detail="License expiry date must be in the future"
        )


def create_driver_service(
    db: Session,
    driver_data
):
    # ==========================================
    # Check duplicate license number
    # ==========================================

    existing_driver = get_driver_by_license_number(
        db,
        driver_data.license_number
    )

    if existing_driver:
        raise HTTPException(
            status_code=400,
            detail="License number already exists"
        )

    # ==========================================
    # Validate driver status
    # ==========================================

    if driver_data.status not in ALLOWED_DRIVER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid driver status. "
                "Allowed statuses: Active, Inactive"
            )
        )

    # ==========================================
    # Create driver
    # ==========================================

    return create_driver(
        db,
        driver_data
    )

# ==========================================
# Get All Drivers
# ==========================================

def get_all_drivers_service(
    db: Session
):
    return get_drivers(db)


# ==========================================
# Get Driver
# ==========================================

def get_driver_service(
    db: Session,
    driver_id: int
):
    driver = get_driver_by_id(
        db,
        driver_id
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    return driver

def get_driver_by_license_number(
    db: Session,
    license_number: str
):
    return (
        db.query(Driver)
        .filter(
            Driver.license_number == license_number
        )
        .first()
    )


# ==========================================
# Update Driver
# ==========================================

def update_driver_service(
    db: Session,
    driver_id: int,
    driver_data
):
    driver = get_driver_by_id(
        db,
        driver_id
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    update_data = driver_data.model_dump(
        exclude_unset=True
    )

    # Check license number
    if "license_number" in update_data:

        existing_license = (
            get_driver_by_license(
                db,
                update_data["license_number"]
            )
        )

        if (
            existing_license
            and existing_license.id != driver_id
        ):
            raise HTTPException(
                status_code=400,
                detail="License number already exists"
            )

    # Check email
    if "email" in update_data:

        existing_email = (
            get_driver_by_email(
                db,
                update_data["email"]
            )
        )

        if (
            existing_email
            and existing_email.id != driver_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Driver email already exists"
            )

    # Validate expiry if changed
    if "license_expiry" in update_data:

        validate_license_expiry(
            update_data["license_expiry"]
        )

    # Validate status
    if "status" in update_data:

        if (
            update_data["status"]
            not in ALLOWED_DRIVER_STATUSES
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid driver status. "
                    "Allowed statuses: "
                    "Active, Assigned, Inactive"
                )
            )

    return update_driver(
        db,
        driver,
        update_data
    )

# ==========================================
# Driver Search, Filtering & Pagination
# ==========================================

def get_drivers_filtered_service(
    db: Session,
    name: str | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 10
):

    query = db.query(Driver)

    # --------------------------------------
    # Search by name
    # --------------------------------------

    if name:
        query = query.filter(
            Driver.name.ilike(
                f"%{name}%"
            )
        )

    # --------------------------------------
    # Filter by status
    # --------------------------------------

    if status:
        query = query.filter(
            Driver.status == status
        )

    # --------------------------------------
    # Total records
    # --------------------------------------

    total_records = query.count()

    # --------------------------------------
    # Pagination
    # --------------------------------------

    offset = (page - 1) * limit

    drivers = (
        query
        .order_by(Driver.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total_records": total_records,
        "current_page": page,
        "limit": limit,
        "data": drivers
    }