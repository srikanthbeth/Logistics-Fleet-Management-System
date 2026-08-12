from fastapi import (
    APIRouter,
    Depends,
    Query
)

from datetime import date

from sqlalchemy.orm import Session

from database import get_db

from oauth2 import require_roles

from schemas import (
    TripCreate,
    TripOut,
    TripListResponse
)



from services.trip_service import (
    cancel_trip_service,
    complete_trip_service,
    create_trip_service,
    get_all_trips_service,
    get_trip_service,
    start_trip_service,
    get_trips_filtered_service
)




router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)


# ==========================================
# Create Trip
# ==========================================

@router.post(
    "",
    response_model=TripOut,
    status_code=201
)
def create_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return create_trip_service(
        db,
        trip_data
    )


# ==========================================
# Get Trips
# Filtering + Pagination
# ==========================================

@router.get(
    "",
    response_model=TripListResponse
)
def get_trips(
    trip_status: str | None = Query(
        default=None
    ),
    source: str | None = Query(
        default=None
    ),
    destination: str | None = Query(
        default=None
    ),
    trip_date: date | None = Query(
        default=None
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return get_trips_filtered_service(
        db=db,
        trip_status=trip_status,
        source=source,
        destination=destination,
        trip_date=trip_date,
        page=page,
        limit=limit
    )

# ==========================================
# Get Trip By ID
# ==========================================

@router.get(
    "/{trip_id}",
    response_model=TripOut
)
def get_trip(
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
    return get_trip_service(
        db,
        trip_id
    )


# ==========================================
# Start Trip
# ==========================================

@router.put(
    "/{trip_id}/start",
    response_model=TripOut
)
def start_trip(
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
    return start_trip_service(
        db,
        trip_id
    )


# ==========================================
# Complete Trip
# ==========================================

@router.put(
    "/{trip_id}/complete",
    response_model=TripOut
)
def complete_trip(
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
    return complete_trip_service(
        db,
        trip_id
    )


# ==========================================
# Cancel Trip
# ==========================================

@router.put(
    "/{trip_id}/cancel",
    response_model=TripOut
)
def cancel_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return cancel_trip_service(
        db,
        trip_id
    )