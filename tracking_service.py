from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import (
    create_tracking,
    get_trip_tracking
)

from models import Trip


# ==========================================
# Allowed Tracking Statuses
# ==========================================

ALLOWED_TRACKING_STATUSES = {
    "Scheduled",
    "Started",
    "In Transit",
    "Delivered",
    "Cancelled"
}


# ==========================================
# Create Tracking
# ==========================================

def create_tracking_service(
    db: Session,
    trip_id: int,
    tracking_data
):
    # --------------------------------------
    # Check Trip
    # --------------------------------------

    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    # --------------------------------------
    # Completed / Delivered trips
    # cannot receive tracking
    # --------------------------------------

    if trip.trip_status == "Delivered":
        raise HTTPException(
            status_code=400,
            detail=(
                "Completed trips cannot receive "
                "new tracking updates"
            )
        )

    # --------------------------------------
    # Validate Status
    # --------------------------------------

    if (
        tracking_data.status
        not in ALLOWED_TRACKING_STATUSES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid tracking status. "
                "Allowed statuses: Scheduled, "
                "Started, In Transit, Delivered, "
                "Cancelled"
            )
        )

    # --------------------------------------
    # Create Tracking Record
    # --------------------------------------

    return create_tracking(
        db,
        trip_id,
        tracking_data
    )


# ==========================================
# Get Trip Tracking History
# ==========================================

def get_trip_tracking_service(
    db: Session,
    trip_id: int
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return get_trip_tracking(
        db,
        trip_id
    )