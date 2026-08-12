from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from oauth2 import require_roles

from schemas import (
    DashboardOut,
    VehicleExpenseReport,
    DriverTripReport,
    MonthlyFuelReport,
    MonthlyMaintenanceReport
)

from services.dashboard_service import (
    get_dashboard_service,
    get_vehicle_expense_report_service,
    get_driver_trip_report_service,
    get_monthly_fuel_report_service,
    get_monthly_maintenance_report_service
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard & Reports"]
)


# ==========================================
# Admin Dashboard
# ==========================================

@router.get(
    "",
    response_model=DashboardOut
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin"
        )
    )
):
    return get_dashboard_service(db)


# ==========================================
# Vehicle-wise Expense Report
# ==========================================

@router.get(
    "/vehicle-expenses",
    response_model=list[
        VehicleExpenseReport
    ]
)
def vehicle_expense_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin"
        )
    )
):
    return get_vehicle_expense_report_service(
        db
    )


# ==========================================
# Driver-wise Trip Report
# ==========================================

@router.get(
    "/driver-trips",
    response_model=list[
        DriverTripReport
    ]
)
def driver_trip_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin"
        )
    )
):
    return get_driver_trip_report_service(
        db
    )


# ==========================================
# Monthly Fuel Report
# ==========================================

@router.get(
    "/monthly-fuel",
    response_model=list[
        MonthlyFuelReport
    ]
)
def monthly_fuel_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin"
        )
    )
):
    return get_monthly_fuel_report_service(
        db
    )


# ==========================================
# Monthly Maintenance Report
# ==========================================

@router.get(
    "/monthly-maintenance",
    response_model=list[
        MonthlyMaintenanceReport
    ]
)
def monthly_maintenance_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin"
        )
    )
):
    return get_monthly_maintenance_report_service(
        db
    )