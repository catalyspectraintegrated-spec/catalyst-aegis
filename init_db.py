import os
from sqlalchemy import create_engine, text

DB_FILE = "trading_data.db"

if not os.path.exists(DB_FILE):
    print("Creating new database...")
    engine = create_engine(f"sqlite:///{DB_FILE}")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eur_usd_h1 (
                time DATETIME PRIMARY KEY,
                open REAL, high REAL, low REAL, close REAL, volume INTEGER
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eur_usd_m15 (
                time DATETIME PRIMARY KEY,
                open REAL, high REAL, low REAL, close REAL, volume INTEGER
            )
        """))
    print("Database initialized")

# Create tables for all assets
TABLES = [
    "eur_usd_h1", "eur_usd_m15",
    "gbp_usd_h1", "gbp_usd_m15",
    "usd_jpy_h1", "usd_jpy_m15",
    "aud_usd_h1", "aud_usd_m15",
    "eur_jpy_h1", "eur_jpy_m15",
    "gbp_jpy_h1", "gbp_jpy_m15",
    "btc_usd_h1", "btc_usd_m15",
    "eth_usd_h1", "eth_usd_m15",
    "bnb_usd_h1", "bnb_usd_m15",
    "sol_usd_h1", "sol_usd_m15",
]

engine = create_engine(f"sqlite:///{DB_FILE}")
with engine.begin() as conn:
    for table in TABLES:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                time DATETIME PRIMARY KEY,
                open REAL, high REAL, low REAL, close REAL, volume REAL
            )
        """))
print(f"All {len(TABLES)} tables ready.")
