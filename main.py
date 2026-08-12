from fastapi import FastAPI

from database import Base, engine

import models

from exceptions import register_exception_handlers

from routers.auth import router as auth_router
from routers.vehicles import router as vehicles_router
from routers.drivers import router as drivers_router
from routers.trips import router as trips_router
from routers.fuel import router as fuel_router
from routers.maintenance import router as maintenance_router
from routers.tracking import router as tracking_router
from routers.dashboard import router as dashboard_router

# ==========================================
# Create Database Tables
# ==========================================

Base.metadata.create_all(
    bind=engine
)


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="Logistics & Fleet Management System",
    description=(
        "Backend API for vehicle, driver, trip, "
        "fuel, maintenance and delivery tracking."
    ),
    version="1.0.0"
)


# ==========================================
# Exception Handlers
# ==========================================

register_exception_handlers(app)


# ==========================================
# Routers
# ==========================================

app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(drivers_router)
app.include_router(trips_router)
app.include_router(fuel_router)
app.include_router(maintenance_router)
app.include_router(tracking_router)
app.include_router(dashboard_router)

# ==========================================
# Root
# ==========================================

@app.get("/")
def root():
    return {
        "message": (
            "Logistics & Fleet Management "
            "API is running"
        )
    }