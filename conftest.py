import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db


# ==========================================
# Test Database Configuration
# ==========================================

TEST_DATABASE_URL = (
    "postgresql://postgres:Srik8499@localhost:5433/"
    "logistics_fleet_test"
)


# ==========================================
# Test Database Engine
# ==========================================

test_engine = create_engine(
    TEST_DATABASE_URL
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# ==========================================
# Create Test Tables
# ==========================================

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


# ==========================================
# Database Session
# ==========================================

@pytest.fixture
def db():

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


# ==========================================
# Override FastAPI Database
# ==========================================

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ==========================================
# Test Client
# ==========================================

@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client