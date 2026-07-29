import streamlit as st

from config import APP_TITLE
from utils.api_client import get_me, refresh_auth_token, APIError
from utils.auth_persistence import sync_auth_local_storage, clear_auth_local_storage

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Session state initialization -------------------------------------------
_defaults = {
    "logged_in": False,
    "username": None,
    "auth_token": None,
    "refresh_token": None,
    "role": "CUSTOMER",
    "messages": [],           # chat history for the AI Assistant page
    "conversation_id": None,  # backend conversation id, so replies stay in context
    "selected_ticket_id": None, # ticket context for conversation page
}
for _key, _value in _defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value

# --- Persistent Authentication Check across Browser Refreshes ----------------
if not st.session_state.logged_in:
    token = st.query_params.get("session_token")
    ref_token = st.query_params.get("refresh_token")
    
    if token or ref_token:
        authenticated = False
        if token:
            try:
                user_info = get_me(token=token)
                if user_info and "username" in user_info:
                    st.session_state.logged_in = True
                    st.session_state.auth_token = token
                    st.session_state.username = user_info.get("username")
                    st.session_state.role = user_info.get("role", "CUSTOMER")
                    authenticated = True
            except APIError:
                pass
                
        if not authenticated and ref_token:
            try:
                res = refresh_auth_token(ref_token)
                new_token = res.get("access_token")
                new_ref = res.get("refresh_token")
                if new_token:
                    st.session_state.logged_in = True
                    st.session_state.auth_token = new_token
                    st.session_state.refresh_token = new_ref
                    st.session_state.username = res.get("username")
                    st.session_state.role = res.get("role", "CUSTOMER")
                    st.query_params["session_token"] = new_token
                    if new_ref:
                        st.query_params["refresh_token"] = new_ref
                    authenticated = True
            except APIError:
                pass
                
        if not authenticated:
            st.query_params.clear()
            st.session_state.logged_in = False
            st.session_state.auth_token = None
            st.session_state.refresh_token = None
            st.session_state.username = None

# --- Sync Browser LocalStorage with Authentication State ---------------------
sync_auth_local_storage()

# --- Page declarations & Routing ----------------------------------------------
if not st.session_state.logged_in:
    login_page = st.Page(
        "pages/login_signup.py",
        title="Sign In / Register",
        icon="🔒",
        default=True,
    )
    pg = st.navigation([login_page], position="hidden")
else:
    dashboard_page = st.Page(
        "pages/dashboard.py",
        title="Support Dashboard",
        default=True,
    )
    conversation_page = st.Page(
        "pages/conversation.py",
        title="Starts a ticket",
        icon="💬",
    )
    pg = st.navigation([dashboard_page, conversation_page], position="sidebar")

pg.run()
