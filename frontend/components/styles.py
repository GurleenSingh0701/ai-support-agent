"""
Shared styling for the Autodesk Support Portal — enterprise console theme.

Design tokens live only here, so every page stays consistent and we
don't copy-paste <style> blocks. Pages layer page-specific CSS on top
after calling inject_base_css().

Palette:
    --bg:            #F4F5F7  app background
    --surface:       #FFFFFF  cards, inputs
    --border:        #DDE1E7  hairline borders
    --text:          #14181F  primary text
    --text-muted:    #5B6472  secondary text / labels
    --navy:          #122A46  sidebar / masthead
    --accent:        #2454A6  primary action / links
    --success:       #166C3B
    --warning:       #92620A
    --danger:        #B3261E

Type: IBM Plex Sans for UI text, IBM Plex Mono for IDs/data — a
deliberate "console" pairing rather than a generic sans default.
Layout: flat surfaces, hairline borders, 4px radius, no blur or
gradients, dense spacing, uppercase micro-labels.
Signature: a colored left-border strip on every ticket/status row.
"""

import streamlit as st

_FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2"
    "?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');"
)

_BASE_CSS = f"""
<style>
    {_FONT_IMPORT}

    :root {{
        --bg: #F4F5F7;
        --surface: #FFFFFF;
        --border: #DDE1E7;
        --text: #14181F;
        --text-muted: #5B6472;
        --navy: #122A46;
        --accent: #2454A6;
        --success: #166C3B;
        --warning: #92620A;
        --danger: #B3261E;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
    }}

    .stApp {{
        background: var(--bg) !important;
        color: var(--text) !important;
    }}

    h1, h2, h3, h4 {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.01em !important;
    }}

    code, .stCode, .stCode * {{
        font-family: 'IBM Plex Mono', monospace !important;
    }}

    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    ::-webkit-scrollbar-thumb {{ background: #C3C9D2; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #A3ABB8; }}

    /* Micro-label utility: small uppercase caption above sections */
    .eyebrow {{
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }}

    /* Flat bordered surface used for custom cards */
    .console-card {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        padding: 1rem 1.25rem !important;
    }}

    /* Buttons: rectangular, flat, no gradients */
    div.stButton > button {{
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        transition: background-color 0.12s ease, border-color 0.12s ease !important;
        box-shadow: none !important;
    }}
    div.stButton > button:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}
    div.stButton > button[kind="primary"] {{
        background: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        color: #FFFFFF !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background: #1D4482 !important;
        border-color: #1D4482 !important;
        color: #FFFFFF !important;
    }}

    /* Sidebar: dense dark navy console rail, not a glass panel */
    section[data-testid="stSidebar"] {{
        background: var(--navy) !important;
        border-right: 1px solid #0B1B2E !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #E7EBF2 !important;
    }}
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
        border-radius: 4px !important;
    }}

    /* Inputs: flat, hairline border, sharp corners */
    div[data-baseweb="base-input"], div[data-baseweb="textarea"] {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
    }}
    div[data-baseweb="base-input"]:focus-within, div[data-baseweb="textarea"]:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: var(--text-muted) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
    }}

    /* Notifications: flat with colored left border */
    div[data-testid="stNotification"] {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-left: 3px solid var(--accent) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
    }}

    /* Metrics: dense bordered stat blocks */
    div[data-testid="stMetric"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        padding: 0.9rem 1.1rem !important;
    }}
    div[data-testid="stMetric"] label {{
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: var(--text) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }}

    /* Generic bordered containers (st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: var(--border) !important;
        border-radius: 4px !important;
        background: var(--surface) !important;
    }}

    div[data-testid="stTabs"] {{
        border-bottom: 1px solid var(--border) !important;
    }}
    button[data-baseweb="tab"] {{
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
    }}
</style>
"""


def inject_base_css() -> None:
    """Inject the shared base CSS. Call once near the top of every page."""
    st.markdown(_BASE_CSS, unsafe_allow_html=True)