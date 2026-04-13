"""
Critical business-logic tests for the Hardware Hub API.

These tests verify the rental guards, authentication, and admin-only operations
that form the core of the application's correctness.
"""

from fastapi.testclient import TestClient
from conftest import auth_header


class TestAuthentication:
    """Login, token validation, and access control."""

    def test_login_valid_credentials(self, client: TestClient):
        resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["is_admin"] is True

    def test_login_invalid_credentials(self, client: TestClient):
        resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401
        assert "Invalid" in resp.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        resp = client.post("/api/auth/login", json={"username": "ghost", "password": "nope"})
        assert resp.status_code == 401

    def test_protected_endpoint_without_token(self, client: TestClient):
        resp = client.get("/api/hardware")
        assert resp.status_code == 401


class TestRentalGuards:
    """Core guards that prevent impossible rental states."""

    def test_cannot_rent_hardware_in_repair(self, client: TestClient, user_token: str):
        """
        CRITICAL: A device in 'Repair' status must not be rentable.
        This prevents issuing broken/unsafe equipment to employees.
        """
        # Hardware ID 3 is seeded with status='Repair'
        resp = client.post("/api/hardware/3/rent", headers=auth_header(user_token))
        assert resp.status_code == 400
        assert "repair" in resp.json()["detail"].lower()

    def test_cannot_rent_hardware_already_in_use(self, client: TestClient, user_token: str):
        """
        CRITICAL: A device already rented ('In Use') cannot be rented again.
        This prevents double-booking of equipment.
        """
        # Hardware ID 2 is seeded with status='In Use'
        resp = client.post("/api/hardware/2/rent", headers=auth_header(user_token))
        assert resp.status_code == 400
        assert "already rented" in resp.json()["detail"].lower()

    def test_cannot_rent_hardware_with_unknown_status(self, client: TestClient, user_token: str):
        """
        CRITICAL: A device with 'Unknown' status cannot be rented.
        Unknown devices need identification before being issued.
        """
        # Hardware ID 4 is seeded with status='Unknown'
        resp = client.post("/api/hardware/4/rent", headers=auth_header(user_token))
        assert resp.status_code == 400
        assert "unknown" in resp.json()["detail"].lower()

    def test_successful_rent_available_hardware(self, client: TestClient, user_token: str):
        """An available device can be rented successfully."""
        # Hardware ID 1 is seeded with status='Available'
        resp = client.post("/api/hardware/1/rent", headers=auth_header(user_token))
        assert resp.status_code == 200
        rental = resp.json()
        assert rental["hardware_id"] == 1
        assert rental["return_date"] is None

        # Verify status changed to 'In Use'
        hw_resp = client.get("/api/hardware", headers=auth_header(user_token))
        item = next(h for h in hw_resp.json() if h["id"] == 1)
        assert item["status"] == "In Use"

    def test_cannot_return_available_hardware(self, client: TestClient, user_token: str):
        """Cannot return a device that is not currently rented."""
        # Hardware ID 1 is 'Available' — not rented
        resp = client.post("/api/hardware/1/return", headers=auth_header(user_token))
        assert resp.status_code == 400
        assert "not currently rented" in resp.json()["detail"].lower()

    def test_rent_then_return_flow(self, client: TestClient, user_token: str):
        """Full rental lifecycle: rent → verify In Use → return → verify Available."""
        # Rent
        resp = client.post("/api/hardware/1/rent", headers=auth_header(user_token))
        assert resp.status_code == 200

        # Return
        resp = client.post("/api/hardware/1/return", headers=auth_header(user_token))
        assert resp.status_code == 200
        assert resp.json()["return_date"] is not None

        # Verify status is back to Available
        hw_resp = client.get("/api/hardware", headers=auth_header(user_token))
        item = next(h for h in hw_resp.json() if h["id"] == 1)
        assert item["status"] == "Available"

    def test_cannot_rent_nonexistent_hardware(self, client: TestClient, user_token: str):
        resp = client.post("/api/hardware/999/rent", headers=auth_header(user_token))
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN-ONLY OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdminOperations:
    """Verify that admin-only endpoints reject non-admin users."""

    def test_regular_user_cannot_create_hardware(self, client: TestClient, user_token: str):
        resp = client.post(
            "/api/hardware",
            headers=auth_header(user_token),
            json={"name": "New Device", "brand": "Test", "status": "Available"},
        )
        assert resp.status_code == 403

    def test_regular_user_cannot_delete_hardware(self, client: TestClient, user_token: str):
        resp = client.delete("/api/hardware/1", headers=auth_header(user_token))
        assert resp.status_code == 403

    def test_regular_user_cannot_create_users(self, client: TestClient, user_token: str):
        resp = client.post(
            "/api/users",
            headers=auth_header(user_token),
            json={"username": "newuser", "password": "pass123", "is_admin": False},
        )
        assert resp.status_code == 403

    def test_admin_can_create_hardware(self, client: TestClient, admin_token: str):
        resp = client.post(
            "/api/hardware",
            headers=auth_header(admin_token),
            json={"name": "New Laptop", "brand": "Dell", "status": "Available"},
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "New Laptop"

    def test_admin_can_toggle_repair_status(self, client: TestClient, admin_token: str):
        # Set Available → Repair
        resp = client.patch(
            "/api/hardware/1/status",
            headers=auth_header(admin_token),
            json={"status": "Repair"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "Repair"

        # Set Repair → Available
        resp = client.patch(
            "/api/hardware/1/status",
            headers=auth_header(admin_token),
            json={"status": "Available"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "Available"

    def test_admin_can_create_user(self, client: TestClient, admin_token: str):
        resp = client.post(
            "/api/users",
            headers=auth_header(admin_token),
            json={"username": "new.employee", "password": "secure123", "is_admin": False},
        )
        assert resp.status_code == 201
        assert resp.json()["username"] == "new.employee"
        assert resp.json()["is_admin"] is False

    def test_cannot_delete_primary_admin(self, client: TestClient, admin_token: str):
        resp = client.delete("/api/users/1", headers=auth_header(admin_token))
        assert resp.status_code == 400
        assert "primary admin" in resp.json()["detail"].lower()


# ═══════════════════════════════════════════════════════════════════════════════
#  AI ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestAIEndpoints:
    """Verify AI search and audit endpoints return meaningful results."""

    def test_semantic_search_mobile(self, client: TestClient, user_token: str):
        resp = client.post(
            "/api/ai/search",
            headers=auth_header(user_token),
            json={"query": "I need something to test a mobile app"},
        )
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) > 0
        names = [r["name"].lower() for r in results]
        assert any("iphone" in n or "galaxy" in n for n in names)

    def test_semantic_search_empty_query(self, client: TestClient, user_token: str):
        resp = client.post(
            "/api/ai/search",
            headers=auth_header(user_token),
            json={"query": "xyznonexistent"},
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_audit_returns_flags(self, client: TestClient, user_token: str):
        resp = client.get("/api/ai/audit", headers=auth_header(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "flags" in data
        assert "summary" in data
        assert isinstance(data["flags"], list)
