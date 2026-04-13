"""
Shared test fixtures for Hardware Hub API tests.
Uses a temporary SQLite file database for each test function.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Create a temp file for the test DB BEFORE importing the app
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["HARDWARE_HUB_DB_PATH"] = _tmp.name

from main import app  # noqa: E402
from sqlite_db import get_db_connection, initialize_database, get_db_path  # noqa: E402
import bcrypt  # noqa: E402


@pytest.fixture(autouse=True)
def _setup_db():
    """Initialize a fresh database before each test."""
    db_path = get_db_path()

    # Wipe and recreate
    if db_path.exists():
        db_path.unlink()

    initialize_database()

    # Seed a default admin + regular user
    pw_admin = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    pw_user = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            ("admin", pw_admin),
        )
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 0)",
            ("j.doe", pw_user),
        )
        # Seed some hardware for testing
        conn.execute(
            "INSERT INTO hardware (name, brand, purchase_date, status) VALUES (?, ?, ?, ?)",
            ("Test iPhone", "Apple", "2023-01-01", "Available"),
        )
        conn.execute(
            "INSERT INTO hardware (name, brand, purchase_date, status) VALUES (?, ?, ?, ?)",
            ("Test MacBook", "Apple", "2023-06-15", "In Use"),
        )
        conn.execute(
            "INSERT INTO hardware (name, brand, purchase_date, status) VALUES (?, ?, ?, ?)",
            ("Test Mouse", "Razer", "2022-03-10", "Repair"),
        )
        conn.execute(
            "INSERT INTO hardware (name, brand, purchase_date, status) VALUES (?, ?, ?, ?)",
            ("Unknown Device", "Unknown", None, "Unknown"),
        )
        conn.commit()

    yield

    # Cleanup temp file
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def client():
    """FastAPI TestClient bound to the app."""
    return TestClient(app)


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    """Login as admin and return the JWT token."""
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["token"]


@pytest.fixture()
def user_token(client: TestClient) -> str:
    """Login as a regular user and return the JWT token."""
    resp = client.post("/api/auth/login", json={"username": "j.doe", "password": "password123"})
    assert resp.status_code == 200
    return resp.json()["token"]


def auth_header(token: str) -> dict[str, str]:
    """Build the Authorization header from a token."""
    return {"Authorization": f"Bearer {token}"}
