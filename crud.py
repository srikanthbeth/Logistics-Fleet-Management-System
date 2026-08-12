from sqlalchemy.orm import Session

from models import User, Vehicle, Driver, Trip, Fuel, Maintenance,  TripTracking

# ==========================================
# User CRUD
# ==========================================

def get_user_by_username(
    db: Session,
    username: str
):
    return (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


def create_user(
    db: Session,
    username: str,
    email: str,
    hashed_password: str,
    role: str
):
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# ==========================================
# Vehicle CRUD
# ==========================================

def get_vehicle_by_number(
    db: Session,
    vehicle_number: str
):
    return (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_number == vehicle_number
        )
        .first()
    )


def create_vehicle(
    db: Session,
    vehicle_data
):
    vehicle = Vehicle(
        vehicle_number=vehicle_data.vehicle_number,
        vehicle_type=vehicle_data.vehicle_type,
        model=vehicle_data.model,
        manufacturing_year=vehicle_data.manufacturing_year,
        capacity=vehicle_data.capacity,
        current_km=vehicle_data.current_km,
        status=vehicle_data.status
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def get_vehicles(
    db: Session
):
    return (
        db.query(Vehicle)
        .order_by(Vehicle.id.desc())
        .all()
    )


def get_vehicle_by_id(
    db: Session,
    vehicle_id: int
):
    return (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )


def update_vehicle(
    db: Session,
    vehicle,
    update_data: dict
):
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)

    return vehicle


def delete_vehicle(
    db: Session,
    vehicle
):
    db.delete(vehicle)
    db.commit()

    # ==========================================
# Driver CRUD
# ==========================================

def get_driver_by_license(
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


def get_driver_by_email(
    db: Session,
    email: str
):
    return (
        db.query(Driver)
        .filter(
            Driver.email == email
        )
        .first()
    )


def create_driver(
    db: Session,
    driver_data
):
    driver = Driver(
        name=driver_data.name,
        email=driver_data.email,
        phone=driver_data.phone,
        license_number=driver_data.license_number,
        license_expiry=driver_data.license_expiry,
        experience=driver_data.experience,
        status=driver_data.status
    )

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return driver


def get_drivers(
    db: Session
):
    return (
        db.query(Driver)
        .order_by(Driver.id.desc())
        .all()
    )


def get_driver_by_id(
    db: Session,
    driver_id: int
):
    return (
        db.query(Driver)
        .filter(
            Driver.id == driver_id
        )
        .first()
    )


def update_driver(
    db: Session,
    driver,
    update_data: dict
):
    for key, value in update_data.items():
        setattr(driver, key, value)

    db.commit()
    db.refresh(driver)

    return driver

# ==========================================
# Trip CRUD
# ==========================================

def create_trip(
    db: Session,
    trip_data
):
    trip = Trip(
        vehicle_id=trip_data.vehicle_id,
        driver_id=trip_data.driver_id,
        source=trip_data.source,
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        expected_delivery_date=trip_data.expected_delivery_date,
        distance=trip_data.distance,
        trip_status="Scheduled"
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)

    return trip


def get_trips(
    db: Session
):
    return (
        db.query(Trip)
        .order_by(Trip.id.desc())
        .all()
    )


def get_trip_by_id(
    db: Session,
    trip_id: int
):
    return (
        db.query(Trip)
        .filter(
            Trip.id == trip_id
        )
        .first()
    )


def update_trip_status(
    db: Session,
    trip,
    status: str
):
    trip.trip_status = status

    db.commit()
    db.refresh(trip)

    return trip

# ==========================================
# Fuel CRUD
# ==========================================

def create_fuel(
    db: Session,
    fuel_data,
    total_cost: float
):
    fuel = Fuel(
        vehicle_id=fuel_data.vehicle_id,
        trip_id=fuel_data.trip_id,
        fuel_type=fuel_data.fuel_type,
        quantity=fuel_data.quantity,
        price_per_litre=fuel_data.price_per_litre,
        total_cost=total_cost,
        fuel_date=fuel_data.fuel_date
    )

    db.add(fuel)
    db.commit()
    db.refresh(fuel)

    return fuel


def get_fuel_records(
    db: Session
):
    return (
        db.query(Fuel)
        .order_by(Fuel.id.desc())
        .all()
    )


def get_vehicle_fuel_history(
    db: Session,
    vehicle_id: int
):
    return (
        db.query(Fuel)
        .filter(
            Fuel.vehicle_id == vehicle_id
        )
        .order_by(
            Fuel.fuel_date.desc()
        )
        .all()
    )

# ==========================================
# Maintenance CRUD
# ==========================================

def create_maintenance(
    db: Session,
    maintenance_data
):
    maintenance = Maintenance(
        vehicle_id=maintenance_data.vehicle_id,
        service_type=maintenance_data.service_type,
        service_date=maintenance_data.service_date,
        service_cost=maintenance_data.service_cost,
        current_km=maintenance_data.current_km,
        description=maintenance_data.description,
        status="Scheduled"
    )

    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)

    return maintenance


def get_maintenance_records(
    db: Session
):
    return (
        db.query(Maintenance)
        .order_by(
            Maintenance.id.desc()
        )
        .all()
    )


def get_maintenance_by_id(
    db: Session,
    maintenance_id: int
):
    return (
        db.query(Maintenance)
        .filter(
            Maintenance.id == maintenance_id
        )
        .first()
    )


def get_vehicle_maintenance(
    db: Session,
    vehicle_id: int
):
    return (
        db.query(Maintenance)
        .filter(
            Maintenance.vehicle_id == vehicle_id
        )
        .order_by(
            Maintenance.service_date.desc()
        )
        .all()
    )


def update_maintenance(
    db: Session,
    maintenance,
    update_data
):
    update_values = update_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_values.items():
        setattr(
            maintenance,
            field,
            value
        )

    db.commit()
    db.refresh(maintenance)

    return maintenance

# ==========================================
# Trip Tracking CRUD
# ==========================================

def create_tracking(
    db: Session,
    trip_id: int,
    tracking_data
):
    tracking = TripTracking(
        trip_id=trip_id,
        location=tracking_data.location,
        status=tracking_data.status,
        remarks=tracking_data.remarks,
        timestamp=tracking_data.timestamp
    )

    db.add(tracking)
    db.commit()
    db.refresh(tracking)

    return tracking


def get_trip_tracking(
    db: Session,
    trip_id: int
):
    return (
        db.query(TripTracking)
        .filter(
            TripTracking.trip_id == trip_id
        )
        .order_by(
            TripTracking.timestamp.asc()
        )
        .all()
    )