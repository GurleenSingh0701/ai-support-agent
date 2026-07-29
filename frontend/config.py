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
    Handles Render internal hostnames, missing .onrender.com suffixes,
    Docker container aliases, and localhost fallbacks seamlessly.
    """
    raw_url = os.getenv("API_BASE_URL") or os.getenv("BACKEND_URL")
    
    if raw_url:
        if "backend:8000" in raw_url:
            try:
                socket.gethostbyname("backend")
                return raw_url
            except Exception:
                return raw_url.replace("backend:8000", "localhost:8000")
        
        # Ensure scheme
        if not raw_url.startswith(("http://", "https://")):
            raw_url = f"https://{raw_url}"
            
        # Fix Render internal host property (e.g. https://autodesk-backend-ibzm -> https://autodesk-backend-ibzm.onrender.com)
        clean_host = raw_url.replace("https://", "").replace("http://", "").split("/")[0]
        if "onrender.com" not in clean_host and "localhost" not in clean_host and "127.0.0.1" not in clean_host and ":" not in clean_host:
            raw_url = f"https://{clean_host}.onrender.com"

        return raw_url

    if os.path.exists("/.dockerenv"):
        return "http://backend:8000"

    return "http://localhost:8000"

API_BASE_URL = resolve_backend_url()

# Seconds to wait before giving up on a backend request.
API_TIMEOUT = 30

APP_TITLE = "Autodesk Support Portal"