from datetime import datetime, date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


# ==========================================
# Authentication Schemas
# ==========================================

class UserRegister(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=72
    )

    role: str = Field(
        default="Driver"
    )


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class Token(BaseModel):
    access_token: str
    token_type: str

  
# ==========================================
# Vehicle Schemas
# ==========================================

class VehicleBase(BaseModel):
    vehicle_number: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    vehicle_type: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    model: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    manufacturing_year: int = Field(
        ...,
        ge=1900
    )

    capacity: float = Field(
        ...,
        gt=0
    )

    current_km: float = Field(
        ...,
        ge=0
    )

    status: str = Field(
        default="Available"
    )
    @field_validator("status")
    @classmethod
    def validate_vehicle_status(cls, value):
        allowed_statuses = {
           "Available",
           "Assigned",
           "Maintenance",
           "Inactive"
        }

        if value not in allowed_statuses:
         raise ValueError(
            "Invalid vehicle status"
        )

        return value

class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    vehicle_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    manufacturing_year: int | None = Field(
        default=None,
        ge=1900
    )

    capacity: float | None = Field(
        default=None,
        gt=0
    )

    current_km: float | None = Field(
        default=None,
        ge=0
    )

    status: str | None = None


class VehicleOut(VehicleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

# ==========================================
# Driver Schemas
# ==========================================

class DriverBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    phone: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    license_number: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    license_expiry: date

    experience: float = Field(
        ...,
        ge=0
    )

    status: str = Field(
        default="Active"
    )

    @field_validator("license_expiry")
    @classmethod
    def validate_license_expiry(cls, value):

        if value <= date.today():
            raise ValueError(
                "License expiry date must be in the future"
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_driver_status(cls, value):

        allowed_statuses = {
            "Active",
            "Inactive"
        }

        if value not in allowed_statuses:
            raise ValueError(
                "Invalid driver status"
            )

        return value


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20
    )

    license_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    license_expiry: datetime | None = None

    experience: float | None = Field(
        default=None,
        ge=0
    )

    status: str | None = None

    @field_validator("license_expiry")
    @classmethod
    def validate_license_expiry(cls, value):

     if value is not None and value <= date.today():
        raise ValueError(
            "License expiry date must be in the future"
        )

     return value


class DriverOut(DriverBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

 # ==========================================
# Trip Schemas
# ==========================================

class TripBase(BaseModel):

    vehicle_id: int = Field(
        ...,
        gt=0
    )

    driver_id: int = Field(
        ...,
        gt=0
    )

    source: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    destination: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    start_date: datetime

    expected_delivery_date: datetime

    distance: float = Field(
        ...,
        gt=0
    )

    trip_status: str = Field(
        default="Scheduled"
    )

    @field_validator("expected_delivery_date")
    @classmethod
    def validate_delivery_date(
        cls,
        value,
        info
    ):

        start_date = info.data.get(
            "start_date"
        )

        if (
            start_date is not None
            and value < start_date
        ):
            raise ValueError(
                "Expected delivery date "
                "cannot be before start date"
            )

        return value

    @field_validator("trip_status")
    @classmethod
    def validate_trip_status(cls, value):

        allowed_statuses = {
            "Scheduled",
            "Started",
            "In Transit",
            "Delivered",
            "Cancelled"
        }

        if value not in allowed_statuses:
            raise ValueError(
                "Invalid trip status"
            )

        return value

class TripCreate(TripBase):
    pass


class TripOut(TripBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

# ==========================================
# Fuel Schemas
# ==========================================

class FuelBase(BaseModel):

    vehicle_id: int = Field(
        ...,
        gt=0
    )

    trip_id: int = Field(
        ...,
        gt=0
    )

    fuel_type: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    quantity: float = Field(
        ...,
        gt=0
    )

    price_per_litre: float = Field(
        ...,
        gt=0
    )

    fuel_date: datetime


class FuelCreate(FuelBase):
    pass


class FuelOut(FuelBase):
    id: int
    total_cost: float
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

# ==========================================
# Maintenance Schemas
# ==========================================

class MaintenanceBase(BaseModel):

    vehicle_id: int = Field(
        ...,
        gt=0
    )

    service_type: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    service_date: datetime

    service_cost: float = Field(
        ...,
        gt=0
    )

    current_km: float = Field(
        ...,
        ge=0
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    status: str = Field(
        default="Scheduled"
    )

    @field_validator("status")
    @classmethod
    def validate_maintenance_status(
        cls,
        value
    ):

        allowed_statuses = {
            "Scheduled",
            "In Progress",
            "Completed"
        }

        if value not in allowed_statuses:
            raise ValueError(
                "Invalid maintenance status"
            )

        return value


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    service_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    service_date: datetime | None = None

    service_cost: float | None = Field(
        default=None,
        gt=0
    )

    current_km: float | None = Field(
        default=None,
        ge=0
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    status: str | None = None


class MaintenanceOut(MaintenanceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

    # ==========================================
# Trip Tracking Schemas
# ==========================================

class TrackingBase(BaseModel):
    location: str = Field(
        min_length=1,
        max_length=255
    )

    status: str = Field(
        min_length=1,
        max_length=50
    )

    remarks: str | None = Field(
        default=None,
        max_length=500
    )

    timestamp: datetime


class TrackingCreate(TrackingBase):
    pass


class TrackingOut(TrackingBase):
    id: int
    trip_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

    # ==========================================
# Pagination Response Schemas
# ==========================================

class VehicleListResponse(BaseModel):
    total_records: int
    current_page: int
    limit: int
    data: list[VehicleOut]


class DriverListResponse(BaseModel):
    total_records: int
    current_page: int
    limit: int
    data: list[DriverOut]


class TripListResponse(BaseModel):
    total_records: int
    current_page: int
    limit: int
    data: list[TripOut]

    # ==========================================
# Dashboard Schemas
# ==========================================

class DashboardOut(BaseModel):
    total_vehicles: int
    available_vehicles: int
    vehicles_under_maintenance: int

    total_drivers: int
    active_drivers: int

    total_trips: int
    completed_trips: int
    cancelled_trips: int

    total_fuel_expenses: float
    total_maintenance_expenses: float

    # ==========================================
# Vehicle Expense Report
# ==========================================

class VehicleExpenseReport(BaseModel):
    vehicle_id: int
    vehicle_number: str
    fuel_expense: float
    maintenance_expense: float
    total_expense: float

    # ==========================================
# Driver Trip Report
# ==========================================

class DriverTripReport(BaseModel):
    driver_id: int
    driver_name: str
    total_trips: int
    completed_trips: int
    cancelled_trips: int
    active_trips: int

    # ==========================================
# Monthly Fuel Expense Report
# ==========================================

class MonthlyFuelReport(BaseModel):
    year: int
    month: int
    total_fuel_expense: float

    # ==========================================
# Monthly Maintenance Expense Report
# ==========================================

class MonthlyMaintenanceReport(BaseModel):
    year: int
    month: int
    total_maintenance_expense: float