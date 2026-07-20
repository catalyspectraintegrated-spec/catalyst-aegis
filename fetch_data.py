"""
Catalyst AEGIS - Initial Data Fetcher
Downloads market data on first run.
"""
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

DB_FILE = "trading_data.db"

SYMBOLS = [
    ("EURUSD=X", "eur_usd"),
    ("GBPUSD=X", "gbp_usd"),
    ("USDJPY=X", "usd_jpy"),
    ("AUDUSD=X", "aud_usd"),
    ("EURJPY=X", "eur_jpy"),
    ("GBPJPY=X", "gbp_jpy"),
    ("BTC-USD", "btc_usd"),
    ("ETH-USD", "eth_usd"),
    ("BNB-USD", "bnb_usd"),
    ("SOL-USD", "sol_usd"),
]

def fetch_and_store(symbol, prefix, period="60d"):
    """Download and store data for a symbol."""
    engine = create_engine(f"sqlite:///{DB_FILE}")
    
    for interval, suffix in [("1h", "h1"), ("15m", "m15")]:
        table = f"{prefix}_{suffix}"
        
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if df.empty:
                continue
            
            # Flatten columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            with engine.begin() as conn:
                for idx, row in df.iterrows():
                    conn.execute(text(f"""
                        INSERT OR REPLACE INTO {table} (time, open, high, low, close, volume)
                        VALUES (:t, :o, :h, :l, :c, :v)
                    """), {
                        "t": str(idx),
                        "o": float(row['open']),
                        "h": float(row['high']),
                        "l": float(row['low']),
                        "c": float(row['close']),
                        "v": float(row['volume'])
                    })
            
            print(f"  ✅ {table}: {len(df)} rows")
        except Exception as e:
            print(f"  ⚠️ {table}: {e}")

def fetch_all():
    """Fetch data for all symbols."""
    print("📥 Fetching market data...")
    for symbol, prefix in SYMBOLS:
        print(f"  {prefix}...")
        fetch_and_store(symbol, prefix)
    print("✅ Data fetch complete")

if __name__ == "__main__":
    fetch_all()
