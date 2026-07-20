import streamlit as st
import pandas as pd
from auth_utils import authenticate_social
from db_setup import init_database

import random

st.set_page_config(page_title="CATALYST AEGIS", page_icon="🛡️", layout="wide")

# Initialize database and fetch data on first run
init_database()

# Initialize session
if 'user' not in st.session_state:
    st.session_state.user = None

# ============================================================
# SIDEBAR — Logo + Sign In/Profile
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
    st.sidebar.caption(f"ID: {user.get('user_id', 'N/A')}")
    if not user.get('verified', False):
        st.sidebar.warning("⚠️ Email not verified — verify in Account page")
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user = None
        st.rerun()
else:
    st.sidebar.warning("👋 Welcome, guest!")
    
    # Sign In form
    with st.sidebar.expander("🔑 Sign In to Your Account", expanded=True):
        login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter password")
        
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
    st.sidebar.markdown("**Or use social login:**")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.button("Google", disabled=True, use_container_width=True)
    with col2:
        st.button("Apple", disabled=True, use_container_width=True)
    with col3:
        st.button("Yahoo", disabled=True, use_container_width=True)

st.sidebar.markdown("---")

# ============================================================
# MAIN PAGE
# ============================================================
st.title("🛡️ CATALYST AEGIS")
st.caption("Multi-Asset Trading Automation Platform | 77.8% Avg Win Rate | +301% Total Return")

# If not signed in, show prominent sign-up prompt
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
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Create Free Account", use_container_width=True, type="primary"):
                st.switch_page("pages/Sign_Up.py")
        with col_b:
            st.info("Already have an account? Sign in from the sidebar →")
else:
    st.success(f"✅ Welcome back, {st.session_state.user.get('full_name', 'Commander')}! Your shield is active.")

# Performance table (visible to everyone)
st.markdown("---")
st.subheader("📊 Proven Performance — All 10 Assets")
perf = pd.DataFrame({
    "Asset": ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","BTC/USD","ETH/USD","BNB/USD","SOL/USD"],
    "Win Rate": ["100.0%","68.6%","70.7%","71.9%","68.1%","70.0%","94.4%","82.8%","72.4%","78.9%"],
    "Return": ["+0.72%","+0.43%","+87.14%","+0.20%","+80.00%","+130.76%","+1.71%","+0.13%","+0.01%","+0.10%"]
})
st.dataframe(perf, use_container_width=True, hide_index=True)

c1, c2, c3 = st.columns(3)
c1.metric("Avg Win Rate", "77.8%")
c2.metric("Combined Return", "+301.2%")
c3.metric("P&L on $10k", "+$30,121")

st.markdown("---")
st.markdown("""
### Why Catalyst AEGIS?

- 🧠 **ML-Filtered Entries** — 72-89% precision, filters out losing trades
- 🛡️ **Trailing Stop Protection** — Every trade protected, every time
- 📊 **10 Assets, Zero Losers** — Every asset profitable in backtesting
- 🔗 **Broker Integration** — Connect Exness, IC Markets, or XM
- 📧 **Automated Reports** — Daily, weekly, monthly PDFs
""")

# AEGIS chat
from aegis_chat import render_chat
render_chat()

# Legal
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
