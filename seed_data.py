"""Quick data seeder — downloads minimal data for immediate dashboard display."""
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text

DB_FILE = "trading_data.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

# Download just 7 days of 1-hour data for the main assets (fast)
SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "BTC/USD": "BTC-USD", 
    "ETH/USD": "ETH-USD",
}

print("📥 Seeding data (this takes 30 seconds)...")
for name, symbol in SYMBOLS.items():
    prefix = "eur_usd" if "EUR" in name else ("btc_usd" if "BTC" in name else "eth_usd")
    table = f"{prefix}_h1"
    
    try:
        df = yf.download(symbol, period="7d", interval="1h", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df[['Open','High','Low','Close','Volume']]
            df.columns = ['open','high','low','close','volume']
            
            with engine.begin() as conn:
                for idx, row in df.iterrows():
                    conn.execute(text(f"INSERT OR REPLACE INTO {table} VALUES (:t,:o,:h,:l,:c,:v)"), {
                        "t": str(idx), "o": float(row['open']), "h": float(row['high']),
                        "l": float(row['low']), "c": float(row['close']), "v": float(row['volume'])
                    })
            print(f"  ✅ {name}: {len(df)} rows")
    except Exception as e:
        print(f"  ⚠️ {name}: {e}")

print("✅ Seed complete — dashboard will now show data")
