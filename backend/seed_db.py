import json
import sqlite3
import logging
from pathlib import Path
import bcrypt
from sqlite_db import get_db_connection, initialize_database, get_db_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
SEED_JSON_PATH = BASE_DIR / 'seed.json'

# Default users with passwords
DEFAULT_USERS = [
    {"username": "admin", "password": "admin123", "is_admin": True},
    {"username": "j.doe", "password": "password123", "is_admin": False},
    {"username": "a.smith", "password": "password123", "is_admin": False},
]


def seed_users(conn: sqlite3.Connection) -> dict[str, int]:
    """Seed default users and return username->id map."""
    cursor = conn.cursor()
    user_map: dict[str, int] = {}

    for u in DEFAULT_USERS:
        pw_hash = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt()).decode()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (u["username"], pw_hash, int(u["is_admin"])),
            )
            user_id = cursor.lastrowid
            logger.info(f"Created user: {u['username']} (id={user_id})")
        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM users WHERE username = ?", (u["username"],))
            user_id = cursor.fetchone()[0]
            logger.info(f"User already exists: {u['username']} (id={user_id})")

        user_map[u["username"]] = user_id

    conn.commit()
    return user_map


def extract_username_from_email(email: str) -> str:
    """Extract username from email address."""
    if '@' in email:
        return email.split('@')[0]
    return email


def seed_hardware(conn: sqlite3.Connection, hardware_data: list, user_map: dict[str, int]) -> None:
    """Populate hardware table with seed data."""
    cursor = conn.cursor()

    valid_statuses = {
        'available': 'Available',
        'in use': 'In Use',
        'repair': 'Repair',
        'unknown': 'Unknown',
    }

    for item in hardware_data:
        raw_status = str(item.get('status', 'Unknown')).lower()
        status = valid_statuses.get(raw_status, 'Unknown')

        # Build notes from notes + history fields
        notes_parts = []
        if item.get('notes'):
            notes_parts.append(item['notes'])
        if item.get('history'):
            notes_parts.append(item['history'])
        notes = '. '.join(notes_parts) if notes_parts else None

        try:
            # Handle assigned_to field
            assigned_to = None
            if 'assignedTo' in item and item['assignedTo']:
                username = extract_username_from_email(item['assignedTo'])
                assigned_to = user_map.get(username)
                if not assigned_to:
                    logger.warning(f"User '{username}' not found for hardware {item['name']}")

            cursor.execute(
                """
                INSERT INTO hardware (id, name, brand, purchase_date, status, notes, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item['id'],
                    item['name'],
                    item.get('brand', 'Unknown'),
                    item.get('purchaseDate'),
                    status,
                    notes,
                    assigned_to,
                ),
            )

            # If item is "In Use" and has assigned_to, create rental record
            if status == 'In Use' and assigned_to:
                cursor.execute(
                    "INSERT INTO rentals (hardware_id, user_id) VALUES (?, ?)",
                    (item['id'], assigned_to),
                )

            logger.info(f"Seeded hardware: {item['name']} (ID: {item['id']})")

        except sqlite3.IntegrityError as e:
            logger.warning(f"Skipped duplicate hardware (ID: {item['id']}): {e}")
        except Exception as e:
            logger.error(f"Error seeding hardware {item.get('name', 'Unknown')}: {e}")

    conn.commit()


def main():
    """Main seeding function."""
    # Delete existing DB and recreate
    db_path = get_db_path()
    if db_path.exists():
        db_path.unlink()
        logger.info(f"Deleted existing database: {db_path}")

    logger.info("Initializing database...")
    initialize_database()

    logger.info(f"Loading seed data from {SEED_JSON_PATH}...")
    with open(SEED_JSON_PATH, 'r', encoding='utf-8') as f:
        hardware_data = json.load(f)

    with get_db_connection() as conn:
        logger.info("Seeding users...")
        user_map = seed_users(conn)

        logger.info("Seeding hardware...")
        seed_hardware(conn, hardware_data, user_map)

    logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    main()
