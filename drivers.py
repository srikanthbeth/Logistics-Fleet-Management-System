from fastapi import (
    APIRouter,
    Depends,
    status,
    Query
)

from sqlalchemy.orm import Session

from database import get_db

from oauth2 import require_roles

from schemas import (
    DriverCreate,
    DriverOut,
    DriverUpdate
)

from schemas import (
    DriverOut,
    DriverListResponse
)

from services.driver_service import (
    create_driver_service,
    get_all_drivers_service,
    get_driver_service,
    update_driver_service
)


from services.driver_service import (
    get_drivers_filtered_service
)

router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"]
)


# ==========================================
# Create Driver
# ==========================================

@router.post(
    "",
    response_model=DriverOut,
    status_code=status.HTTP_201_CREATED
)
def create_driver(
    driver_data: DriverCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return create_driver_service(
        db,
        driver_data
    )


# ==========================================
# Get Drivers
# Search + Filtering + Pagination
# ==========================================

@router.get(
    "",
    response_model=DriverListResponse
)
def get_drivers_api(
    name: str | None = Query(
        default=None
    ),
    status: str | None = Query(
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
    return get_drivers_filtered_service(
        db=db,
        name=name,
        status=status,
        page=page,
        limit=limit
    )


# ==========================================
# Get Driver By ID
# ==========================================

@router.get(
    "/{driver_id}",
    response_model=DriverOut
)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return get_driver_service(
        db,
        driver_id
    )


# ==========================================
# Update Driver
# ==========================================

@router.put(
    "/{driver_id}",
    response_model=DriverOut
)
def update_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return update_driver_service(
        db,
        driver_id,
        driver_data
    )