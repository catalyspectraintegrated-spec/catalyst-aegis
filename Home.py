from db_setup import init_database
init_database()

import streamlit as st
import pandas as pd
from auth_utils import authenticate_social

st.set_page_config(page_title="CATALYST AEGIS", page_icon="🛡️", layout="wide")

# Initialize session
if 'user' not in st.session_state:
    st.session_state.user = None

# ============================================================
# SIDEBAR — Logo + Login/Profile
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
    st.sidebar.success(f"🟢 {user.get('full_name', 'Commander')}")
    st.sidebar.caption(f"ID: {user.get('user_id', 'N/A')}")
    if not user.get('verified', False):
        st.sidebar.warning("⚠️ Email not verified")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()
else:
    st.sidebar.info("👋 Welcome, guest!")
    
    # Login form in sidebar
    with st.sidebar.expander("🔑 Sign In", expanded=False):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In", use_container_width=True):
            from auth_utils import authenticate_user
            success, msg, user_data = authenticate_user(login_email, login_password)
            if success:
                st.session_state.user = user_data
                st.rerun()
            else:
                st.error(msg)
    
    if st.sidebar.button("📝 Create Account", use_container_width=True):
        st.switch_page("pages/Sign_Up.py")

st.sidebar.markdown("---")

# ============================================================
# MAIN PAGE
# ============================================================
st.title("🛡️ CATALYST AEGIS")
st.caption("Multi-Asset Trading Automation Platform | 77.8% Avg Win Rate | +301% Total Return")

# Social login section (visible to guests)
if not st.session_state.user:
    st.markdown("---")
    st.subheader("🚀 Get Started in Seconds")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔵 Sign up with Google", use_container_width=True):
            st.info("Google OAuth integration coming soon. Please use email sign-up for now.")
    with col2:
        if st.button("🟣 Sign up with Yahoo", use_container_width=True):
            st.info("Yahoo OAuth integration coming soon. Please use email sign-up for now.")
    with col3:
        if st.button("⚪ Sign up with Apple", use_container_width=True):
            st.info("Apple OAuth integration coming soon. Please use email sign-up for now.")
    with col4:
        if st.button("📧 Sign up with Email", use_container_width=True, type="primary"):
            st.switch_page("pages/Sign_Up.py")

# Performance table (visible to everyone)
st.markdown("---")
st.subheader("📊 Proven Performance — All Assets")
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

- 🧠 **ML-Filtered Entries** — 72-89% precision, filters out losing trades before they execute
- 🛡️ **Military-Grade Protection** — Trailing stops on every trade, max drawdown limits, emergency stop
- 📊 **10 Assets, Zero Losers** — Every asset tested is profitable. Forex + Crypto.
- 📧 **Automated Reports** — Daily, weekly, monthly PDFs delivered to your email
- 🔗 **Broker Integration** — Connect Exness, IC Markets, or XM for automated execution
""")

# AEGIS chat widget

# Legal
st.markdown("---")
st.markdown("""
<style>
@keyframes pulseGold { 0%{box-shadow:0 0 6px rgba(212,160,23,0.3)} 50%{box-shadow:0 0 18px rgba(212,160,23,0.8)} 100%{box-shadow:0 0 6px rgba(212,160,23,0.3)} }
.legal-bar { background:linear-gradient(135deg,#0A1628,#1A2A4A,#0A1628); border:1.5px solid #D4A017; border-radius:12px; padding:14px 20px; animation:pulseGold 3s infinite; text-align:center; }
</style>
<div class="legal-bar">
    <span style="color:#D4A017;font-weight:800;">⚠️ RISK WARNING</span><br>
    <span style="color:#B8C7D9;font-size:11px;">Trading involves substantial risk. Past performance does not guarantee future results. 
    Catalyspectra Integrated Solutions LTD (RC: 9544839) is not liable for trading losses. Not financial advice.</span>
</div>
""", unsafe_allow_html=True)


from aegis_chat import render_chat
render_chat()

from mobile_css import add_mobile_css
add_mobile_css()

# PWA Meta Tags for Mobile
st.markdown("""
<link rel="manifest" href="/pwa_manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Catalyst AEGIS">
<meta name="theme-color" content="#0A1628">
""", unsafe_allow_html=True)
