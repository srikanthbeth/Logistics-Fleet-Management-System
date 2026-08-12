from typing import Optional

from schemas import (
    VehicleOut,
    VehicleListResponse
)



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
    VehicleCreate,
    VehicleOut,
    VehicleUpdate,
    FuelOut,
    MaintenanceOut
)



from services.vehicle_service import (
    create_vehicle_service,
    delete_vehicle_service,
    get_all_vehicles_service,
    get_vehicle_service,
    update_vehicle_service
)

from services.fuel_service import (
    get_vehicle_fuel_history_service
)

from services.maintenance_service import (
    get_vehicle_maintenance_service
)

from services.vehicle_service import (
    get_vehicles_filtered_service
)


router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


# ==========================================
# Create Vehicle
# ==========================================

@router.post(
    "",
    response_model=VehicleOut,
    status_code=status.HTTP_201_CREATED
)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return create_vehicle_service(
        db,
        vehicle_data
    )

# ==========================================
# Get Vehicles
# Filtering + Pagination
# ==========================================

@router.get(
    "",
    response_model=VehicleListResponse
)
def get_vehicles_api(
    status: str | None = Query(
        default=None
    ),
    vehicle_type: str | None = Query(
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
    return get_vehicles_filtered_service(
        db=db,
        status=status,
        vehicle_type=vehicle_type,
        page=page,
        limit=limit
    )

# ==========================================
# Vehicle Maintenance History
# ==========================================

@router.get(
    "/{vehicle_id}/maintenance",
    response_model=list[MaintenanceOut]
)
def get_vehicle_maintenance_api(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return get_vehicle_maintenance_service(
        db,
        vehicle_id
    )


# ==========================================
# Vehicle Fuel History
# ==========================================

@router.get(
    "/{vehicle_id}/fuel-history",
    response_model=list[FuelOut]
)
def get_vehicle_fuel_history_api(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return get_vehicle_fuel_history_service(
        db,
        vehicle_id
    )



# ==========================================
# Get Vehicle By ID
# ==========================================

@router.get(
    "/{vehicle_id}",
    response_model=VehicleOut
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager",
            "Driver"
        )
    )
):
    return get_vehicle_service(
        db,
        vehicle_id
    )


# ==========================================
# Update Vehicle
# ==========================================

@router.put(
    "/{vehicle_id}",
    response_model=VehicleOut
)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return update_vehicle_service(
        db,
        vehicle_id,
        vehicle_data
    )


# ==========================================
# Delete Vehicle
# ==========================================

@router.delete(
    "/{vehicle_id}"
)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Admin")
    )
):
    return delete_vehicle_service(
        db,
        vehicle_id
    )
