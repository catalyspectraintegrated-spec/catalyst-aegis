import streamlit as st
import pandas as pd
from db_setup import init_database
import random
import os

# Initialize database on startup
init_database()

st.set_page_config(page_title="CATALYST AEGIS", page_icon="🛡️", layout="wide")

# Initialize session
if 'user' not in st.session_state:
    st.session_state.user = None

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("""
<div style="background:linear-gradient(135deg,#0A1628,#1A2A4A);border:2px solid #D4A017;border-radius:12px;padding:18px 12px;text-align:center;margin-bottom:15px;">
    <span style="font-size:38px;">🛡️</span><br>
    <span style="font-size:22px;font-weight:900;color:#D4A017;letter-spacing:2px;">CATALYST</span><br>
    <span style="font-size:22px;font-weight:900;color:#FFFFFF;letter-spacing:2px;">AEGIS</span>
</div>
""", unsafe_allow_html=True)

if st.session_state.user:
    user = st.session_state.user
    st.sidebar.success(f"🟢 Signed in as {user.get('full_name', 'Commander')}")
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user = None
        st.rerun()
else:
    st.sidebar.warning("👋 Welcome, guest!")
    with st.sidebar.expander("🔑 Sign In", expanded=True):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In", use_container_width=True, type="primary"):
                from auth_utils import authenticate_user
                success, msg, user_data = authenticate_user(login_email, login_password)
                if success:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error(msg)
        with col2:
            if st.button("Create Account", use_container_width=True):
                st.switch_page("pages/Sign_Up.py")

st.sidebar.markdown("---")

# ============================================================
# MAIN PAGE
# ============================================================
st.title("🛡️ CATALYST AEGIS")
st.caption("Multi-Asset Trading Automation Platform | 77.8% Avg Win Rate | +301% Total Return")

if not st.session_state.user:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0A1628,#1A2A4A);border:2px solid #D4A017;border-radius:16px;padding:30px;text-align:center;margin:20px 0;">
            <h2 style="color:#D4A017;">🔐 Sign In to Start Trading</h2>
            <p style="color:#D0D8E0;">Access live trading, configure strategies, connect your broker, and track your performance.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Create Free Account", use_container_width=True, type="primary"):
            st.switch_page("pages/Sign_Up.py")

st.markdown("---")
st.subheader("📊 Proven Performance — All 10 Assets")
perf = pd.DataFrame({
    "Asset": ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","BTC/USD","ETH/USD","BNB/USD","SOL/USD"],
    "Win Rate": ["100.0%","68.6%","70.7%","71.9%","68.1%","70.0%","94.4%","82.8%","72.4%","78.9%"],
    "Return": ["+0.72%","+0.43%","+87.14%","+0.20%","+80.00%","+130.76%","+1.71%","+0.13%","+0.01%","+0.10%"]
})
st.dataframe(perf, use_container_width=True, hide_index=True)
c1,c2,c3=st.columns(3)
c1.metric("Avg Win Rate","77.8%");c2.metric("Combined Return","+301.2%");c3.metric("P&L on $10k","+$30,121")

st.markdown("---")
st.markdown("""
### Why Catalyst AEGIS?
- 🧠 ML-Filtered Entries — 72-89% precision
- 🛡️ Trailing Stop Protection on every trade
- 📊 10 Assets, Zero Losers in backtesting
- 🔗 Connect Exness, IC Markets, or XM
- 📧 Automated daily/weekly/monthly reports
""")

from aegis_chat import render_chat
render_chat()

st.markdown("---")
st.markdown("""
<style>
@keyframes pulseGold { 0%{box-shadow:0 0 6px rgba(212,160,23,0.3)} 50%{box-shadow:0 0 18px rgba(212,160,23,0.8)} 100%{box-shadow:0 0 6px rgba(212,160,23,0.3)} }
.legal-bar { background:linear-gradient(135deg,#0A1628,#1A2A4A,#0A1628); border:1.5px solid #D4A017; border-radius:12px; padding:14px 20px; animation:pulseGold 3s infinite; text-align:center; }
</style>
<div class="legal-bar">
    <span style="color:#D4A017;font-weight:800;">⚠️ RISK WARNING</span><br>
    <span style="color:#B8C7D9;font-size:11px;">Trading involves substantial risk. Past performance does not guarantee future results. Catalyspectra Integrated Solutions LTD (RC: 9544839) is not liable for trading losses. Not financial advice.</span>
</div>
""", unsafe_allow_html=True)
