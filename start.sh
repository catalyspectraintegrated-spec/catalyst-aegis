#!/bin/bash
python -c "
from sqlalchemy import create_engine, text
import os
DB_FILE = 'trading_data.db'
if not os.path.exists(DB_FILE):
    engine = create_engine(f'sqlite:///{DB_FILE}')
    tables = ['eur_usd_h1','eur_usd_m15','gbp_usd_h1','gbp_usd_m15','usd_jpy_h1','usd_jpy_m15','aud_usd_h1','aud_usd_m15','eur_jpy_h1','eur_jpy_m15','gbp_jpy_h1','gbp_jpy_m15','btc_usd_h1','btc_usd_m15','eth_usd_h1','eth_usd_m15','bnb_usd_h1','bnb_usd_m15','sol_usd_h1','sol_usd_m15']
    with engine.begin() as conn:
        for t in tables:
            conn.execute(text(f'CREATE TABLE IF NOT EXISTS {t} (time DATETIME PRIMARY KEY, open REAL, high REAL, low REAL, close REAL, volume REAL)'))
    print('Database ready')
"
streamlit run Home.py --server.headless true --server.port $PORT --server.address 0.0.0.0
