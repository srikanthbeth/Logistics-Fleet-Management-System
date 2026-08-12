from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from oauth2 import require_roles

from schemas import (
    FuelCreate,
    FuelOut
)

from services.fuel_service import (
    create_fuel_service,
    get_all_fuel_service,
    get_vehicle_fuel_history_service
)


router = APIRouter(
    prefix="/fuel",
    tags=["Fuel Management"]
)


# ==========================================
# Create Fuel Record
# ==========================================

@router.post(
    "",
    response_model=FuelOut,
    status_code=201
)
def create_fuel(
    fuel_data: FuelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return create_fuel_service(
        db,
        fuel_data
    )


# ==========================================
# Get All Fuel Records
# ==========================================

@router.get(
    "",
    response_model=list[FuelOut]
)
def get_fuel(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Fleet Manager"
        )
    )
):
    return get_all_fuel_service(db)