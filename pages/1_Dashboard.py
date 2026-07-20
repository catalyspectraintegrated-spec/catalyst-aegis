import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.graph_objects as go
from datetime import datetime
import json, os

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

DB_FILE = "trading_data.db"
TRADE_LOG_FILE = "trade_log.json"
EMERGENCY_STOP_FILE = "emergency_stop.flag"

# Only create engine — don't fail if database is empty
try:
    engine = create_engine(f"sqlite:///{DB_FILE}")
except:
    engine = None

ALL_ASSETS = {
    "EUR/USD": ("eur_usd_h1","eur_usd_m15","forex"),
    "GBP/USD": ("gbp_usd_h1","gbp_usd_m15","forex"),
    "USD/JPY": ("usd_jpy_h1","usd_jpy_m15","forex"),
    "AUD/USD": ("aud_usd_h1","aud_usd_m15","forex"),
    "EUR/JPY": ("eur_jpy_h1","eur_jpy_m15","forex"),
    "GBP/JPY": ("gbp_jpy_h1","gbp_jpy_m15","forex"),
    "BTC/USD": ("btc_usd_h1","btc_usd_m15","crypto"),
    "ETH/USD": ("eth_usd_h1","eth_usd_m15","crypto"),
    "BNB/USD": ("bnb_usd_h1","bnb_usd_m15","crypto"),
    "SOL/USD": ("sol_usd_h1","sol_usd_m15","crypto"),
}

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

all_names = list(ALL_ASSETS.keys())
selected = st.sidebar.multiselect("Active Assets", all_names, default=all_names[:10])
view = st.sidebar.selectbox("View Chart", selected, index=0) if selected else all_names[0]
h1t, m15t, _ = ALL_ASSETS.get(view, ALL_ASSETS[all_names[0]])
tf = st.sidebar.radio("Timeframe", ["1 Hour","15 Minutes"])
days = st.sidebar.slider("History (days)", 1, 180, 30)

# Try to load data — show clear message if it fails
table = h1t if tf == "1 Hour" else m15t

try:
    df = pd.read_sql(f"SELECT * FROM {table} WHERE time >= datetime('now','-{days} days') ORDER BY time ASC", 
                     engine, index_col="time", parse_dates=True)
except Exception as e:
    st.warning("📡 Market data is loading. This takes 1-2 minutes on first run.")
    st.info("The platform is downloading historical data for 10 assets. Please wait and refresh.")
    
    # Show a simple placeholder
    st.markdown("---")
    st.markdown("### ⏳ Data Loading In Progress...")
    st.markdown("""
    Catalyst AEGIS is fetching market data for all 10 assets. This happens once.
    - EUR/USD, GBP/USD, USD/JPY, AUD/USD, EUR/JPY, GBP/JPY
    - BTC/USD, ETH/USD, BNB/USD, SOL/USD
    
    **Refresh this page in 2 minutes.**
    """)
    st.stop()

if df.empty:
    st.warning("📡 No data available yet. Data is being fetched — please refresh in 2 minutes.")
    st.stop()

# Calculate indicators
df['MA20'] = df['close'].rolling(20).mean()
df['MA50'] = df['close'].rolling(50).mean()
delta = df['close'].diff(); gain=delta.where(delta>0,0); loss=-delta.where(delta<0,0)
df['RSI'] = (100-(100/(1+(gain.rolling(14).mean()/loss.rolling(14).mean().replace(0,np.nan))))).fillna(50)

cur = df['close'].iloc[-1]
pct = ((cur-df['close'].iloc[-2])/df['close'].iloc[-2]*100) if len(df)>1 else 0
h = df['high'].iloc[-24:].max() if tf=="1 Hour" else df['high'].iloc[-96:].max()
l = df['low'].iloc[-24:].min() if tf=="1 Hour" else df['low'].iloc[-96:].min()
v = df['volume'].iloc[-24:].sum() if tf=="1 Hour" else df['volume'].iloc[-96:].sum()
pf = "{:.3f}" if "JPY" in view else ("{:.5f}" if any(x in view for x in ["EUR","GBP","AUD"]) else "${:,.2f}")

st.title("📊 Live Dashboard")
st.caption(f"Monitoring {len(selected)} assets | {datetime.now().strftime('%H:%M:%S')}")

if not is_verified:
    st.warning("🔒 Viewing in read-only mode. Sign up and verify your email to start trading.")

c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("Price", pf.format(cur), f"{pct:+.2f}%")
with c2: st.metric("24h High", pf.format(h))
with c3: st.metric("24h Low", pf.format(l))
with c4: st.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
with c5: st.metric("Volume", f"{v:,.0f}")

st.markdown("---")
st.subheader("📡 Live Monitor")
lc1,lc2,lc3,lc4 = st.columns(4)

# Trade log
trades = []
if os.path.exists(TRADE_LOG_FILE):
    with open(TRADE_LOG_FILE) as f:
        data = json.load(f)
        trades = data.get("trades",[])

ft = [t for t in trades if t.get("symbol") in selected]
ot = [t for t in ft if t.get("status")=="open"]
closed = [t for t in ft if t.get("status")=="closed"]
pnl_total = sum(t.get("pnl",0) for t in closed)
eq = 10000+pnl_total
w = sum(1 for t in closed if t.get("pnl",0)>0)
wr = w/len(closed)*100 if closed else 0

with lc1: st.metric("Equity", f"${eq:,.2f}", f"${pnl_total:+,.2f}")
with lc2:
    if ot:
        for t in ot[:5]: st.write(f"{'🟢' if t.get('pnl',0)>0 else '🔴'} {t['symbol']}")
    else: st.info("No open positions")
with lc3: st.metric("Trades", len(closed)); st.metric("Win Rate", f"{wr:.1f}%")
with lc4:
    st.markdown("**Trading Controls**")
    if not is_verified:
        st.info("🔒 Sign up to trade")
    elif ot:
        st.markdown("🟢 **LIVE TRADE ACTIVE**")
        if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
            with open(EMERGENCY_STOP_FILE,'w') as f: f.write(datetime.now().isoformat())
            st.rerun()
    else:
        st.markdown("⚪ Idle — Monitoring")

# Chart
st.markdown("---")
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
    name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'))
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='MA 20', line=dict(color='#FFA000',width=1.5)))
fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines', name='MA 50', line=dict(color='#1565C0',width=1.5)))
fig.update_layout(title=f"{view} — {tf}", height=450, xaxis_rangeslider_visible=False,
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1), margin=dict(l=0,r=0,t=40,b=0))
st.plotly_chart(fig, use_container_width=True)

from mobile_css import add_mobile_css
add_mobile_css()
from aegis_chat import render_chat
render_chat()
