"""
CATALYST AEGIS — Social Authentication
Google, Apple, and Yahoo OAuth integration.
"""

import os
import json
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from datetime import datetime

# OAuth Config — set these in environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID", "")
YAHOO_CLIENT_ID = os.environ.get("YAHOO_CLIENT_ID", "")
YAHOO_CLIENT_SECRET = os.environ.get("YAHOO_CLIENT_SECRET", "")

# Redirect URI (update for production domain)
REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8501")

def get_google_login_url():
    """Generate Google OAuth login URL."""
    if not GOOGLE_CLIENT_ID:
        return None
    
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="openid email profile"
    )
    url, state = oauth.create_authorization_url(
        "https://accounts.google.com/o/oauth2/v2/auth"
    )
    st.session_state['oauth_state'] = state
    return url

def handle_google_callback(auth_code):
    """Handle Google OAuth callback."""
    if not GOOGLE_CLIENT_ID:
        return None
    
    try:
        oauth = OAuth2Session(
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI
        )
        token = oauth.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=auth_code
        )
        user_info = oauth.get("https://www.googleapis.com/oauth2/v3/userinfo").json()
        
        return {
            "provider": "google",
            "email": user_info.get("email"),
            "full_name": user_info.get("name"),
            "avatar": user_info.get("picture"),
            "verified": user_info.get("email_verified", False)
        }
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return None

def render_social_buttons():
    """Render social login buttons."""
    st.markdown("### 🚀 Quick Sign Up")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        google_url = get_google_login_url()
        if google_url:
            st.markdown(f"""
            <a href="{google_url}" target="_self" style="text-decoration:none;">
                <button style="width:100%;padding:12px;background:#4285F4;color:white;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">
                    🔵 Google
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.button("🔵 Google", disabled=True, use_container_width=True,
                      help="Google OAuth not configured yet")
    
    with col2:
        if APPLE_CLIENT_ID:
            st.button("⚪ Apple", use_container_width=True,
                     help="Apple sign-in coming soon")
        else:
            st.button("⚪ Apple", disabled=True, use_container_width=True,
                     help="Apple OAuth not configured yet")
    
    with col3:
        if YAHOO_CLIENT_ID:
            st.button("🟣 Yahoo", use_container_width=True,
                     help="Yahoo sign-in coming soon")
        else:
            st.button("🟣 Yahoo", disabled=True, use_container_width=True,
                     help="Yahoo OAuth not configured yet")
    
    st.markdown("---")
    st.markdown("#### Or use email")
