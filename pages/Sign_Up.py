import streamlit as st
import re
from auth_utils import register_user, verify_email, get_verification_code

st.set_page_config(page_title="Sign Up — Catalyst AEGIS", page_icon="🛡️", layout="centered")

# Initialize session
if 'signup_step' not in st.session_state:
    st.session_state.signup_step = 1
if 'signup_email' not in st.session_state:
    st.session_state.signup_email = ""

st.title("🛡️ Join Catalyst AEGIS")
st.caption("Create your account and deploy the shield.")

# ============================================================
# STEP 1: Registration Form
# ============================================================
if st.session_state.signup_step == 1:
    with st.form("signup_form"):
        st.subheader("📋 Account Information")
        full_name = st.text_input("Full Name *", placeholder="John Doe")
        email = st.text_input("Email Address *", placeholder="you@example.com")
        password = st.text_input("Password *", type="password", help="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password *", type="password")
        country = st.selectbox("Country of Residence", [
            "Nigeria", "Ghana", "Kenya", "South Africa", 
            "United Kingdom", "United States", "Other"
        ])
        
        st.markdown("---")
        st.subheader("📜 Legal Agreements")
        st.markdown("""
        **Please read and accept:**
        
        - **Terms of Service:** Catalyst AEGIS is a trading automation platform, not a financial adviser. 
        All trading decisions are your own responsibility.
        - **Risk Disclosure:** Forex and cryptocurrency trading involves substantial risk of loss. 
        You may lose some or all of your invested capital.
        - **Liability:** Catalyspectra Integrated Solutions LTD (RC: 9544839) shall not be liable 
        for any trading losses incurred.
        """)
        
        accept_terms = st.checkbox("I accept the Terms of Service *")
        accept_risk = st.checkbox("I understand and accept the Risk Disclosure *")
        accept_liability = st.checkbox("I agree Catalyspectra Integrated Solutions LTD is not liable for losses *")
        
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submitted:
            errors = []
            if not full_name: errors.append("Full name is required.")
            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email): errors.append("Valid email is required.")
            if not password or len(password) < 6: errors.append("Password must be at least 6 characters.")
            if password != confirm_password: errors.append("Passwords do not match.")
            if not accept_terms: errors.append("You must accept the Terms of Service.")
            if not accept_risk: errors.append("You must accept the Risk Disclosure.")
            if not accept_liability: errors.append("You must agree to the liability terms.")
            
            if errors:
                for e in errors: st.error(e)
            else:
                success, message, user_data = register_user(
                    full_name, email, password, country,
                    accept_terms, accept_risk, accept_liability
                )
                
                if success:
                    st.session_state.signup_step = 2
                    st.session_state.signup_email = email
                    st.session_state.pending_user = user_data
                    st.rerun()
                else:
                    st.error(message)

# ============================================================
# STEP 2: Email Verification
# ============================================================
elif st.session_state.signup_step == 2:
    email = st.session_state.signup_email
    verification_code = get_verification_code(email)
    
    st.success(f"✅ Account created! A verification code has been sent to **{email}**")
    
    st.markdown("""
    ### 📧 Verify Your Email
    
    Enter the 6-digit code sent to your email address.
    """)
    
    # For demo purposes, show the code
    with st.expander("📩 Demo: Click to see verification code (for testing)"):
        st.info(f"Your verification code is: **{verification_code}**")
        st.caption("In production, this code is sent via email and never displayed here.")
    
    code = st.text_input("Verification Code", placeholder="000000", max_chars=6)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Verify Email", type="primary", use_container_width=True):
            success, message = verify_email(email, code)
            if success:
                st.session_state.signup_step = 3
                st.session_state.user = st.session_state.pending_user
                st.session_state.user['verified'] = True
                st.rerun()
            else:
                st.error(message)
    with col2:
        if st.button("↩️ Back to Sign Up", use_container_width=True):
            st.session_state.signup_step = 1
            st.rerun()

# ============================================================
# STEP 3: Complete
# ============================================================
elif st.session_state.signup_step == 3:
    st.success("🎉 Email verified successfully!")
    st.balloons()
    st.markdown(f"""
    ### Welcome to Catalyst AEGIS, {st.session_state.user.get('full_name', 'Commander')}!
    
    Your unique ID: **{st.session_state.user.get('user_id', 'N/A')}**
    
    You can now:
    - 📊 Monitor live trades
    - ⚙️ Configure your strategy
    - 🔗 Connect your broker
    - 📈 Access performance reports
    
    **What would you like to do?**
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    with col2:
        if st.button("🏠 Go to Home", use_container_width=True):
            st.switch_page("Home.py")


from aegis_chat import render_chat
render_chat()

from mobile_css import add_mobile_css
add_mobile_css()
