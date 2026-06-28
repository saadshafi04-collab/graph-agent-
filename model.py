import sqlite3 
from datetime import datetime,timedelta
import random 

DB_PATH= 'assets.db'
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT,
            measurement_type TEXT,
            value REAL,
            unit TEXT,
            recorded_at TEXT,
            utilization REAL,
            status TEXT
        )
    ''')

    assets = ["Asset_A", "Asset_B", "Asset_C", "Asset_D"]
    measurement_types = {
        "corrosion_rate": ("mm/year", 0.05, 0.5),
        "temperature": ("°C", 40, 130),
        "pressure": ("bar", 2, 15),
    }

    start_date = datetime(2026, 1, 1)

    cursor.execute("SELECT COUNT(*) FROM measurements")
    if cursor.fetchone()[0] == 0:
        for asset in assets:
            for day in range(90):
                date = start_date + timedelta(days=day)
                utilization = round(random.uniform(0, 100), 2)
                status = "idle" if utilization < 10 else "busy"

                for m_type, (unit, min_val, max_val) in measurement_types.items():
                    value = round(random.uniform(min_val, max_val), 3)
                    cursor.execute(
                        "INSERT INTO measurements (asset_name, measurement_type, value, unit, recorded_at, utilization, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (asset, m_type, value, unit, date.strftime("%Y-%m-%d"), utilization, status)
                    )

    conn.commit()
    conn.close()


def get_assets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT asset_name FROM measurements")
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]


def get_measurements(asset_name, measurement_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT recorded_at, value, utilization, status FROM measurements WHERE asset_name = ? AND measurement_type = ? ORDER BY recorded_at",
        (asset_name, measurement_type)
    )
    results = cursor.fetchall()
    conn.close()
    return [
        {"date": row[0], "value": row[1], "utilization": row[2], "status": row[3]}
        for row in results
    ]


def get_summary(asset_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT measurement_type, AVG(value), MIN(value), MAX(value), unit FROM measurements WHERE asset_name = ? GROUP BY measurement_type",
        (asset_name,)
    )
    results = cursor.fetchall()
    conn.close()
    return [
        {"type": row[0], "avg": round(row[1], 3), "min": row[2], "max": row[3], "unit": row[4]}
        for row in results
    ]


def get_status_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT asset_name, status, COUNT(*) FROM measurements GROUP BY asset_name, status"
    )
    results = cursor.fetchall()
    conn.close()
    return [
        {"asset": row[0], "status": row[1], "count": row[2]}
        for row in results
    ]

