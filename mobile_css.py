import streamlit as st

def add_mobile_css():
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stApp { padding: 0.5rem; }
        .block-container { padding: 0.5rem !important; }
        iframe { width: 100% !important; height: auto !important; }
        table { font-size: 11px !important; }
        .stButton button { width: 100% !important; padding: 12px !important; font-size: 14px !important; }
        .stMarkdown h1 { font-size: 1.5rem !important; }
        .stMarkdown h2 { font-size: 1.2rem !important; }
        .stMarkdown h3 { font-size: 1rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)
