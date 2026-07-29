"""
Central configuration for the Streamlit frontend.

Keeping these in one place makes it trivial to point the app at a
different backend (local dev vs. staging vs. prod) without touching
page code — just set the API_BASE_URL environment variable.
"""

import os
import socket

def resolve_backend_url() -> str:
    """
    Dynamically determines the correct backend URL.
    If 'backend' hostname is unresolvable (e.g. running outside Docker network),
    it automatically falls back to localhost:8000.
    """
    raw_url = os.getenv("API_BASE_URL") or os.getenv("BACKEND_URL")
    
    if raw_url:
        if "backend:8000" in raw_url:
            try:
                socket.gethostbyname("backend")
                return raw_url
            except Exception:
                return raw_url.replace("backend:8000", "localhost:8000")
        if not raw_url.startswith(("http://", "https://")):
            raw_url = f"https://{raw_url}"
        return raw_url

    if os.path.exists("/.dockerenv"):
        return "http://backend:8000"

    return "http://localhost:8000"

API_BASE_URL = resolve_backend_url()

# Seconds to wait before giving up on a backend request.
API_TIMEOUT = 30

APP_TITLE = "Autodesk Support Portal"