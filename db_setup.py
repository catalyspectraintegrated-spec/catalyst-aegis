"""
Catalyst AEGIS - Database Setup
Creates all required tables on fresh deployments.
"""
import os
from sqlalchemy import create_engine, text

DB_FILE = "trading_data.db"

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

def init_database():
    """Create all tables if they don't exist."""
    engine = create_engine(f"sqlite:///{DB_FILE}")
    with engine.begin() as conn:
        for table in TABLES:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    time DATETIME PRIMARY KEY,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL
                )
            """))
    print(f"✅ Database ready: {len(TABLES)} tables available")

if __name__ == "__main__":
    init_database()
