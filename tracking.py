from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from oauth2 import require_roles

from schemas import (
    TrackingCreate,
    TrackingOut
)

from services.tracking_service import (
    create_tracking_service,
    get_trip_tracking_service
)


router = APIRouter(
    prefix="/trips",
    tags=["Delivery Tracking"]
)


# ==========================================
# Add Trip Tracking
# ==========================================

@router.post(
    "/{trip_id}/tracking",
    response_model=TrackingOut,
    status_code=201
)
def create_tracking(
    trip_id: int,
    tracking_data: TrackingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return create_tracking_service(
        db,
        trip_id,
        tracking_data
    )


# ==========================================
# Get Trip Tracking History
# ==========================================

@router.get(
    "/{trip_id}/tracking",
    response_model=list[TrackingOut]
)
def get_tracking(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return get_trip_tracking_service(
        db,
        trip_id
    )