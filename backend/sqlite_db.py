import sqlite3
import os
import logging
from pathlib import Path
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS hardware (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        brand TEXT CHECK(length(brand) > 0),
        purchase_date DATE,
        status TEXT NOT NULL CHECK(status IN ('Available', 'In Use', 'Repair', 'Unknown')),
        notes TEXT,
        assigned_to INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assigned_to) REFERENCES users(id)
    );

    CREATE TRIGGER IF NOT EXISTS update_hardware_timestamp
    AFTER UPDATE ON hardware
    BEGIN
        UPDATE hardware SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

    CREATE TABLE IF NOT EXISTS hardware_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hardware_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT,
        change_note TEXT,
        changed_by INTEGER,
        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hardware_id) REFERENCES hardware(id) ON DELETE CASCADE,
        FOREIGN KEY (changed_by) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hardware_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        return_date DATETIME,
        FOREIGN KEY (hardware_id) REFERENCES hardware (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_rentals_active 
    ON rentals(hardware_id) 
    WHERE return_date IS NULL;

    CREATE INDEX IF NOT EXISTS idx_hardware_status ON hardware(status);
    CREATE INDEX IF NOT EXISTS idx_hardware_assigned_to ON hardware(assigned_to);
    CREATE INDEX IF NOT EXISTS idx_hardware_history_hw_id ON hardware_history(hardware_id);
    CREATE INDEX IF NOT EXISTS idx_hardware_history_changed_by ON hardware_history(changed_by);
'''

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / 'hardware_hub.db'

def get_db_path() -> Path:
    return Path(os.getenv('HARDWARE_HUB_DB_PATH', str(DEFAULT_DB_PATH)))

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def initialize_database() -> None:
    try:
        with get_db_connection() as conn:
            conn.executescript(CREATE_TABLE_SQL)
            conn.commit()
        logger.info("Baza danych została pomyślnie zainicjowana.")
    except sqlite3.Error as e:
        logger.error(f"Błąd podczas inicjalizacji bazy danych: {e}")
        raise 

if __name__ == "__main__":
    initialize_database()