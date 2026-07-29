"""
Sign In / Sign Up page for Autodesk Support Portal.

Centered enterprise card layout with custom tabs, field focus states,
inside input icons, and FastAPI backend authentication integration.
"""

import streamlit as st

from components.styles import inject_base_css
from utils.api_client import APIError, login, signup

inject_base_css()

# Custom CSS for broader centered card layout and professional styling
st.markdown(
    """
    <style>
        /* Page container reset & subtle gradient canvas */
        .stApp {
            background: linear-gradient(135deg, #F4F6F9 0%, #E5E9F0 100%) !important;
        }

        /* Container width (580px) */
        div.block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 580px !important;
            margin: 0 auto !important;
        }

        /* Header styling */
        .auth-card-header {
            text-align: center;
            margin-bottom: 32px;
        }
        .auth-logo-badge {
            width: 58px;
            height: 58px;
            margin: 0 auto 16px auto;
            background: linear-gradient(135deg, #122A46 0%, #2454A6 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 16px rgba(36, 84, 166, 0.22);
        }
        .auth-card-header h1 {
            font-size: 30px !important;
            font-weight: 700 !important;
            color: #122A46 !important;
            margin: 0 0 8px 0 !important;
            letter-spacing: -0.02em !important;
        }
        .auth-card-header p {
            font-size: 15.5px !important;
            color: #5B6472 !important;
            margin: 0 !important;
            line-height: 1.5 !important;
        }

        /* Segmented tab control */
        div[data-testid="stTabs"] {
            border-bottom: none !important;
            background: #EAEFF5 !important;
            padding: 4px !important;
            border-radius: 8px !important;
            margin-bottom: 28px !important;
        }
        button[data-baseweb="tab"] {
            border-radius: 6px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 11px 0 !important;
            color: #5B6472 !important;
            transition: all 0.15s ease !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: #FFFFFF !important;
            color: #122A46 !important;
            box-shadow: 0 2px 4px rgba(18, 42, 70, 0.08) !important;
        }
        div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Tab content padding */
        div[data-testid="stTabContent"] {
            padding-top: 8px !important;
        }

        /* Input field container spacing */
        div[data-testid="stTextInput"] {
            margin-bottom: 18px !important;
        }
        
        div[data-baseweb="base-input"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"] {
            background-color: #FFFFFF !important;
            border: 1px solid #DDE1E7 !important;
            border-radius: 6px !important;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: #2454A6 !important;
            box-shadow: 0 0 0 3px rgba(36, 84, 166, 0.15) !important;
        }

        .stTextInput input {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 12px 14px 12px 42px !important;
            font-size: 15.5px !important;
            color: #14181F !important;
        }
        .stTextInput input:focus {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Lock icon inside password inputs */
        .stTextInput input[type="password"] {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%235B6472' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'%3E%3C/rect%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'%3E%3C/path%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: 14px center !important;
        }

        /* User icon inside username inputs */
        .stTextInput input:not([type="password"]) {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%235B6472' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'%3E%3C/path%3E%3Ccircle cx='12' cy='7' r='4'%3E%3C/circle%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: 14px center !important;
        }

        label[data-testid="stWidgetLabel"] p {
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #14181F !important;
            margin-bottom: 6px !important;
        }

        /* Primary action button spacing & height */
        div.stButton {
            margin-top: 26px !important;
            margin-bottom: 8px !important;
            width: 100% !important;
        }

        div.stButton > button {
            width: 100% !important;
            height: 48px !important;
            border-radius: 6px !important;
            padding: 0 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            transition: all 0.15s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #122A46 0%, #2454A6 100%) !important;
            border: 1px solid #122A46 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 10px rgba(18, 42, 70, 0.18) !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0B1B2E 0%, #1D4482 100%) !important;
            box-shadow: 0 6px 14px rgba(18, 42, 70, 0.28) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def handle_login(username: str, password: str) -> None:
    """Call the FastAPI /auth/login endpoint and securely update session state."""
    if not username or not password:
        st.error("Please fill in all fields.")
        return
    try:
        with st.spinner("Signing in..."):
            result = login(username, password)
        st.session_state.logged_in = True
        st.session_state.username = result.get("username", username)
        st.session_state.auth_token = result.get("access_token")
        st.session_state.refresh_token = result.get("refresh_token")
        st.session_state.role = result.get("role", "CUSTOMER")
                 
        # REMOVED: Insecure st.query_params token persistence
        
        st.toast("Welcome back!", icon="✅")
        st.rerun()
    except APIError as e:
        st.error(str(e))

# [Keep the rest of your handle_signup, Header Section, and Segmented Auth Tabs exactly the same...]
def handle_signup(username: str, password: str, confirm_password: str) -> None:
    """Call the FastAPI /auth/signup endpoint."""
    if not username or not password or not confirm_password:
        st.error("Please fill in all fields.")
        return
    if password != confirm_password:
        st.error("Passwords do not match.")
        return
    if len(password) < 6:
        st.error("Password must be at least 6 characters long.")
        return
    try:
        with st.spinner("Creating your account..."):
            signup(username, password)
        st.success("Account created successfully! You can now sign in.")
        st.toast("Account ready", icon="✅")
    except APIError as e:
        st.error(str(e))


# --- Header Section -----------------------------------------------------------
st.markdown(
    """
    <div class="auth-card-header">
        <div class="auth-logo-badge">
            <svg viewBox="0 0 24 24" width="30" height="30" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
            </svg>
        </div>
        <h1>Autodesk Support Portal</h1>
        <p>Sign in to manage tickets or access the AI Assistant</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Segmented Auth Tabs ------------------------------------------------------
tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

with tab_login:
    with st.form(key="login_form", clear_on_submit=False):
        login_username = st.text_input(
            "Username", placeholder="Enter your username", key="login_user"
        )
        login_password = st.text_input(
            "Password", placeholder="••••••••", type="password", key="login_pass"
        )
        submit_login = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submit_login:
            handle_login(login_username, login_password)

with tab_signup:
    with st.form(key="signup_form", clear_on_submit=False):
        signup_username = st.text_input(
            "Choose Username", placeholder="Enter username", key="signup_user"
        )
        signup_password = st.text_input(
            "Password", placeholder="Min 6 characters", type="password", key="signup_pass"
        )
        signup_confirm = st.text_input(
            "Confirm Password", placeholder="••••••••", type="password", key="signup_confirm_pass"
        )
        submit_signup = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        if submit_signup:
            handle_signup(signup_username, signup_password, signup_confirm)