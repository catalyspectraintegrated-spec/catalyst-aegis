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
engine = create_engine(f"sqlite:///{DB_FILE}")

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

def load_trade_log():
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE) as f: return json.load(f)
    return {"trades":[],"account_snapshot":{},"last_updated":""}

def emergency_stop_active(): return os.path.exists(EMERGENCY_STOP_FILE)
def trigger_emergency_stop():
    with open(EMERGENCY_STOP_FILE,'w') as f: f.write(datetime.now().isoformat())
def clear_emergency_stop():
    if os.path.exists(EMERGENCY_STOP_FILE): os.remove(EMERGENCY_STOP_FILE)

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

all_names = list(ALL_ASSETS.keys())
selected = st.sidebar.multiselect("Active Assets", all_names, default=all_names[:10])
view = st.sidebar.selectbox("View Chart", selected, index=0) if selected else all_names[0]
h1t, m15t, _ = ALL_ASSETS.get(view, ALL_ASSETS[all_names[0]])
tf = st.sidebar.radio("Timeframe", ["1 Hour","15 Minutes"])
days = st.sidebar.slider("History (days)", 1, 180, 30)

stopped = emergency_stop_active()
if not is_verified:
    st.sidebar.warning("⚠️ Sign up & verify to trade")
elif stopped:
    st.sidebar.error("🚨 EMERGENCY STOP ACTIVE")
    if st.sidebar.button("✅ Resume Trading", use_container_width=True):
        clear_emergency_stop()
        st.rerun()
else:
    st.sidebar.success("🟢 Engine Running")

trade_log = load_trade_log()

@st.cache_data(ttl=60)
def load_data(t, d):
    return pd.read_sql(f"SELECT * FROM {t} WHERE time >= datetime('now','-{d} days') ORDER BY time ASC", engine, index_col="time", parse_dates=True)

df = load_data(h1t if tf=="1 Hour" else m15t, days)
if df.empty: st.error("No data"); st.stop()

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
if stopped:
    st.error("🚨 EMERGENCY STOP IS ACTIVE — NO NEW TRADES WILL BE OPENED")

c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("Price", pf.format(cur), f"{pct:+.2f}%")
with c2: st.metric("24h High", pf.format(h))
with c3: st.metric("24h Low", pf.format(l))
with c4: st.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
with c5: st.metric("Volume", f"{v:,.0f}")

st.markdown("---")
st.subheader("📡 Live Monitor")
lc1,lc2,lc3,lc4 = st.columns(4)

trades = trade_log.get("trades",[])
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
    elif stopped:
        st.error("🛑 STOPPED")
    elif ot:
        st.markdown("🟢 **LIVE TRADE ACTIVE**")
        if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
            trigger_emergency_stop()
            st.rerun()
    else:
        st.markdown("⚪ Idle — Monitoring")
        if st.button("▶️ Start Trading", type="primary", use_container_width=True, disabled=not is_verified):
            st.success("Engine is running — waiting for entry signals")

if ft:
    st.markdown("---"); st.subheader("Recent Trades")
    rows = [{"Time":t.get("entry_time","")[:16],"Symbol":t.get("symbol",""),"P&L":f"${t.get('pnl',0):+,.2f}","Reason":t.get("exit_reason","")} for t in ft[-15:]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("---")
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
    name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'))
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='MA 20', line=dict(color='#FFA000',width=1.5)))
fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines', name='MA 50', line=dict(color='#1565C0',width=1.5)))
fig.update_layout(title=f"{view} — {tf}", height=450, xaxis_rangeslider_visible=False,
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1), margin=dict(l=0,r=0,t=40,b=0))
st.plotly_chart(fig, use_container_width=True)

ca,cb = st.columns(2)
with ca:
    st.subheader("RSI"); fr=go.Figure()
    fr.add_trace(go.Scatter(x=df.index,y=df['RSI'],mode='lines',line=dict(color='#7B1FA2',width=1.5)))
    fr.add_hline(y=70,line_dash="dash",line_color="#ef5350"); fr.add_hline(y=30,line_dash="dash",line_color="#26a69a")
    fr.update_layout(height=250,yaxis=dict(range=[0,100]),showlegend=False,margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fr,use_container_width=True)
with cb:
    st.subheader("Performance"); df['returns']=df['close'].pct_change()
    st.metric("Return",f"{((df['close'].iloc[-1]-df['close'].iloc[0])/df['close'].iloc[0]*100):+.2f}%")
    st.metric("Volatility",f"{df['returns'].std()*100:.4f}%")
    st.metric("Max DD",f"{((df['close']/df['close'].cummax())-1).min()*100:+.2f}%")

# On-Chain Data Panel
st.markdown("---")
st.subheader("🔗 On-Chain Market Data")
try:
    from onchain_data import get_onchain_summary, get_funding_rates, get_whale_transactions
    summary = get_onchain_summary()
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Market Sentiment", summary.get('sentiment_label','N/A'))
    with col2:
        funding = get_funding_rates()
        btc_funding = funding.get("BTC/USD", {}).get("funding_rate", 0)
        st.metric("BTC Funding Rate", f"{btc_funding:.4f}%")
    with col3: st.metric("Recent Whale Moves", summary.get('recent_whales', 0))
    with col4: st.metric("Largest Whale Move", "N/A" if not summary.get('recent_whales') else "Active")
except:
    st.info("On-chain data module loading.")

from mobile_css import add_mobile_css
add_mobile_css()
from aegis_chat import render_chat
render_chat()
