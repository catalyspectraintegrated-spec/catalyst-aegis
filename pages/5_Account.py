import streamlit as st
st.set_page_config(page_title="Account", page_icon="👤", layout="wide")

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

st.title("👤 Account Settings")
if not is_verified:
    st.warning("🔒 Sign up and verify your email to manage account settings.")

tab1,tab2,tab3,tab4=st.tabs(["Profile","Subscription","KYC","Security"])
with tab1:
    c1,c2=st.columns(2)
    with c1: st.text_input("Full Name", value=user.get('full_name','') if user else '', disabled=not is_verified)
    with c2: st.text_input("Email", value=user.get('email','') if user else '', disabled=True)
    if user: st.info(f"🆔 Your ID: **{user.get('user_id','N/A')}**")
    st.button("Save Profile",type="primary", disabled=not is_verified)
with tab2:
    plan=st.radio("Plan",["Paper Trading (Free)","Performance Fee (20%)","Hybrid ($25/mo + 10%)"], disabled=not is_verified)
    if "Paper" in plan:
        st.button("Activate Paper Trading",type="primary", disabled=not is_verified, use_container_width=True)
    elif "Performance" in plan:
        st.text_input("Card Number", disabled=not is_verified)
        st.checkbox("I agree to Terms", disabled=not is_verified)
        st.button("Activate Performance Plan",type="primary", disabled=not is_verified, use_container_width=True)
    else:
        st.text_input("Card Number", disabled=not is_verified)
        st.checkbox("I agree to Terms", disabled=not is_verified)
        st.button("Activate Hybrid Plan",type="primary", disabled=not is_verified, use_container_width=True)
with tab3:
    st.subheader("Tier 1: Basic"); st.info("Email only. Trade up to $500.")
    st.subheader("Tier 2: Standard"); st.warning("ID required. Trade up to $5,000.")
    st.subheader("Tier 3: Full"); st.error("Facial + ID + Address. Unlimited.")
    st.file_uploader("Upload ID",type=["jpg","jpeg","png","pdf"], disabled=not is_verified)
    st.button("Submit KYC",type="primary", disabled=not is_verified)
with tab4:
    st.checkbox("Enable 2FA",True, disabled=not is_verified)
    st.button("Save Security Settings",type="primary", disabled=not is_verified)



from aegis_chat import render_chat
render_chat()

from mobile_css import add_mobile_css
add_mobile_css()
