import streamlit as st
st.set_page_config(page_title="Strategy Config", page_icon="⚙️", layout="wide")

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

st.title("⚙️ Strategy Configuration")
if not is_verified:
    st.warning("🔒 Sign up and verify your email to save strategy settings.")

tab1,tab2,tab3=st.tabs(["Entry Rules","Exit Rules","ML Filter"])
with tab1:
    st.checkbox("RSI Oversold", True, disabled=not is_verified)
    st.checkbox("Large Bullish Candle", True, disabled=not is_verified)
    st.slider("Forex Hours (UTC)",0,23,(5,13), disabled=not is_verified)
    st.button("Save Entry Rules",type="primary", disabled=not is_verified)
with tab2:
    st.slider("Forex Stop (pips)",10,50,20, disabled=not is_verified)
    st.selectbox("Forex Size ($10k)",[2000,5000,10000],index=1, disabled=not is_verified)
    st.slider("Max Daily Loss %",1,20,5, disabled=not is_verified)
    st.button("Save Exit Rules",type="primary", disabled=not is_verified)
with tab3:
    st.checkbox("Enable ML Filter",True, disabled=not is_verified)
    st.slider("Threshold",0.50,0.95,0.55, disabled=not is_verified)
    st.metric("EUR/USD Precision","72.3%"); st.metric("BTC/USD Precision","88.6%")
    st.button("Save ML Settings",type="primary", disabled=not is_verified)



from aegis_chat import render_chat
render_chat()

from mobile_css import add_mobile_css
add_mobile_css()
