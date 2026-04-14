"""
Hardware Hub — FastAPI Backend
All endpoints match the frontend API contract exactly.
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything reads os.getenv()

import os
import re
import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import bcrypt as _bcrypt

from sqlite_db import get_db_connection, initialize_database

# ── Config ──────────────────────────────────────────────────────────────────────

JWT_SECRET = os.getenv("JWT_SECRET", "hardware-hub-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App ─────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Hardware Hub API", version="1.0.0")

ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
if ALLOWED_ORIGINS_ENV:
    _origins = [o.strip() for o in ALLOWED_ORIGINS_ENV.split(",") if o.strip()]
else:
    # Default: allow localhost + all Vercel preview/production deployments
    _origins = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    initialize_database()
    logger.info("Database initialized")


# ── Pydantic Models ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class CreateHardwareRequest(BaseModel):
    name: str
    brand: str
    purchase_date: Optional[str] = None
    status: str = "Available"
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Available", "In Use", "Repair", "Unknown"}
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v


class StatusChangeRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Available", "In Use", "Repair", "Unknown"}
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v


class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class SearchRequest(BaseModel):
    query: str


# ── Auth Helpers ────────────────────────────────────────────────────────────────

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print("TOKEN DECODE ERROR:", e)
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    return decode_token(token)


def get_current_user(user_id: int = Depends(get_current_user_id)) -> dict:
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return dict(row)


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def format_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "username": row["username"],
        "is_admin": bool(row["is_admin"]),
        "created_at": row["created_at"],
    }


def format_hardware(row: dict) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "brand": row["brand"],
        "purchase_date": row["purchase_date"],
        "status": row["status"],
        "notes": row["notes"],
        "assigned_to": row["assigned_to"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def format_rental(row: dict) -> dict:
    return {
        "id": row["id"],
        "hardware_id": row["hardware_id"],
        "user_id": row["user_id"],
        "rent_date": row["rent_date"],
        "return_date": row["return_date"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/auth/login")
def login(body: LoginRequest):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (body.username,)
        ).fetchone()

    if not row or not _bcrypt.checkpw(body.password.encode(), row["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(row["id"])
    return {"user": format_user(dict(row)), "token": token}


@app.post("/api/auth/logout")
def logout(user: dict = Depends(get_current_user)):
    # Stateless JWT — no server-side invalidation needed for MVP
    return {"ok": True}


@app.get("/api/auth/me")
def me(user: dict = Depends(get_current_user)):
    return format_user(user)


# ═══════════════════════════════════════════════════════════════════════════════
#  HARDWARE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/hardware")
def list_hardware(user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM hardware ORDER BY name ASC").fetchall()
    return [format_hardware(dict(r)) for r in rows]


@app.post("/api/hardware", status_code=201)
def create_hardware(body: CreateHardwareRequest, admin: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO hardware (name, brand, purchase_date, status, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (body.name, body.brand, body.purchase_date, body.status, body.notes),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM hardware WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return format_hardware(dict(row))


@app.delete("/api/hardware/{hardware_id}")
def delete_hardware(hardware_id: int, admin: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM hardware WHERE id = ?", (hardware_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Hardware not found")
        conn.execute("DELETE FROM hardware WHERE id = ?", (hardware_id,))
        conn.commit()
    return {"ok": True}


@app.patch("/api/hardware/{hardware_id}/status")
def change_hardware_status(
    hardware_id: int,
    body: StatusChangeRequest,
    admin: dict = Depends(require_admin),
):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM hardware WHERE id = ?", (hardware_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Hardware not found")

        old_status = row["status"]

        # Update status
        conn.execute(
            "UPDATE hardware SET status = ? WHERE id = ?",
            (body.status, hardware_id),
        )

        # If moving to Available, clear assigned_to
        if body.status == "Available":
            conn.execute("UPDATE hardware SET assigned_to = NULL WHERE id = ?", (hardware_id,))

        # Log history
        conn.execute(
            """
            INSERT INTO hardware_history (hardware_id, old_status, new_status, changed_by)
            VALUES (?, ?, ?, ?)
            """,
            (hardware_id, old_status, body.status, admin["id"]),
        )

        conn.commit()
        updated = conn.execute("SELECT * FROM hardware WHERE id = ?", (hardware_id,)).fetchone()
    return format_hardware(dict(updated))


@app.post("/api/hardware/{hardware_id}/rent")
def rent_hardware(hardware_id: int, user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM hardware WHERE id = ?", (hardware_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Hardware not found")

        item = dict(row)

        # ── Business logic guards ──
        if item["status"] == "Repair":
            raise HTTPException(status_code=400, detail="Cannot rent equipment that is under repair")
        if item["status"] == "In Use":
            raise HTTPException(status_code=400, detail="This item is already rented by someone")
        if item["status"] == "Unknown":
            raise HTTPException(status_code=400, detail="Cannot rent equipment with unknown status")
        if item["status"] != "Available":
            raise HTTPException(status_code=400, detail=f"Cannot rent item with status '{item['status']}'")

        # Update hardware
        conn.execute(
            "UPDATE hardware SET status = 'In Use', assigned_to = ? WHERE id = ?",
            (user["id"], hardware_id),
        )

        # Create rental record
        cursor = conn.execute(
            "INSERT INTO rentals (hardware_id, user_id) VALUES (?, ?)",
            (hardware_id, user["id"]),
        )

        # Log history
        conn.execute(
            """
            INSERT INTO hardware_history (hardware_id, old_status, new_status, change_note, changed_by)
            VALUES (?, ?, 'In Use', ?, ?)
            """,
            (hardware_id, item["status"], f"Rented by {user['username']}", user["id"]),
        )

        conn.commit()

        rental = conn.execute("SELECT * FROM rentals WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return format_rental(dict(rental))


@app.post("/api/hardware/{hardware_id}/return")
def return_hardware(hardware_id: int, user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM hardware WHERE id = ?", (hardware_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Hardware not found")

        item = dict(row)

        # ── Business logic guards ──
        if item["status"] != "In Use":
            raise HTTPException(status_code=400, detail="This item is not currently rented")

        # Only the assignee or an admin can return
        if item["assigned_to"] != user["id"] and not user["is_admin"]:
            raise HTTPException(status_code=403, detail="You can only return items assigned to you")

        # Update hardware
        conn.execute(
            "UPDATE hardware SET status = 'Available', assigned_to = NULL WHERE id = ?",
            (hardware_id,),
        )

        # Close rental record
        conn.execute(
            """
            UPDATE rentals SET return_date = CURRENT_TIMESTAMP
            WHERE hardware_id = ? AND return_date IS NULL
            """,
            (hardware_id,),
        )

        # Log history
        conn.execute(
            """
            INSERT INTO hardware_history (hardware_id, old_status, new_status, change_note, changed_by)
            VALUES (?, 'In Use', 'Available', ?, ?)
            """,
            (hardware_id, f"Returned by {user['username']}", user["id"]),
        )

        conn.commit()

        rental = conn.execute(
            "SELECT * FROM rentals WHERE hardware_id = ? ORDER BY id DESC LIMIT 1",
            (hardware_id,),
        ).fetchone()
    return format_rental(dict(rental))


# ═══════════════════════════════════════════════════════════════════════════════
#  USER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/users")
def list_users(admin: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()
    return [format_user(dict(r)) for r in rows]


@app.post("/api/users", status_code=201)
def create_user(body: CreateUserRequest, admin: dict = Depends(require_admin)):
    pw_hash = _bcrypt.hashpw(body.password.encode(), _bcrypt.gensalt()).decode()
    with get_db_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (body.username, pw_hash, int(body.is_admin)),
            )
            conn.commit()
        except Exception:
            raise HTTPException(status_code=400, detail=f"Username '{body.username}' already exists")
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return format_user(dict(row))


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, admin: dict = Depends(require_admin)):
    if user_id == 1:
        raise HTTPException(status_code=400, detail="Cannot delete the primary admin account")
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════════════════════════════════
#  AI ENDPOINTS (Gemini-powered with keyword fallback)
# ═══════════════════════════════════════════════════════════════════════════════

from ai_service import semantic_search, inventory_audit, is_gemini_available


@app.get("/api/ai/status")
def ai_status(user: dict = Depends(get_current_user)):
    """Check if Gemini AI is configured and available."""
    return {"gemini_available": is_gemini_available()}


@app.post("/api/ai/search")
def ai_search(body: SearchRequest, user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        all_items = conn.execute("SELECT * FROM hardware ORDER BY name").fetchall()

    items = [dict(r) for r in all_items]
    results = semantic_search(body.query, items)
    return [format_hardware(h) for h in results]


@app.get("/api/ai/audit")
def ai_audit(user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        all_items = conn.execute("SELECT * FROM hardware").fetchall()

    items = [dict(r) for r in all_items]
    return inventory_audit(items)

