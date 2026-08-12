from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from models import (
    Vehicle,
    Driver,
    Trip,
    Fuel,
    Maintenance
)


# ==========================================
# Dashboard
# ==========================================

def get_dashboard_service(
    db: Session
):

    # --------------------------------------
    # Vehicles
    # --------------------------------------

    total_vehicles = (
        db.query(Vehicle)
        .count()
    )

    available_vehicles = (
        db.query(Vehicle)
        .filter(
            Vehicle.status == "Available"
        )
        .count()
    )

    vehicles_under_maintenance = (
        db.query(Vehicle)
        .filter(
            Vehicle.status == "Maintenance"
        )
        .count()
    )

    # --------------------------------------
    # Drivers
    # --------------------------------------

    total_drivers = (
        db.query(Driver)
        .count()
    )

    active_drivers = (
        db.query(Driver)
        .filter(
            Driver.status == "Active"
        )
        .count()
    )

    # --------------------------------------
    # Trips
    # --------------------------------------

    total_trips = (
        db.query(Trip)
        .count()
    )

    completed_trips = (
        db.query(Trip)
        .filter(
            Trip.trip_status == "Delivered"
        )
        .count()
    )

    cancelled_trips = (
        db.query(Trip)
        .filter(
            Trip.trip_status == "Cancelled"
        )
        .count()
    )

    # --------------------------------------
    # Fuel Expenses
    # --------------------------------------

    total_fuel_expenses = (
        db.query(
            func.coalesce(
                func.sum(Fuel.total_cost),
                0
            )
        )
        .scalar()
    )

    # --------------------------------------
    # Maintenance Expenses
    # --------------------------------------

    total_maintenance_expenses = (
        db.query(
            func.coalesce(
                func.sum(
                    Maintenance.service_cost
                ),
                0
            )
        )
        .scalar()
    )

    return {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "vehicles_under_maintenance":
            vehicles_under_maintenance,

        "total_drivers": total_drivers,
        "active_drivers": active_drivers,

        "total_trips": total_trips,
        "completed_trips": completed_trips,
        "cancelled_trips": cancelled_trips,

        "total_fuel_expenses":
            float(total_fuel_expenses or 0),

        "total_maintenance_expenses":
            float(
                total_maintenance_expenses or 0
            )
    }

# ==========================================
# Vehicle-wise Expense Report
# ==========================================

def get_vehicle_expense_report_service(
    db: Session
):

    vehicles = (
        db.query(Vehicle)
        .order_by(Vehicle.id)
        .all()
    )

    report = []

    for vehicle in vehicles:

        # ----------------------------------
        # Fuel expense
        # ----------------------------------

        fuel_expense = (
            db.query(
                func.coalesce(
                    func.sum(Fuel.total_cost),
                    0
                )
            )
            .filter(
                Fuel.vehicle_id ==
                vehicle.id
            )
            .scalar()
        )

        # ----------------------------------
        # Maintenance expense
        # ----------------------------------

        maintenance_expense = (
            db.query(
                func.coalesce(
                    func.sum(
                        Maintenance.service_cost
                    ),
                    0
                )
            )
            .filter(
                Maintenance.vehicle_id ==
                vehicle.id
            )
            .scalar()
        )

        fuel_expense = float(
            fuel_expense or 0
        )

        maintenance_expense = float(
            maintenance_expense or 0
        )

        total_expense = (
            fuel_expense +
            maintenance_expense
        )

        report.append({
            "vehicle_id": vehicle.id,
            "vehicle_number":
                vehicle.vehicle_number,
            "fuel_expense":
                fuel_expense,
            "maintenance_expense":
                maintenance_expense,
            "total_expense":
                total_expense
        })

    return report

# ==========================================
# Driver-wise Trip Report
# ==========================================

def get_driver_trip_report_service(
    db: Session
):

    drivers = (
        db.query(Driver)
        .order_by(Driver.id)
        .all()
    )

    report = []

    for driver in drivers:

        total_trips = (
            db.query(Trip)
            .filter(
                Trip.driver_id ==
                driver.id
            )
            .count()
        )

        completed_trips = (
            db.query(Trip)
            .filter(
                Trip.driver_id ==
                driver.id,
                Trip.trip_status ==
                "Delivered"
            )
            .count()
        )

        cancelled_trips = (
            db.query(Trip)
            .filter(
                Trip.driver_id ==
                driver.id,
                Trip.trip_status ==
                "Cancelled"
            )
            .count()
        )

        active_trips = (
            db.query(Trip)
            .filter(
                Trip.driver_id ==
                driver.id,
                Trip.trip_status.in_(
                    [
                        "Scheduled",
                        "Started",
                        "In Transit"
                    ]
                )
            )
            .count()
        )

        report.append({
            "driver_id": driver.id,
            "driver_name": driver.name,
            "total_trips": total_trips,
            "completed_trips":
                completed_trips,
            "cancelled_trips":
                cancelled_trips,
            "active_trips":
                active_trips
        })

    return report

# ==========================================
# Monthly Fuel Expense Report
# ==========================================

def get_monthly_fuel_report_service(
    db: Session
):

    results = (
        db.query(
            extract(
                "year",
                Fuel.fuel_date
            ).label("year"),

            extract(
                "month",
                Fuel.fuel_date
            ).label("month"),

            func.sum(
                Fuel.total_cost
            ).label("total_fuel_expense")
        )
        .group_by(
            extract(
                "year",
                Fuel.fuel_date
            ),
            extract(
                "month",
                Fuel.fuel_date
            )
        )
        .order_by(
            extract(
                "year",
                Fuel.fuel_date
            ),
            extract(
                "month",
                Fuel.fuel_date
            )
        )
        .all()
    )

    return [
        {
            "year": int(row.year),
            "month": int(row.month),
            "total_fuel_expense":
                float(
                    row.total_fuel_expense or 0
                )
        }
        for row in results
    ]

# ==========================================
# Monthly Maintenance Expense Report
# ==========================================

def get_monthly_maintenance_report_service(
    db: Session
):

    results = (
        db.query(
            extract(
                "year",
                Maintenance.service_date
            ).label("year"),

            extract(
                "month",
                Maintenance.service_date
            ).label("month"),

            func.sum(
                Maintenance.service_cost
            ).label(
                "total_maintenance_expense"
            )
        )
        .group_by(
            extract(
                "year",
                Maintenance.service_date
            ),
            extract(
                "month",
                Maintenance.service_date
            )
        )
        .order_by(
            extract(
                "year",
                Maintenance.service_date
            ),
            extract(
                "month",
                Maintenance.service_date
            )
        )
        .all()
    )

    return [
        {
            "year": int(row.year),
            "month": int(row.month),
            "total_maintenance_expense":
                float(
                    row.total_maintenance_expense
                    or 0
                )
        }
        for row in results
    ]