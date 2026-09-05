import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-harvestos")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app, limiter


TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "admin@example.com",
            "password": "StrongAdminPass!123",
            "full_name": "Admin User",
        },
    )
    assert response.status_code == 200
    login = client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "StrongAdminPass!123"},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
