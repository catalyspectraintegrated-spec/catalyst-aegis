import streamlit as st
st.set_page_config(page_title="Support", page_icon="🆘", layout="wide")

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

st.title("🆘 Help & Support")
tab1,tab2,tab3=st.tabs(["FAQ","Contact","Bug Report"])
with tab1:
    with st.expander("How does Catalyst AEGIS work?"): st.write("Multi-timeframe momentum + ML filtering across 10 assets.")
    with st.expander("Minimum to start?"): st.write("$10 on Exness. Paper trading is free.")
    with st.expander("Is my money safe?"): st.write("We never hold funds. Money stays in your broker.")
with tab2:
    st.markdown("**Catalyspectra Integrated Solutions LTD** (RC: 9544839) | Port Harcourt, Nigeria")
    st.text_input("Your Email", disabled=not is_verified)
    st.text_area("Message", disabled=not is_verified)
    st.button("Send",type="primary", disabled=not is_verified)
with tab3:
    st.selectbox("Type",["Bug","Feature","Performance","Other"], disabled=not is_verified)
    st.text_area("Description", disabled=not is_verified)
    st.button("Submit",type="primary", disabled=not is_verified)



from aegis_chat import render_chat
render_chat()

from mobile_css import add_mobile_css
add_mobile_css()
