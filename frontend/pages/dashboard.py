"""
Support Dashboard - ticket overview + entry point to the AI Assistant.
"""

import streamlit as st

from components.sidebar import render_sidebar
from components.styles import inject_base_css
from utils.api_client import APIError, create_ticket, get_user_tickets

inject_base_css()

if not st.session_state.get("logged_in", False):
    st.warning("Please login to access this page.")
    st.stop()

render_sidebar()

# Reset ticket context when viewing dashboard
st.session_state.selected_ticket_id = None
st.session_state.loaded_ticket_id = None

# Page-specific styling
st.markdown(
    """
    <style>
        .dashboard-header {
            margin-bottom: 1.5rem; padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        .dashboard-header h1 {
            font-weight: 700 !important; font-size: 1.65rem !important; margin: 0.15rem 0 0 0 !important;
        }
        .ticket-row {
            display: flex; border: 1px solid var(--border); border-left: 3px solid var(--status-color);
            border-radius: 4px; background: var(--surface); padding: 0.85rem 1rem;
            margin-bottom: 0.6rem; align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="dashboard-header">
        <span class="eyebrow">Support Console &middot; {st.session_state.username}</span>
        <h1>Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.page_link("pages/conversation.py", label="Starts a ticket", icon="💬")

st.markdown("<div class='eyebrow' style='margin:1.5rem 0 0.6rem;'>Overview</div>", unsafe_allow_html=True)

# --- Pull ticket data from the FastAPI backend, with a graceful fallback ------
try:
    tickets = get_user_tickets()
except APIError as e:
    st.warning(f"Couldn't load live ticket data ({e}). Showing sample data instead.")
    tickets = [
        {"id": "TK-883", "title": "Fusion 360 license validation failure",
         "status": "Pending Customer Response", "date": "2026-07-27"},
        {"id": "TK-881", "title": "AutoCAD installation error on Windows 11 ARM",
         "status": "Under Investigation", "date": "2026-07-26"},
        {"id": "TK-879", "title": "Revit cloud rendering pipeline hanging",
         "status": "Open", "date": "2026-07-25"},
    ]

total = len(tickets)
pending = sum(1 for t in tickets if "Pending" in t.get("status", ""))
resolved = sum(1 for t in tickets if "Resolved" in t.get("status", ""))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tickets", total)
col2.metric("Pending Response", pending)
col3.metric("Resolved", resolved)
col4.metric("Avg Response Time", "42 min")

st.markdown("<div class='eyebrow' style='margin:1.75rem 0 0.6rem;'>Recent Tickets</div>", unsafe_allow_html=True)

STATUS_COLORS = {
    "Open": "#2454A6",
    "Under Investigation": "#2454A6",
    "Pending Customer Response": "#92620A",
    "Resolved": "#166C3B",
}

for t in tickets:
    color = STATUS_COLORS.get(t["status"], "#5B6472")
    
    # Display each ticket with an aligned Chat button
    col_t_info, col_t_btn = st.columns([5, 1])
    with col_t_info:
        st.markdown(
            f"""
            <div class="ticket-row" style="--status-color:{color};">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;
                            color:var(--text-muted);width:75px;flex-shrink:0;">{t['id']}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:0.92rem;color:var(--text);">{t['title']}</div>
                    <div style="font-size:0.76rem;color:var(--text-muted);margin-top:0.15rem;">
                        Opened {t['date']}
                    </div>
                </div>
                <div style="font-size:0.78rem;font-weight:600;color:{color};
                            text-align:right;flex-shrink:0;margin-left:1rem;">
                    {t['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t_btn:
        try:
            ticket_id = int(t['id'].split("-")[1])
        except Exception:
            ticket_id = None
            
        if ticket_id is not None:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True) # small spacing
            if st.button("Chat 💬", key=f"chat_btn_{ticket_id}", use_container_width=True):
                st.session_state.selected_ticket_id = ticket_id
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.switch_page("pages/conversation.py")