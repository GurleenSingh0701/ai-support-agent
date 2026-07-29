"""
AI Assistant conversation page.

A chat-style interface backed by the FastAPI /chat endpoint. Message
history is kept in st.session_state so it survives reruns within a
session; the conversation_id returned by the backend is passed back on
every request so the AI has context from earlier turns.
"""

import streamlit as st

from components.sidebar import render_sidebar
from components.styles import inject_base_css
from utils.api_client import APIError, send_chat_message, get_ticket_chats, get_user_tickets, get_ticket_details

inject_base_css()

if not st.session_state.get("logged_in", False):
    st.warning("Please login to access this page.")
    st.stop()

render_sidebar()

# Page-specific styling
st.markdown(
    """
    <style>
        .chat-header {
            margin-bottom: 1rem; padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        .chat-header h1 {
            font-weight: 700 !important; font-size: 1.5rem !important; margin: 0.15rem 0 0 0 !important;
        }
        div[data-testid="stChatMessage"] {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 4px !important;
        }
        div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
            background: #EEF2F8 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

selected_ticket_id = st.session_state.get("selected_ticket_id")

if selected_ticket_id is not None:
    # Fetch ticket details to show in the header
    ticket_title = "Loading..."
    try:
        t_details = get_ticket_details(selected_ticket_id)
        ticket_title = t_details.get("query") or "No Title"
    except Exception:
        ticket_title = f"Ticket TK-{selected_ticket_id}"

    st.markdown(
        f"""
        <div class="chat-header">
            <span class="eyebrow">Support Console &middot; Ticket TK-{selected_ticket_id}</span>
            <h1>AI Support Assistant</h1>
            <div style="font-size:0.92rem;color:var(--text-muted);margin-top:0.25rem;">
                Discussing Ticket: <strong>{ticket_title}</strong> (ID: TK-{selected_ticket_id})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load ticket-specific chat history if not already loaded
    if st.session_state.get("loaded_ticket_id") != selected_ticket_id:
        try:
            chats = get_ticket_chats(selected_ticket_id)
            st.session_state.messages = []
            for c in chats:
                st.session_state.messages.append({"role": "user", "content": c["message"]})
                st.session_state.messages.append({"role": "assistant", "content": c["response"]})
                st.session_state.conversation_id = c["conversation_id"]
            st.session_state.loaded_ticket_id = selected_ticket_id
        except APIError as e:
            st.error(f"Couldn't load chat history: {e}")

    col_back, col_clear = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Dashboard", use_container_width=True, key="scoped_back_btn"):
            st.session_state.selected_ticket_id = None
            st.session_state.loaded_ticket_id = None
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.switch_page("pages/dashboard.py")
    with col_clear:
        if st.button("Clear chat history", use_container_width=True, key="scoped_clear_btn"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

    # --- Render existing chat history --------------------------------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Handle new user input ----------------------------------------------------
    user_input = st.chat_input("Describe your issue or ask a question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            try:
                reply = send_chat_message(
                    message=user_input,
                    conversation_id=st.session_state.get("conversation_id"),
                    ticket_id=selected_ticket_id,
                )
                answer = reply.get("response", "Sorry, I didn't get a response from the server.")
                st.session_state.conversation_id = reply.get(
                    "conversation_id", st.session_state.get("conversation_id")
                )
                placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except APIError as e:
                placeholder.error(f"Couldn't reach the AI backend: {e}")

else:
    # Unscoped Mode -> Headline: "Starts a ticket"
    st.markdown(
        """
        <div class="chat-header">
            <span class="eyebrow">Support Console &middot; AI Assistant</span>
            <h1>Starts a ticket</h1>
            <div style="font-size:0.92rem;color:var(--text-muted);margin-top:0.25rem;">
                Describe your issue below to automatically open a new support ticket.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to Dashboard", use_container_width=True, key="unscoped_back_btn"):
        st.session_state.selected_ticket_id = None
        st.session_state.loaded_ticket_id = None
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.switch_page("pages/dashboard.py")

    # Show any messages typed before redirect (will normally be empty)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input to start a ticket
    user_input = st.chat_input("Describe your issue here to start a ticket...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Starting ticket and analyzing details...")
            try:
                # ticket_id is None, so the backend automatically creates a ticket!
                reply = send_chat_message(
                    message=user_input,
                    conversation_id=st.session_state.get("conversation_id"),
                    ticket_id=None,
                )
                answer = reply.get("response", "Sorry, I didn't get a response from the server.")
                new_ticket_id = reply.get("ticket_id")
                
                st.session_state.conversation_id = reply.get(
                    "conversation_id", st.session_state.get("conversation_id")
                )
                placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Switch to scoped ticket view
                if new_ticket_id:
                    st.session_state.selected_ticket_id = new_ticket_id
                    st.session_state.loaded_ticket_id = new_ticket_id
                    st.rerun()
            except APIError as e:
                placeholder.error(f"Couldn't reach the AI backend: {e}")

    st.markdown("<br><hr style='border: 0; border-top: 1px solid var(--border);'><br>", unsafe_allow_html=True)
    
    with st.expander("Or view/chat about an existing ticket"):
        try:
            tickets = get_user_tickets()
        except APIError as e:
            tickets = []
            st.error(f"Could not load tickets: {e}")

        if tickets:
            ticket_options = {}
            for t in tickets:
                try:
                    t_id = int(t["id"].split("-")[1])
                except Exception:
                    continue
                label = f"{t['id']} - {t['title']} ({t['status']})"
                ticket_options[label] = t_id

            selected_label = st.selectbox("Select ticket:", list(ticket_options.keys()), key="select_existing_ticket_dropdown")
            if st.button("Open Selected Ticket Conversation 💬", type="primary", use_container_width=True):
                st.session_state.selected_ticket_id = ticket_options[selected_label]
                st.session_state.messages = []
                st.session_state.loaded_ticket_id = None
                st.session_state.conversation_id = None
                st.rerun()
        else:
            st.warning("You do not have any open tickets yet.")