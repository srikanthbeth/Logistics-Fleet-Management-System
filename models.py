from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Float,
    ForeignKey
)

from sqlalchemy.sql import func

from database import Base


# ==========================================
# User Model
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False,
        default="Driver"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
# Vehicle Model
# ==========================================

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    vehicle_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    vehicle_type = Column(
        String(50),
        nullable=False
    )

    model = Column(
        String(100),
        nullable=False
    )

    manufacturing_year = Column(
        Integer,
        nullable=False
    )

    capacity = Column(
        Float,
        nullable=False
    )

    current_km = Column(
        Float,
        nullable=False,
        default=0
    )

    status = Column(
        String(30),
        nullable=False,
        default="Available"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
# Driver Model
# ==========================================

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String(20),
        nullable=False
    )

    license_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    license_expiry = Column(
        DateTime,
        nullable=False
    )

    experience = Column(
        Float,
        nullable=False,
        default=0
    )

    status = Column(
        String(30),
        nullable=False,
        default="Active"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
# Trip Model
# ==========================================

class Trip(Base):
    __tablename__ = "trips"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    driver_id = Column(
        Integer,
        ForeignKey("drivers.id"),
        nullable=False,
        index=True
    )

    source = Column(
        String(255),
        nullable=False
    )

    destination = Column(
        String(255),
        nullable=False
    )

    start_date = Column(
        DateTime,
        nullable=False
    )

    expected_delivery_date = Column(
        DateTime,
        nullable=False
    )

    distance = Column(
        Float,
        nullable=False
    )

    trip_status = Column(
        String(30),
        nullable=False,
        default="Scheduled"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
# Fuel Model
# ==========================================

class Fuel(Base):
    __tablename__ = "fuel"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    trip_id = Column(
        Integer,
        ForeignKey("trips.id"),
        nullable=False,
        index=True
    )

    fuel_type = Column(
        String(50),
        nullable=False
    )

    quantity = Column(
        Float,
        nullable=False
    )

    price_per_litre = Column(
        Float,
        nullable=False
    )

    total_cost = Column(
        Float,
        nullable=False
    )

    fuel_date = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
# Maintenance Model
# ==========================================

class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    service_type = Column(
        String(100),
        nullable=False
    )

    service_date = Column(
        DateTime,
        nullable=False
    )

    service_cost = Column(
        Float,
        nullable=False
    )

    current_km = Column(
        Float,
        nullable=False
    )

    description = Column(
        String(500),
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="Scheduled"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
# Trip Tracking Model
# ==========================================

class TripTracking(Base):
    __tablename__ = "trip_tracking"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    trip_id = Column(
        Integer,
        ForeignKey("trips.id"),
        nullable=False,
        index=True
    )

    location = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    remarks = Column(
        String(500),
        nullable=True
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )