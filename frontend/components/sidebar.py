"""
Custom sidebar chrome shown on every authenticated page.

st.navigation() (declared in app.py) already renders the page links at
the top of the sidebar automatically. This module adds a dense user
identity block and the sign-out control underneath those links.
"""

import streamlit as st


from utils.auth_persistence import clear_auth_local_storage


def render_sidebar() -> None:
    """Render the user identity block and sign-out button in the sidebar."""
    with st.sidebar:
        st.markdown(
            "<div style='border-top:1px solid rgba(255,255,255,0.12);margin:0.75rem 0 1rem 0;'></div>",
            unsafe_allow_html=True,
        )

        username = st.session_state.get("username") or "User"
        initials = username[:2].upper()

        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.7rem;
                        padding:0.4rem 0.15rem;margin-bottom:0.75rem;">
                <div style="width:34px;height:34px;border-radius:4px;
                            background:rgba(255,255,255,0.08);
                            border:1px solid rgba(255,255,255,0.18);
                            display:flex;align-items:center;justify-content:center;
                            font-family:'IBM Plex Mono',monospace;
                            font-weight:600;font-size:0.8rem;color:#E7EBF2;flex-shrink:0;">
                    {initials}
                </div>
                <div style="min-width:0;">
                    <div style="font-weight:600;font-size:0.88rem;color:#F4F5F7;
                                overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        {username}
                    </div>
                    <div style="font-size:0.7rem;letter-spacing:0.04em;
                                text-transform:uppercase;color:#8FA0B8;">
                        Support Portal
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Sign out", use_container_width=True, key="sidebar_logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.auth_token = None
            st.session_state.refresh_token = None
            st.session_state.role = "CUSTOMER"
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.query_params.clear()
            clear_auth_local_storage()
            st.toast("Signed out", icon="✓")
            st.rerun()

        st.markdown(
            "<div style='font-size:0.68rem;color:#5E7089;margin-top:1rem;"
            "letter-spacing:0.03em;'>Autodesk Support Portal &middot; v1.0</div>",
            unsafe_allow_html=True,
        )