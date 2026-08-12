from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from oauth2 import require_roles

from schemas import (
    MaintenanceCreate,
    MaintenanceOut,
    MaintenanceUpdate
)

from services.maintenance_service import (
    create_maintenance_service,
    get_all_maintenance_service,
    get_vehicle_maintenance_service,
    update_maintenance_service,
    get_maintenance_service
)


router = APIRouter(
    prefix="/maintenance",
    tags=["Vehicle Maintenance"]
)


# ==========================================
# Create Maintenance
# ==========================================

@router.post(
    "",
    response_model=MaintenanceOut,
    status_code=201
)
def create_maintenance(
    maintenance_data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return create_maintenance_service(
        db,
        maintenance_data
    )


# ==========================================
# Get All Maintenance
# ==========================================

@router.get(
    "",
    response_model=list[MaintenanceOut]
)
def get_maintenance(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return get_all_maintenance_service(db)


# ==========================================
# Get Maintenance By ID
# ==========================================

@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceOut
)
def get_maintenance_by_id(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return get_maintenance_service(
        db,
        maintenance_id
    )


# ==========================================
# Update Maintenance
# ==========================================

@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceOut
)
def update_maintenance(
    maintenance_id: int,
    update_data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return update_maintenance_service(
        db,
        maintenance_id,
        update_data
    )