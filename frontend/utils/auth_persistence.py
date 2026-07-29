# """
# Authentication Persistence Helper for Streamlit using URL Query Parameters.
# """

# import streamlit as st

# def sync_auth_local_storage():
#     """
#     Ensures URL query parameters match the active session tokens.
#     """
#     if st.session_state.get("logged_in") and st.session_state.get("auth_token"):
#         token = st.session_state.get("auth_token")
#         ref_token = st.session_state.get("refresh_token")
        
#         if token and st.query_params.get("session_token") != token:
#             st.query_params["session_token"] = token
#         if ref_token and st.query_params.get("refresh_token") != ref_token:
#             st.query_params["refresh_token"] = ref_token

# def clear_auth_local_storage():
#     """
#     Clears session query parameters on explicit sign out.
#     """
#     st.query_params.clear()





import streamlit as st

def sync_auth_local_storage():
    """
    Deprecated URL-based auth synchronization to address severe security vulnerabilities. 
    Authentication state is now exclusively handled by secure Streamlit session_state
    to prevent JWT leakage in browser histories, HTTP Referers, and proxy logs.
    """
    pass 

def clear_auth_local_storage():
    """
    Ensures URL query parameters are thoroughly wiped clean upon logout, 
    eradicating any residual insecure tokens left over from legacy workflows.
    """
    st.query_params.clear()
