import sqlite3
from pathlib import Path

DB_PATH = Path("sdms_system.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        department TEXT NOT NULL,
        role_name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_code TEXT UNIQUE NOT NULL,
        equipment_type TEXT NOT NULL,
        item_profile TEXT NOT NULL,
        status TEXT NOT NULL,
        condition_name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS checkout_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        equipment_id INTEGER NOT NULL,
        issued_by TEXT NOT NULL,
        checkout_condition TEXT NOT NULL,
        checkout_time TEXT NOT NULL,
        return_time TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (equipment_id) REFERENCES equipment(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS temp_workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temp_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        company_name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS temp_signins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temp_worker_id INTEGER NOT NULL,
        sign_in_time TEXT NOT NULL,
        purpose TEXT NOT NULL,
        issued_by TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (temp_worker_id) REFERENCES temp_workers(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lost_found_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        item_description TEXT NOT NULL,
        found_location TEXT NOT NULL,
        found_date TEXT NOT NULL,
        status TEXT NOT NULL,
        claimed_by TEXT,
        claimed_at TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) AS count FROM employees")
    if cur.fetchone()["count"] == 0:
        cur.executemany(
            "INSERT INTO employees (employee_id, full_name, department, role_name) VALUES (?, ?, ?, ?)",
            [
                ("E1001", "Ava Thompson", "Operations", "Warehouse Associate"),
                ("E1002", "Liam Carter", "Operations", "Warehouse Associate"),
                ("E1003", "Noah Singh", "Security", "Security Clerk"),
                ("E1004", "Mia Patel", "Operations", "Equipment Manager"),
            ],
        )

    cur.execute("SELECT COUNT(*) AS count FROM equipment")
    if cur.fetchone()["count"] == 0:
        cur.executemany(
            "INSERT INTO equipment (equipment_code, equipment_type, item_profile, status, condition_name) VALUES (?, ?, ?, ?, ?)",
            [
                ("SCN-001", "Scanner", "Zebra TC21", "Available", "Good"),
                ("SCN-002", "Scanner", "Zebra TC21", "Available", "Good"),
                ("SCN-003", "Scanner", "Zebra TC21", "Available", "Fair"),
                ("RAD-001", "Radio", "Motorola R2", "Available", "Good"),
            ],
        )

    cur.execute("SELECT COUNT(*) AS count FROM temp_workers")
    if cur.fetchone()["count"] == 0:
        cur.executemany(
            "INSERT INTO temp_workers (temp_id, full_name, company_name) VALUES (?, ?, ?)",
            [
                ("T2001", "Ethan Walker", "PeopleReady"),
                ("T2002", "Sophia Green", "Randstad"),
                ("T2003", "Mason Hall", "PeopleReady"),
            ],
        )

    cur.execute("SELECT COUNT(*) AS count FROM lost_found_items")
    if cur.fetchone()["count"] == 0:
        cur.executemany(
            "INSERT INTO lost_found_items (item_name, item_description, found_location, found_date, status, claimed_by, claimed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("Wallet", "Black leather wallet", "Lunch Room", "2026-04-10", "Unclaimed", None, None),
                ("Keys", "Key ring with 3 keys and a blue tag", "Dock Door 4", "2026-04-11", "Unclaimed", None, None),
                ("Phone", "Black iPhone with cracked case", "Aisle 7", "2026-04-12", "Unclaimed", None, None),
            ],
        )

    conn.commit()
    conn.close()
