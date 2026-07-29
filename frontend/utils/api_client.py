"""
Thin HTTP client for the FastAPI backend.

Every function here raises APIError with a short, user-friendly message
on failure, so pages can simply do:

    try:
        data = get_tickets()
    except APIError as e:
        st.error(str(e))

This keeps requests/network handling out of the page files entirely.
"""

from __future__ import annotations

from typing import Any
import requests
import streamlit as st

from config import API_BASE_URL, API_TIMEOUT


class APIError(Exception):
    """Raised when a backend call fails. Message is safe to show the user."""


def _auth_headers() -> dict:
    """Attach the bearer token from session state, if the user is logged in."""
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("auth_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request(method: str, path: str, **kwargs) -> Any:
    """Shared request/error-handling logic for every endpoint below."""
    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.ConnectionError as exc:
        raise APIError(
            f"Could not connect to the backend at {API_BASE_URL}. "
            "Make sure the FastAPI service is running."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise APIError("The server took too long to respond. Please try again.") from exc
    except requests.exceptions.HTTPError as exc:
        # If 401 Unauthorized occurs on an authenticated request, attempt silent refresh token flow
        if exc.response is not None and exc.response.status_code == 401 and path not in ["/auth/login", "/auth/refresh"]:
            ref_token = st.session_state.get("refresh_token") or st.query_params.get("refresh_token")
            if ref_token:
                try:
                    ref_res = requests.post(f"{API_BASE_URL}/auth/refresh", json={"refresh_token": ref_token}, timeout=API_TIMEOUT)
                    if ref_res.status_code == 200:
                        ref_data = ref_res.json()
                        new_access = ref_data.get("access_token")
                        new_ref = ref_data.get("refresh_token")
                        st.session_state.auth_token = new_access
                        st.query_params["session_token"] = new_access
                        if new_ref:
                            st.session_state.refresh_token = new_ref
                            st.query_params["refresh_token"] = new_ref
                        # Retry original request with new token
                        headers = kwargs.get("headers", {})
                        headers["Authorization"] = f"Bearer {new_access}"
                        kwargs["headers"] = headers
                        retry_resp = requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
                        retry_resp.raise_for_status()
                        return retry_resp.json() if retry_resp.content else {}
                except Exception:
                    pass

        detail = "Request failed. Please try again."
        try:
            if exc.response is not None:
                detail = exc.response.json().get("detail", detail)
        except (ValueError, AttributeError):
            pass
        raise APIError(detail) from exc


# --- Auth -----------------------------------------------------------------

def login(username: str, password: str) -> dict:
    """POST /auth/login -> {"access_token": ..., "username": ...}"""
    return _request(
        "POST",
        "/auth/login",
        json={"username": username, "password": password},
    )


def signup(username: str, password: str) -> dict:
    """POST /auth/signup -> {"username": ...}"""
    return _request(
        "POST",
        "/auth/signup",
        json={"username": username, "password": password},
    )


def get_me(token: str | None = None) -> dict:
    """GET /auth/me -> {"id": ..., "username": ..., "role": ...}"""
    headers = {"Content-Type": "application/json"}
    t = token or st.session_state.get("auth_token")
    if t:
        headers["Authorization"] = f"Bearer {t}"
    return _request("GET", "/auth/me", headers=headers)


def refresh_auth_token(refresh_token: str) -> dict:
    """POST /auth/refresh -> {"access_token": ..., "refresh_token": ..., "username": ..., "role": ...}"""
    return _request(
        "POST",
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )


# --- AI chat ----------------------------------------------------------------

def send_chat_message(
    message: str,
    conversation_id: str | None = None,
    ticket_id: int | None = None
) -> dict:
    """POST /chat -> {"response": ..., "conversation_id": ..., "ticket_id": ...}"""
    return _request(
        "POST",
        "/chat",
        json={
            "message": message,
            "conversation_id": conversation_id,
            "ticket_id": ticket_id
        },
        headers=_auth_headers(),
    )


def get_user_chats() -> list:
    """GET /chat/my-chats -> list of chat message dicts for the current user"""
    raw_chats = _request("GET", "/chat/my-chats", headers=_auth_headers())
    if not isinstance(raw_chats, list):
        return []
    return raw_chats


def get_ticket_chats(ticket_id: int) -> list:
    """GET /chat/ticket/{ticket_id} -> list of chat entries for this ticket"""
    raw_chats = _request("GET", f"/chat/ticket/{ticket_id}", headers=_auth_headers())
    if not isinstance(raw_chats, list):
        return []
    return raw_chats


# --- Tickets ----------------------------------------------------------------

# Maps the backend's internal ticket status codes to the friendly labels
# used throughout the dashboard UI. Keep in sync with dashboard.py's
# STATUS_COLORS mapping.
STATUS_DISPLAY_MAP = {
    "OPEN": "Open",
    "IN_PROGRESS": "Under Investigation",
    "ESCALATED": "Pending Customer Response",
    "RESOLVED": "Resolved",
    "CLOSED": "Closed",
}


def get_tickets(user_only: bool = False) -> list:
    """GET /tickets/all-tickets or /tickets/my-tickets -> list of ticket dicts"""
    endpoint = "/tickets/my-tickets" if user_only else "/tickets/all-tickets"
    raw_tickets = _request("GET", endpoint, headers=_auth_headers())
    if not isinstance(raw_tickets, list):
        return []
    
    formatted_tickets = []
    for t in raw_tickets:
        created_at_str = t.get("created_at")
        date_str = "Unknown"
        if created_at_str:
            try:
                date_str = str(created_at_str).split("T")[0]
            except Exception:
                date_str = str(created_at_str)

        raw_status = (t.get("status") or "OPEN").upper()

        formatted_tickets.append({
            "id": f"TK-{t.get('id')}",
            "title": t.get("query") or "No Title",
            "status": STATUS_DISPLAY_MAP.get(raw_status, raw_status.title()),
            "priority": t.get("priority") or "MEDIUM",
            "category": t.get("category") or "GENERAL",
            "date": date_str
        })
    return formatted_tickets


def get_user_tickets() -> list:
    """GET /tickets/my-tickets -> list of ticket dicts for the current user"""
    return get_tickets(user_only=True)


def create_ticket(query: str, response: str) -> dict:
    """POST /create-ticket -> created ticket dict"""
    return _request(
        "POST",
        "/tickets/create-ticket",
        json={"query": query, "response": response},
        headers=_auth_headers(),
    )


def get_ticket_details(ticket_id: int) -> dict:
    """GET /tickets/{ticket_id} -> details of a single ticket"""
    return _request("GET", f"/tickets/{ticket_id}", headers=_auth_headers())