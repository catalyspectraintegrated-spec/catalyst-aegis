import streamlit as st
st.set_page_config(page_title="Broker Connect", page_icon="🔗", layout="wide")

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

st.title("🔗 Broker Connection")
if not is_verified:
    st.warning("🔒 Sign up and verify your email to connect a broker.")

c1,c2,c3=st.columns(3)
with c1:
    st.markdown("### Exness"); st.caption("Min $10 | REST API")
    st.button("Connect Exness", disabled=not is_verified, use_container_width=True)
with c2:
    st.markdown("### IC Markets"); st.caption("Min $200 | MT5")
    st.button("Connect IC Markets", disabled=not is_verified, use_container_width=True)
with c3:
    st.markdown("### XM"); st.caption("Min $5 | MT4/MT5")
    st.button("Connect XM", disabled=not is_verified, use_container_width=True)

st.markdown("---")
st.text_input("API Key", type="password", disabled=not is_verified)
st.text_input("API Secret", type="password", disabled=not is_verified)
st.button("Test Connection", type="primary", disabled=not is_verified)



from aegis_chat import render_chat
render_chat()

from mobile_css import add_mobile_css
add_mobile_css()
