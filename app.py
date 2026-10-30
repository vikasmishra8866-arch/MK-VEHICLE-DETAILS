"""
Vehicle Information Lookup Portal
---------------------------------
A production-ready, dark-cyberpunk styled Streamlit application that performs
vehicle registration lookups against the "mvahan" API endpoint.

Author : Elite Full-Stack Python / UI-UX Engineering
Deploy : Streamlit Community Cloud (single file `app.py`)
"""

import html
import math
import re
import time

import requests
import streamlit as st

# =============================================================================
# 1. CONFIGURATION
# =============================================================================

API_URL = "https://hideme.eu.org/lookup"
API_PARAMS = {"api": "mvahan", "key": "mk-4px4ohkcxybb"}

COOLDOWN_SECONDS = 10      # Strict anti-spam window
REQUEST_TIMEOUT = 30       # Seconds before the HTTP call is abandoned
MIN_REG_LENGTH = 6         # Loose sanity check on the cleaned input

st.set_page_config(
    page_title="Vehicle Information Lookup Portal",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# 2. GLOBAL CSS  —  Ultra-premium dark cyberpunk / glassmorphism
# =============================================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --vi-bg:        #060911;
    --vi-card:      #0f172a;
    --vi-blue:      #3b82f6;
    --vi-emerald:   #22c55e;
    --vi-text:      #e2e8f0;
    --vi-muted:     #94a3b8;
    --vi-border:    rgba(255,255,255,0.08);
}

/* ----------  Global canvas  ---------- */
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 12% 8%,  rgba(59,130,246,0.14), transparent 42%),
        radial-gradient(circle at 88% 92%, rgba(34,197,94,0.10),  transparent 42%),
        radial-gradient(circle at 50% 50%, rgba(99,102,241,0.06), transparent 60%),
        #060911;
    background-attachment: fixed;
    color: var(--vi-text);
}

/* ----------  Kill Streamlit chrome  ---------- */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"] { display: none !important; }
.stDeployButton { display: none !important; }
#root > div:nth-child(1) > div > div > div > div > section
    > div > div > div > div > div { gap: 0.9rem; }

/* ----------  Page container  ---------- */
.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px;
}

/* ----------  Hero header  ---------- */
.vi-header {
    text-align: center;
    padding: 14px 0 26px 0;
}
.vi-header-eyebrow {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: #7dd3fc;
    background: rgba(59,130,246,0.10);
    border: 1px solid rgba(59,130,246,0.32);
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 18px;
}
.vi-header h1 {
    font-size: clamp(1.85rem, 4vw, 2.9rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
    background: linear-gradient(100deg, #ffffff 0%, #93c5fd 45%, #22c55e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.vi-header p {
    color: var(--vi-muted);
    font-size: 0.95rem;
    margin-top: 10px;
    font-weight: 400;
}

/* ----------  Glass panel (search zone)  ---------- */
.vi-panel {
    background: rgba(15, 23, 42, 0.62);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--vi-border);
    border-radius: 24px;
    padding: 26px 26px 20px 26px;
    box-shadow: 0 18px 46px rgba(0,0,0,0.55),
                inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 26px;
}
.vi-panel-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #7dd3fc;
    margin-bottom: 14px;
}

/* ----------  Text input  ---------- */
div[data-testid="stTextInput"] div[data-baseweb="input"] {
    background: rgba(6, 9, 17, 0.85) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 14px !important;
    transition: all 0.22s ease;
}
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: var(--vi-blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.18),
                0 0 24px rgba(59,130,246,0.20) !important;
}
div[data-testid="stTextInput"] input {
    background: transparent !important;
    color: var(--vi-text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.02rem !important;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    padding: 13px 16px !important;
    caret-color: var(--vi-emerald);
}
div[data-testid="stTextInput"] input::placeholder {
    color: rgba(148,163,184,0.45) !important;
    letter-spacing: 0.14em;
}
div[data-testid="stTextInput"] label { display: none !important; }

/* ----------  Primary button  ---------- */
div[data-testid="stButton"] > button,
.stButton > button {
    width: 100%;
    height: 52px;
    background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 45%, #22c55e 130%);
    color: #ffffff;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    box-shadow: 0 10px 28px rgba(59,130,246,0.30);
    transition: transform 0.20s ease, box-shadow 0.20s ease, border-color 0.20s ease;
}
div[data-testid="stButton"] > button:hover,
.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(34,197,94,0.65);
    box-shadow: 0 16px 36px rgba(59,130,246,0.45);
    color: #ffffff;
}
div[data-testid="stButton"] > button:active,
.stButton > button:active { transform: translateY(0); }

/* ----------  Result cards  ---------- */
.vi-card {
    background: rgba(15, 23, 42, 0.70);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid var(--vi-border);
    border-radius: 22px;
    padding: 20px 22px 14px 22px;
    margin-bottom: 18px;
    box-shadow: 0 12px 34px rgba(0,0,0,0.48),
                inset 0 1px 0 rgba(255,255,255,0.04);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.vi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(59,130,246,0.38);
    box-shadow: 0 18px 44px rgba(0,0,0,0.60),
                0 0 30px rgba(59,130,246,0.16);
}
.vi-card-head {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 12px;
    margin-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.vi-card-icon {
    font-size: 1.05rem;
    filter: drop-shadow(0 0 8px rgba(59,130,246,0.55));
}
.vi-card-title {
    font-size: 0.80rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #93c5fd;
}

/* ----------  Key / value rows  ---------- */
.vi-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 18px;
    padding: 9px 0;
    border-bottom: 1px dashed rgba(255,255,255,0.05);
}
.vi-row:last-child { border-bottom: none; }
.vi-label {
    color: var(--vi-muted);
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    white-space: nowrap;
    padding-top: 2px;
}
.vi-value {
    color: var(--vi-text);
    font-size: 0.92rem;
    font-weight: 600;
    text-align: right;
    word-break: break-word;
    line-height: 1.45;
}
.vi-value.mono {
    font-family: 'JetBrains Mono', monospace;
    color: #7dd3fc;
    letter-spacing: 0.06em;
}
.vi-empty {
    color: rgba(148,163,184,0.55);
    font-size: 0.85rem;
    font-style: italic;
    padding: 10px 0 16px 0;
}

/* ----------  Hero result banner  ---------- */
.vi-hero {
    background:
        linear-gradient(135deg, rgba(59,130,246,0.16) 0%, rgba(15,23,42,0.72) 42%, rgba(34,197,94,0.13) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(59,130,246,0.28);
    border-radius: 24px;
    padding: 26px 28px;
    margin-bottom: 24px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    box-shadow: 0 18px 48px rgba(0,0,0,0.55),
                0 0 46px rgba(59,130,246,0.10);
}
.vi-hero-label {
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.30em;
    text-transform: uppercase;
    color: #7dd3fc;
    margin-bottom: 8px;
}
.vi-hero-reg {
    font-family: 'JetBrains Mono', monospace;
    font-size: clamp(1.5rem, 3.4vw, 2.15rem);
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #ffffff;
    text-shadow: 0 0 26px rgba(59,130,246,0.60);
    line-height: 1.1;
}
.vi-hero-sub {
    color: var(--vi-muted);
    font-size: 0.90rem;
    margin-top: 8px;
    font-weight: 400;
}
.vi-hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
}

/* ----------  Badges  ---------- */
.vi-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 13px;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    white-space: nowrap;
}
.vi-badge.blue {
    background: rgba(59,130,246,0.13);
    border: 1px solid rgba(59,130,246,0.42);
    color: #93c5fd;
}
.vi-badge.green {
    background: rgba(34,197,94,0.13);
    border: 1px solid rgba(34,197,94,0.42);
    color: #86efac;
}
.vi-badge.grey {
    background: rgba(148,163,184,0.10);
    border: 1px solid rgba(148,163,184,0.28);
    color: #cbd5e1;
}

/* ----------  Alerts  ---------- */
.vi-alert {
    display: flex;
    align-items: center;
    gap: 12px;
    border-radius: 18px;
    padding: 16px 20px;
    font-size: 0.90rem;
    font-weight: 600;
    margin-bottom: 16px;
    line-height: 1.5;
}
.vi-alert.error {
    background: rgba(239,68,68,0.10);
    border: 1px solid rgba(239,68,68,0.38);
    color: #fca5a5;
    animation: viPulse 2.1s ease-in-out infinite;
}
.vi-alert.info {
    background: rgba(59,130,246,0.10);
    border: 1px solid rgba(59,130,246,0.38);
    color: #93c5fd;
}
@keyframes viPulse {
    0%, 100% { box-shadow: 0 0 0 rgba(239,68,68,0); }
    50%      { box-shadow: 0 0 26px rgba(239,68,68,0.30); }
}

/* ----------  Meta / credits strip  ---------- */
.vi-meta {
    margin-top: 26px;
    padding: 16px 20px;
    border-radius: 16px;
    background: rgba(15,23,42,0.55);
    border: 1px solid rgba(255,255,255,0.06);
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px 26px;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(148,163,184,0.80);
}
.vi-meta b { color: #7dd3fc; font-weight: 700; }

/* ----------  Spinner  ---------- */
[data-testid="stSpinner"] > div { border-top-color: var(--vi-emerald) !important; }
[data-testid="stSpinner"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.10em;
    color: #7dd3fc !important;
    text-transform: uppercase;
}

/* ----------  Footer  ---------- */
.vi-footer {
    text-align: center;
    margin-top: 34px;
    padding-top: 18px;
    border-top: 1px solid rgba(255,255,255,0.05);
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(148,163,184,0.55);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================================
# 3. SESSION STATE
# =============================================================================

_DEFAULTS = {
    "last_request_ts": 0.0,   # epoch timestamp of the last API hit
    "result": None,           # last successful payload
    "error": None,            # last error message string
    "last_number": "",        # cleaned number of the last successful lookup
}
for _key, _default in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

# =============================================================================
# 4. HELPERS
# =============================================================================

_PLACEHOLDERS = {"", "-", "--", "null", "none", "nan", "na", "n/a", "nil"}


def clean_value(value, fallback: str = "—") -> str:
    """
    Safely normalise any JSON value into a display-ready string.

    Returns `fallback` for None / empty / placeholder-like values so the UI
    never renders blank or "None" fields.
    """
    if value is None:
        return fallback
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).strip()
    if text.lower() in _PLACEHOLDERS:
        return fallback
    return text


def is_meaningful(value) -> bool:
    """True when the value would actually render something useful."""
    return clean_value(value) != "—"


def build_rows(pairs) -> str:
    """
    Convert [(label, value, is_mono), ...] into card row HTML.
    Null / empty values are silently dropped.
    """
    rows = []
    for label, value, mono in pairs:
        if not is_meaningful(value):
            continue
        display = html.escape(clean_value(value))
        css = "vi-value mono" if mono else "vi-value"
        rows.append(
            f'<div class="vi-row">'
            f'<span class="vi-label">{html.escape(label)}</span>'
            f'<span class="{css}">{display}</span>'
            f"</div>"
        )
    if not rows:
        return '<div class="vi-empty">No records available for this section.</div>'
    return "".join(rows)


def render_card(icon: str, title: str, pairs) -> str:
    """Build the full glass card HTML for a section."""
    return (
        f'<div class="vi-card">'
        f'  <div class="vi-card-head">'
        f'    <span class="vi-card-icon">{icon}</span>'
        f'    <span class="vi-card-title">{html.escape(title)}</span>'
        f"  </div>"
        f"  {build_rows(pairs)}"
        f"</div>"
    )


def render_alert(message: str, kind: str = "error") -> None:
    """Render a styled alert box."""
    icon = "⚠️" if kind == "error" else "ℹ️"
    st.markdown(
        f'<div class="vi-alert {kind}"><span>{icon}</span><span>{html.escape(message)}</span></div>',
        unsafe_allow_html=True,
    )


def sanitise_registration(raw: str) -> str:
    """Strip everything non-alphanumeric and force uppercase."""
    return re.sub(r"[^A-Za-z0-9]", "", raw or "").upper()


def cooldown_remaining() -> float:
    """Seconds left before another API call is permitted (0 if ready)."""
    elapsed = time.time() - float(st.session_state.get("last_request_ts", 0.0))
    return max(0.0, COOLDOWN_SECONDS - elapsed)


def fetch_vehicle(number: str) -> dict:
    """Perform the API request and return the parsed JSON payload."""
    params = dict(API_PARAMS)
    params["number"] = number
    response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


# =============================================================================
# 5. HEADER
# =============================================================================

st.markdown(
    """
    <div class="vi-header">
        <div class="vi-header-eyebrow">Secure Vahan Gateway</div>
        <h1>Vehicle Information Lookup</h1>
        <p>Decode registration records, technical specifications and insurance data in real time.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# 6. SEARCH PANEL
# =============================================================================

st.markdown('<div class="vi-panel">', unsafe_allow_html=True)
st.markdown('<div class="vi-panel-title">Registration Number</div>', unsafe_allow_html=True)

col_input, col_button = st.columns([3, 1], gap="medium")

with col_input:
    raw_number = st.text_input(
        "Registration Number",
        value="",
        placeholder="GJ39CD0387",
        label_visibility="collapsed",
        key="reg_input",
        max_chars=16,
    )

with col_button:
    search_clicked = st.button("🔍  Decode", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 7. SEARCH HANDLER
# =============================================================================

if search_clicked:
    cleaned = sanitise_registration(raw_number)

    if len(cleaned) < MIN_REG_LENGTH:
        st.session_state.error = (
            "Please enter a valid registration number (e.g. GJ39CD0387)."
        )
        st.session_state.result = None

    else:
        remaining = cooldown_remaining()
        if remaining > 0:
            st.session_state.error = (
                f"Cooldown active — please wait "
                f"{math.ceil(remaining)}s before the next lookup."
            )
        else:
            st.session_state.error = None
            st.session_state.last_request_ts = time.time()

            try:
                with st.spinner("Decrypting vehicle records from Vahan…"):
                    payload = fetch_vehicle(cleaned)

                if isinstance(payload, dict) and payload.get("success"):
                    st.session_state.result = payload
                    st.session_state.last_number = cleaned
                elif isinstance(payload, dict):
                    st.session_state.result = None
                    st.session_state.error = (
                        str(payload.get("message") or payload.get("error")
                            or "No records were found for this registration number.")
                    )
                else:
                    st.session_state.result = None
                    st.session_state.error = "Unexpected response format from the server."

            except requests.exceptions.Timeout:
                st.session_state.result = None
                st.session_state.error = "The request timed out. Please try again."
            except requests.exceptions.ConnectionError:
                st.session_state.result = None
                st.session_state.error = "Network error — unable to reach the lookup service."
            except requests.exceptions.HTTPError as exc:
                st.session_state.result = None
                st.session_state.error = f"Server returned an error: {exc.response.status_code}"
            except ValueError:
                st.session_state.result = None
                st.session_state.error = "Received malformed data from the server."
            except Exception as exc:  # noqa: BLE001 — last-resort guard
                st.session_state.result = None
                st.session_state.error = f"Unexpected error: {exc}"

# ---- Render any pending error ----------------------------------------------
if st.session_state.error:
    render_alert(st.session_state.error, "error")

# =============================================================================
# 8. RESULT RENDERING
# =============================================================================

data = st.session_state.result

if data:
    vehicle = data.get("vehicle") or {}

    # ------------------------------------------------------------------ HERO
    reg_no = clean_value(vehicle.get("registration_no") or data.get("reg_no"), "—")
    make = clean_value(vehicle.get("make"), "")
    model = clean_value(vehicle.get("model"), "")
    variant = clean_value(vehicle.get("variant"), "")

    title_bits = [b for b in (make, model) if b]
    subtitle = " · ".join(title_bits) if title_bits else "Vehicle Record"
    if variant:
        subtitle = f"{subtitle} · {variant}"

    badge_html = []
    if is_meaningful(vehicle.get("fuel")):
        badge_html.append(f'<span class="vi-badge blue">{html.escape(clean_value(vehicle.get("fuel")))}</span>')
    if is_meaningful(vehicle.get("vehicle_class")):
        badge_html.append(f'<span class="vi-badge green">{html.escape(clean_value(vehicle.get("vehicle_class")))}</span>')
    if is_meaningful(vehicle.get("vehicle_category")):
        badge_html.append(f'<span class="vi-badge grey">{html.escape(clean_value(vehicle.get("vehicle_category")))}</span>')
    if is_meaningful(vehicle.get("body_type")):
        badge_html.append(f'<span class="vi-badge grey">{html.escape(clean_value(vehicle.get("body_type")))}</span>')

    st.markdown(
        f"""
        <div class="vi-hero">
            <div>
                <div class="vi-hero-label">Registration Number</div>
                <div class="vi-hero-reg">{html.escape(reg_no)}</div>
                <div class="vi-hero-sub">{html.escape(subtitle)}</div>
            </div>
            <div class="vi-hero-badges">{''.join(badge_html)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------ OWNER CARD
    owner_card = render_card(
        "👤",
        "Owner Details",
        [
            ("Owner Name",       vehicle.get("owner"),            False),
            ("Father's Name",    vehicle.get("father_name"),      False),
            ("Mobile",           data.get("mobile"),              True),
            ("Vehicle Class",    vehicle.get("vehicle_class"),    False),
            ("Category",         vehicle.get("vehicle_category"), False),
            ("Financier",        vehicle.get("financier"),        False),
            ("Registered RTO",   vehicle.get("rto"),              False),
            ("Registration Date", vehicle.get("registration_date"), False),
        ],
    )

    # --------------------------------------------------------- TECHNICAL CARD
    technical_card = render_card(
        "⚙️",
        "Technical Specifications",
        [
            ("Make",              vehicle.get("make"),              False),
            ("Model",             vehicle.get("model"),             False),
            ("Variant",           vehicle.get("variant"),           False),
            ("Fuel Type",         vehicle.get("fuel"),              False),
            ("Chassis Number",    vehicle.get("chassis"),           True),
            ("Engine Number",     vehicle.get("engine"),            True),
            ("Colour",            vehicle.get("color"),             False),
            ("Body Type",         vehicle.get("body_type"),         False),
            ("Cubic Capacity",    vehicle.get("cubic_capacity"),    False),
            ("Seating Capacity",  vehicle.get("seating_capacity"),  False),
            ("Emission Norms",    vehicle.get("norms"),             False),
            ("Fitness Upto",      vehicle.get("fit_upto"),          False),
            ("Tax Upto",          vehicle.get("tax_upto"),          False),
            ("Vehicle Status",    vehicle.get("status"),            False),
        ],
    )

    # --------------------------------------------------------- INSURANCE CARD
    insurance_card = render_card(
        "🛡️",
        "Insurance & Compliance",
        [
            ("Insurance Company",  vehicle.get("insurance_company"),   False),
            ("Policy Number",      vehicle.get("insurance_policy_no"), True),
            ("Insurance Valid Upto", vehicle.get("insurance_upto"),    False),
            ("PUC Certificate No", vehicle.get("puc_no"),              True),
            ("PUC Valid Upto",     vehicle.get("puc_upto"),            False),
            ("Status As On",       vehicle.get("status_as_on"),        False),
        ],
    )

    # ----------------------------------------------------------- ADDRESS CARD
    address_card = render_card(
        "📍",
        "Registered Address",
        [
            ("Full Address", vehicle.get("address"), False),
            ("City / District", vehicle.get("city"), False),
            ("RTO Jurisdiction", vehicle.get("rto"), False),
            ("Data Source", vehicle.get("source"), False),
        ],
    )

    # ------------------------------------------------------------- 2-COL GRID
    left_col, right_col = st.columns(2, gap="medium")
    with left_col:
        st.markdown(owner_card, unsafe_allow_html=True)
        st.markdown(insurance_card, unsafe_allow_html=True)
    with right_col:
        st.markdown(technical_card, unsafe_allow_html=True)
        st.markdown(address_card, unsafe_allow_html=True)

    # ---------------------------------------------------------------- META BAR
    meta_bits = []
    if is_meaningful(data.get("runtime")):
        meta_bits.append(f"Runtime <b>{html.escape(clean_value(data.get('runtime')))}</b>")
    if is_meaningful(data.get("timestamp")):
        meta_bits.append(f"Fetched <b>{html.escape(clean_value(data.get('timestamp')))}</b>")
    if is_meaningful(data.get("key_expiry")):
        meta_bits.append(f"Key Expiry <b>{html.escape(clean_value(data.get('key_expiry')))}</b>")
    if is_meaningful(data.get("credits")):
        meta_bits.append(f"Credits <b>{html.escape(clean_value(data.get('credits')))}</b>")
    if is_meaningful(data.get("developer")):
        meta_bits.append(f"Developer <b>{html.escape(clean_value(data.get('developer')))}</b>")

    if meta_bits:
        st.markdown(
            f'<div class="vi-meta">{"".join(f"<span>{m}</span>" for m in meta_bits)}</div>',
            unsafe_allow_html=True,
        )

# =============================================================================
# 9. EMPTY STATE + FOOTER
# =============================================================================

elif not st.session_state.error:
    render_alert(
        "Enter a registration number above and hit “Decode” to retrieve the full vehicle profile.",
        "info",
    )

st.markdown(
    '<div class="vi-footer">Vehicle Information Lookup Portal · Powered by Vahan Gateway</div>',
    unsafe_allow_html=True,
)
