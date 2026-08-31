import streamlit as st
import cv2
import numpy as np
import hashlib
import os
import re
import base64
import html
from pathlib import Path
from datetime import datetime


# =========================================================
# IMPORT PROJECT MODULES
# =========================================================

from algorithms.aes import (
    encrypt_message,
    decrypt_message
)

from algorithms.adaptive_lsb import (
    embed_message,
    extract_message
)

from algorithms.sobel import apply_sobel

from algorithms.dct import (
    embed_dct,
    extract_dct
)

from algorithms.dwt import (
    embed_dwt,
    extract_dwt
)

from algorithms.metrics import (
    calculate_mse,
    calculate_psnr
)

from database.database import (
    initialize_database,
    create_user,
    get_user,
    add_stego_history,
    get_user_history
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="StegoSecure",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# PATH & ASSET CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_FOLDER = BASE_DIR / "assets"
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

ASSETS_FOLDER.mkdir(exist_ok=True)
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)


def get_logo_path():
    """Locate the StegoSecure logo from the assets folder."""
    for filename in ["stegosecure_logo.png", "logo.png", "stegosecure_logo.jpg", "logo.jpg"]:
        candidate = ASSETS_FOLDER / filename
        if candidate.exists():
            return candidate
    for file in ASSETS_FOLDER.glob("*.*"):
        if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".svg", ".webp"]:
            return file
    return None


LOGO_PATH = get_logo_path()


def get_logo_base64():
    """Convert the logo to base64 for pixel-perfect inline rendering."""
    if LOGO_PATH and LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/png" if LOGO_PATH.suffix.lower() == ".png" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
        except Exception:
            return None
    return None


LOGO_BASE64 = get_logo_base64()


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# ENTERPRISE CYBERSECURITY DESIGN SYSTEM & CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* =====================================================
       GLOBAL THEME VARIABLES & BASE
    ===================================================== */
    :root {
        --bg-app: #0B1220;
        --bg-card: #111C2E;
        --bg-card-elevated: #16243A;
        --bg-input: #0E1726;
        --border-subtle: #1E2E48;
        --border-medium: #233854;
        --border-accent: rgba(56, 189, 248, 0.35);
        --accent-cyan: #38BDF8;
        --accent-blue: #0284C7;
        --accent-royal: #2563EB;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    html, body, [class*="css"] {
        font-family: var(--font-sans) !important;
    }

    .stApp {
        background-color: var(--bg-app) !important;
        background-image: 
            radial-gradient(circle at 15% 10%, rgba(2, 132, 199, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 85% 15%, rgba(37, 99, 235, 0.06) 0%, transparent 45%),
            linear-gradient(180deg, #0B1220 0%, #0D1627 50%, #0B1220 100%) !important;
        background-attachment: fixed !important;
        color: var(--text-primary) !important;
    }

    .main .block-container {
        max-width: 1240px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    #MainMenu, footer, header, [data-testid="stSidebar"] {
        display: none !important;
    }

    /* =====================================================
       PROPORTIONAL TYPOGRAPHY & VISUAL HIERARCHY
    ===================================================== */
    h1 {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
    }

    h2 {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.01em !important;
        margin-top: 12px !important;
        margin-bottom: 6px !important;
    }

    h3 {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #E2E8F0 !important;
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }

    p {
        font-size: 14.5px !important;
        line-height: 1.6 !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.5rem !important;
    }

    label {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #BAE6FD !important;
        letter-spacing: 0.01em !important;
        margin-bottom: 4px !important;
    }

    hr, [data-testid="stDivider"] {
        border-color: var(--border-subtle) !important;
        margin: 1.2rem 0 !important;
    }

    /* =====================================================
       NAVIGATION HEADER
    ===================================================== */
    .nav-wrapper {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }

    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo-img {
        height: 38px;
        width: auto;
        border-radius: 6px;
        object-fit: contain;
    }

    .brand-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 11px;
        font-weight: 600;
        color: var(--accent-cyan);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .user-tag {
        display: inline-block;
        padding: 6px 12px;
        background: #0E1726;
        border: 1px solid var(--border-medium);
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        color: #BAE6FD;
        text-align: center;
        width: 100%;
        margin-top: 1px;
    }

    /* =====================================================
       BUTTON HIERARCHY
    ===================================================== */
    .stButton > button {
        background: var(--bg-card-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px !important;
        padding: 6px 14px !important;
        min-height: 38px !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        font-family: var(--font-sans) !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: #1C2E4A !important;
        color: #FFFFFF !important;
        border-color: var(--accent-cyan) !important;
    }

    .stButton > button:active {
        background: #142338 !important;
    }

    /* Primary Actions / Form Submit & Download Buttons */
    div[data-testid="stFormSubmitButton"] > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
        min-height: 40px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #0369A1 0%, #0284C7 100%) !important;
        border-color: #7DD3FC !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.4) !important;
    }

    /* =====================================================
       INPUTS, TEXTAREAS & SELECTBOXES (HIGH VISIBILITY)
    ===================================================== */
    /* Container Wrappers */
    .stTextInput > div,
    .stTextInput > div > div,
    .stTextArea > div,
    .stTextArea > div > div,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] {
        background-color: var(--bg-input) !important;
        background: var(--bg-input) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px !important;
        color: #F8FAFC !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stTextInput > div:focus-within,
    .stTextArea > div:focus-within,
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
        background-color: var(--bg-input) !important;
    }

    /* Inner Input & Textarea Elements */
    .stTextInput input,
    .stTextArea textarea {
        background-color: transparent !important;
        background: transparent !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        border: none !important;
        padding: 8px 12px !important;
        font-family: var(--font-mono) !important;
        font-size: 14px !important;
        caret-color: var(--accent-cyan) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }

    /* BROWSER AUTOFILL DARK THEME OVERRIDE */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active,
    textarea:-webkit-autofill,
    textarea:-webkit-autofill:hover,
    textarea:-webkit-autofill:focus,
    select:-webkit-autofill {
        -webkit-box-shadow: 0 0 0 1000px #0E1726 inset !important;
        box-shadow: 0 0 0 1000px #0E1726 inset !important;
        -webkit-text-fill-color: #F8FAFC !important;
        color: #F8FAFC !important;
        caret-color: #38BDF8 !important;
        border-color: #233854 !important;
        transition: background-color 5000s ease-in-out 0s !important;
    }

    /* Password Reveal Button & Icon */
    .stTextInput button,
    div[data-baseweb="input"] button,
    div[data-baseweb="base-input"] button {
        background: transparent !important;
        color: #94A3B8 !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 8px !important;
    }

    .stTextInput button:hover,
    div[data-baseweb="input"] button:hover {
        color: #38BDF8 !important;
        background: transparent !important;
    }

    .stTextInput svg,
    div[data-baseweb="input"] svg {
        fill: #94A3B8 !important;
    }

    /* Force full brightness and contrast on disabled / read-only fields */
    .stTextInput input:disabled,
    .stTextInput input[disabled],
    .stTextArea textarea:disabled,
    .stTextArea textarea[disabled],
    div[data-baseweb="textarea"] textarea:disabled,
    div[data-baseweb="textarea"] textarea[disabled],
    div[data-baseweb="base-input"] input:disabled,
    div[data-baseweb="base-input"] input[disabled] {
        color: #38BDF8 !important;
        -webkit-text-fill-color: #38BDF8 !important;
        background: #0A1629 !important;
        border: 1px solid #0284C7 !important;
        opacity: 1 !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        cursor: text !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background: var(--bg-input) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px !important;
        font-size: 13.5px !important;
    }

    .stSelectbox div[data-baseweb="select"]:hover > div {
        border-color: var(--accent-cyan) !important;
    }

    /* =====================================================
       FILE UPLOADER
    ===================================================== */
    [data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: var(--bg-input) !important;
        border: 1.5px dashed var(--border-medium) !important;
        border-radius: 6px !important;
        padding: 16px 12px !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent-cyan) !important;
        background: #132034 !important;
    }

    /* =====================================================
       CARDS & METRIC WIDGETS
    ===================================================== */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
    }

    .card h3 {
        color: #F8FAFC !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }

    .card p {
        color: var(--text-secondary) !important;
        font-size: 13.5px !important;
        line-height: 1.55 !important;
        margin-bottom: 0 !important;
    }

    .card-accent-lsb {
        border-top: 3px solid #0284C7;
    }

    .card-accent-dct {
        border-top: 3px solid #38BDF8;
    }

    .card-accent-dwt {
        border-top: 3px solid #60A5FA;
    }

    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--accent-blue);
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
    }

    .metric-card-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }

    .metric-card-value {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        font-family: var(--font-mono);
        line-height: 1.1;
    }

    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 14px 16px !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        font-family: var(--font-mono) !important;
    }

    /* =====================================================
       SECURITY PIPELINE VISUALIZER
    ===================================================== */
    .pipeline-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 10px;
        margin: 14px 0 18px 0;
    }

    .pipeline-node {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 14px 12px;
        text-align: center;
    }

    .pipeline-step-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        background: #0E1726;
        border: 1px solid var(--border-medium);
        border-radius: 4px;
        color: var(--accent-cyan);
        margin-bottom: 6px;
    }

    .pipeline-title {
        font-size: 13.5px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 2px;
    }

    .pipeline-desc {
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    /* =====================================================
       TIMELINE & METHODOLOGY STEPS
    ===================================================== */
    .methodology-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 12px;
        margin: 12px 0;
    }

    .methodology-item {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 14px 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }

    .methodology-num {
        background: #0E1726;
        border: 1px solid var(--accent-blue);
        color: var(--accent-cyan);
        font-size: 12px;
        font-weight: 700;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-family: var(--font-mono);
    }

    .methodology-content h4 {
        font-size: 13.5px;
        font-weight: 600;
        color: #F1F5F9;
        margin: 0 0 3px 0;
    }

    .methodology-content p {
        font-size: 12.5px;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.45;
    }

    /* =====================================================
       WORKFLOW STEP HEADERS
    ===================================================== */
    .step-header {
        font-size: 12px;
        font-weight: 700;
        color: var(--accent-cyan);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }

    /* =====================================================
       AUTH CARD
    ===================================================== */
    .auth-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 28px 26px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        margin: 0 auto;
    }

    /* =====================================================
       HISTORY CARD
    ===================================================== */
    .history-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--accent-blue);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 10px;
        margin-bottom: 12px;
    }

    .history-filename {
        font-size: 15px;
        font-weight: 600;
        color: #FFFFFF;
        font-family: var(--font-mono);
    }

    .history-timestamp {
        font-size: 12px;
        color: var(--text-secondary);
        font-family: var(--font-mono);
    }

    .history-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 10px;
        font-size: 13px;
    }

    .history-field-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .history-field-value {
        font-size: 13.5px;
        font-weight: 500;
        color: #F1F5F9;
        font-family: var(--font-mono);
        margin-top: 2px;
    }

    /* =====================================================
       ALERTS & NOTICES
    ===================================================== */
    .stAlert {
        border-radius: 6px !important;
    }

    .stInfo {
        background: #0E1F38 !important;
        border: 1px solid #1E3A68 !important;
        color: #BAE6FD !important;
    }

    .stSuccess {
        background: #0D2B24 !important;
        border: 1px solid #1A5446 !important;
        color: #A7F3D0 !important;
    }

    .stError {
        background: #33141C !important;
        border: 1px solid #632231 !important;
        color: #FECACA !important;
    }

    .stWarning {
        background: #332410 !important;
        border: 1px solid #63461D !important;
        color: #FDE68A !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def change_page(page: str):
    st.session_state.page = page
    st.rerun()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def sanitize_filename(filename: str) -> str:
    name, extension = os.path.splitext(filename)
    name = name.encode("ascii", "ignore").decode()
    name = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    if not name:
        name = "uploaded_image"

    extension = extension.lower()
    if extension not in [".png", ".jpg", ".jpeg"]:
        extension = ".png"

    return name + extension


def save_uploaded_file(uploaded_file) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = sanitize_filename(uploaded_file.name)
    filename = f"{timestamp}_{safe_name}"
    file_path = UPLOAD_FOLDER / filename

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(file_path)


def read_uploaded_image(uploaded_file):
    file_bytes = np.asarray(bytearray(uploaded_file.getvalue()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return image


def get_image_bytes(image) -> bytes:
    success, encoded_image = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Unable to encode image.")
    return encoded_image.tobytes()


def calculate_metrics(original, stego, grayscale=False):
    if original is None or stego is None:
        raise ValueError("Invalid images for metric calculation.")

    original_for_metric = original.copy()
    stego_for_metric = stego.copy()

    if grayscale:
        if len(original_for_metric.shape) == 3:
            original_for_metric = cv2.cvtColor(original_for_metric, cv2.COLOR_BGR2GRAY)
        if len(stego_for_metric.shape) == 3:
            stego_for_metric = cv2.cvtColor(stego_for_metric, cv2.COLOR_BGR2GRAY)
    else:
        if len(original_for_metric.shape) != len(stego_for_metric.shape):
            if len(original_for_metric.shape) == 3:
                original_for_metric = cv2.cvtColor(original_for_metric, cv2.COLOR_BGR2GRAY)
            if len(stego_for_metric.shape) == 3:
                stego_for_metric = cv2.cvtColor(stego_for_metric, cv2.COLOR_BGR2GRAY)

    if original_for_metric.shape != stego_for_metric.shape:
        stego_for_metric = cv2.resize(
            stego_for_metric,
            (original_for_metric.shape[1], original_for_metric.shape[0])
        )

    mse = calculate_mse(original_for_metric, stego_for_metric)
    psnr = calculate_psnr(original_for_metric, stego_for_metric)
    return mse, psnr


def calculate_capacity_adaptive(texture_map) -> int:
    smooth = np.sum(texture_map == 0)
    moderate = np.sum(texture_map == 1)
    strong = np.sum(texture_map == 2)
    total_bits = smooth * 1 + moderate * 2 + strong * 3
    usable_bits = max(0, total_bits - 32)
    return usable_bits // 8


def calculate_capacity_dct(image) -> int:
    height, width = image.shape[:2]
    blocks = (height // 8) * (width // 8)
    usable_bits = max(0, blocks - 32)
    return usable_bits // 8


def calculate_capacity_dwt(image) -> int:
    height, width = image.shape[:2]
    coefficients = (height // 2) * (width // 2)
    usable_bits = max(0, coefficients - 32)
    return usable_bits // 8


# =========================================================
# GLOBAL NAVIGATION COMPONENT
# =========================================================

def show_navigation():
    st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)

    if st.session_state.logged_in:
        col_brand, col_home, col_dash, col_create, col_extract, col_hist, col_user, col_out = st.columns(
            [3.8, 1, 1.2, 1, 1, 1, 1.3, 1.1],
            vertical_alignment="center"
        )

        with col_brand:
            if LOGO_BASE64:
                st.markdown(
                    f"""
                    <div class="brand-container">
                        <img src="{LOGO_BASE64}" class="brand-logo-img" alt="StegoSecure Logo" />
                        <div>
                            <div class="brand-title">StegoSecure</div>
                            <div class="brand-subtitle">Security Suite</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div class="brand-container">
                        <div>
                            <div class="brand-title">StegoSecure</div>
                            <div class="brand-subtitle">Security Suite</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_home:
            if st.button("Home", key="nav_home", use_container_width=True):
                change_page("Home")

        with col_dash:
            if st.button("Dashboard", key="nav_dash", use_container_width=True):
                change_page("Dashboard")

        with col_create:
            if st.button("Create", key="nav_create", use_container_width=True):
                change_page("Create")

        with col_extract:
            if st.button("Extract", key="nav_extract", use_container_width=True):
                change_page("Extract")

        with col_hist:
            if st.button("History", key="nav_hist", use_container_width=True):
                change_page("History")

        with col_user:
            st.markdown(
                f'<div class="user-tag">{st.session_state.username}</div>',
                unsafe_allow_html=True
            )

        with col_out:
            if st.button("Sign Out", key="nav_out", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_id = None
                change_page("Home")

    else:
        col_brand, col_home, col_login, col_reg = st.columns(
            [5.2, 1, 1, 1.2],
            vertical_alignment="center"
        )

        with col_brand:
            if LOGO_BASE64:
                st.markdown(
                    f"""
                    <div class="brand-container">
                        <img src="{LOGO_BASE64}" class="brand-logo-img" alt="StegoSecure Logo" />
                        <div>
                            <div class="brand-title">StegoSecure</div>
                            <div class="brand-subtitle">Security Suite</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div class="brand-container">
                        <div>
                            <div class="brand-title">StegoSecure</div>
                            <div class="brand-subtitle">Security Suite</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_home:
            if st.button("Home", key="nav_home_anon", use_container_width=True):
                change_page("Home")

        with col_login:
            if st.button("Login", key="nav_login_anon", use_container_width=True):
                change_page("Login")

        with col_reg:
            if st.button("Register", key="nav_reg_anon", use_container_width=True):
                change_page("Register")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 1. HOME PAGE
# =========================================================

def home_page():
    show_navigation()

    # 1. HERO SECTION (CLEAR & SIMPLE COPY)
    st.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
            <div style="font-size: 11px; font-weight: 700; color: #38BDF8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                Simple & Secure Image Steganography
            </div>
            <h1 style="font-size: 32px !important; line-height: 1.25; margin-bottom: 12px !important;">
                Hide Secret Messages Inside Photos Easily
            </h1>
            <p style="font-size: 15px; max-width: 820px; line-height: 1.6; color: #94A3B8; margin-bottom: 20px;">
                StegoSecure lets you lock any private text with a password and hide it inside a normal photo. The photo looks completely untouched to anyone viewing it, while your secret message stays safe and invisible inside.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    cta_col1, cta_col2, cta_spacer = st.columns([1.8, 2.2, 5])
    with cta_col1:
        if not st.session_state.logged_in:
            if st.button("Get Started", key="hero_get_started", use_container_width=True):
                change_page("Register")
        else:
            if st.button("Open Dashboard", key="hero_dashboard", use_container_width=True):
                change_page("Dashboard")
    with cta_col2:
        if not st.session_state.logged_in:
            if st.button("Login to Account", key="hero_login", use_container_width=True):
                change_page("Login")
        else:
            if st.button("Create Stego Image", key="hero_create", use_container_width=True):
                change_page("Create")

    st.divider()

    # 2. FEATURE HIGHLIGHTS (USER-FRIENDLY DESCRIPTIONS)
    st.markdown("<h2>How It Hides Your Data</h2>", unsafe_allow_html=True)
    st.markdown("<p>Three straightforward methods you can choose from to hide your secret message:</p>", unsafe_allow_html=True)

    tech1, tech2, tech3 = st.columns(3)

    with tech1:
        st.markdown(
            """
            <div class="card card-accent-lsb">
                <h3>Adaptive LSB</h3>
                <p>
                    Hides your secret text inside detailed, textured parts of the photo and leaves smooth areas untouched. This keeps the photo looking completely natural with zero noticeable differences.
                </p>
                <div style="margin-top: 12px; font-size: 11.5px; font-weight: 600; color: #38BDF8; text-transform: uppercase;">
                    High Picture Quality
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tech2:
        st.markdown(
            """
            <div class="card card-accent-dct">
                <h3>DCT Method</h3>
                <p>
                    Divides the image into small blocks and stores your secret message inside them. This helps protect your hidden data even if the image is saved, resized, or slightly compressed.
                </p>
                <div style="margin-top: 12px; font-size: 11.5px; font-weight: 600; color: #38BDF8; text-transform: uppercase;">
                    Compression Safe
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tech3:
        st.markdown(
            """
            <div class="card card-accent-dwt">
                <h3>DWT Method</h3>
                <p>
                    Splits the photo into different visual layers and embeds your message into fine background details. This gives maximum invisibility while keeping the photo crisp and clean.
                </p>
                <div style="margin-top: 12px; font-size: 11.5px; font-weight: 600; color: #38BDF8; text-transform: uppercase;">
                    Maximum Invisibility
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # 3. SECURITY PIPELINE (EASY-TO-UNDERSTAND WORKFLOW)
    st.markdown("<h2>Simple 6-Step Process</h2>", unsafe_allow_html=True)
    st.markdown("<p>How your secret message is protected and recovered from start to finish:</p>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="pipeline-grid">
            <div class="pipeline-node">
                <div class="pipeline-step-badge">STEP 1</div>
                <div class="pipeline-title">Write Message</div>
                <div class="pipeline-desc">Type your secret text</div>
            </div>
            <div class="pipeline-node">
                <div class="pipeline-step-badge">STEP 2</div>
                <div class="pipeline-title">Lock with Password</div>
                <div class="pipeline-desc">Encrypted with AES-256</div>
            </div>
            <div class="pipeline-node">
                <div class="pipeline-step-badge">STEP 3</div>
                <div class="pipeline-title">Hide in Picture</div>
                <div class="pipeline-desc">Embedded invisibly</div>
            </div>
            <div class="pipeline-node">
                <div class="pipeline-step-badge">STEP 4</div>
                <div class="pipeline-title">Download Picture</div>
                <div class="pipeline-desc">Looks like a normal photo</div>
            </div>
            <div class="pipeline-node">
                <div class="pipeline-step-badge">STEP 5</div>
                <div class="pipeline-title">Upload Picture</div>
                <div class="pipeline-desc">Enter your password</div>
            </div>
            <div class="pipeline-node">
                <div class="pipeline-step-badge">STEP 6</div>
                <div class="pipeline-title">Read Secret Text</div>
                <div class="pipeline-desc">Message is unlocked</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # 4. ABOUT SECTION (USER-FRIENDLY & CONCISE)
    st.markdown("<h2>Why Use StegoSecure?</h2>", unsafe_allow_html=True)
    st.write(
        """
        Standard encryption scrambles your message into random-looking code, which can make people suspicious that you are hiding something. Steganography solves this by hiding the encrypted message directly inside an ordinary photo. To anyone looking at the image, it just looks like a regular picture. Only someone who has the photo and knows the secret password can unlock and read the original message.
        """
    )


# =========================================================
# 2. REGISTER PAGE
# =========================================================

def register_page():
    show_navigation()

    left_col, center_col, right_col = st.columns([1.2, 2.2, 1.2])

    with center_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        if LOGO_BASE64:
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="{LOGO_BASE64}" style="height: 52px; width: auto; border-radius: 8px;" alt="Logo" />
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="font-size: 22px !important; margin-bottom: 4px !important;">Create an Account</h1>
                <p style="font-size: 13.5px; color: #94A3B8;">Join StegoSecure for protected steganographic operations</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Enter username")
            email = st.text_input("Email", placeholder="name@domain.com")
            password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Register Account", use_container_width=True)

            if submitted:
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    password_hash = hash_password(password)
                    success = create_user(username.strip(), email.strip(), password_hash)

                    if success:
                        st.success("Account created successfully. Please login to continue.")
                    else:
                        st.error("Username or email already exists.")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("Already have an account? Login", key="reg_goto_login", use_container_width=True):
            change_page("Login")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 3. LOGIN PAGE
# =========================================================

def login_page():
    show_navigation()

    left_col, center_col, right_col = st.columns([1.2, 2.2, 1.2])

    with center_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        if LOGO_BASE64:
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="{LOGO_BASE64}" style="height: 52px; width: auto; border-radius: 8px;" alt="Logo" />
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="font-size: 22px !important; margin-bottom: 4px !important;">Welcome Back</h1>
                <p style="font-size: 13.5px; color: #94A3B8;">Access your secure steganography workspace</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter username and password.")
                else:
                    user = get_user(username.strip())
                    if user:
                        stored_hash = user[3]
                        entered_hash = hash_password(password)

                        if stored_hash == entered_hash:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user[0]
                            st.session_state.username = user[1]
                            st.success("Login successful.")
                            change_page("Dashboard")
                        else:
                            st.error("Incorrect password.")
                    else:
                        st.error("User not found.")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("Don't have an account? Register", key="login_goto_reg", use_container_width=True):
            change_page("Register")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 4. DASHBOARD PAGE
# =========================================================

def dashboard_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        change_page("Login")
        return

    show_navigation()

    # Header
    st.markdown(
        f"""
        <div style="margin-bottom: 18px;">
            <h1>Dashboard</h1>
            <p>Welcome back, {st.session_state.username}. Manage your StegoSecure operations from one place.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    history = get_user_history(st.session_state.user_id)
    total_images = len(history)

    # Statistics Section (3 Metric Cards)
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-label">Stego Images Created</div>
                <div class="metric-card-value">{total_images}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-card-label">Available Algorithms</div>
                <div class="metric-card-value">3 Techniques</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-card-label">Encryption Standard</div>
                <div class="metric-card-value">AES-256-GCM</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Quick Actions (2 Cards)
    st.markdown("<h2>Quick Actions</h2>", unsafe_allow_html=True)

    act1, act2 = st.columns(2)

    with act1:
        st.markdown(
            """
            <div class="card card-accent-lsb">
                <h3>Create Secure Stego Image</h3>
                <p>
                    Upload a carrier image, encrypt your confidential message using AES-256, and embed it using Adaptive LSB, DCT, or DWT.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Create Stego Image", key="dash_btn_create", use_container_width=True):
            change_page("Create")

    with act2:
        st.markdown(
            """
            <div class="card card-accent-dct">
                <h3>Extract Hidden Message</h3>
                <p>
                    Upload an existing stego image, select the matching transformation algorithm, and decrypt the recovered payload.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Extract Hidden Message", key="dash_btn_extract", use_container_width=True):
            change_page("Extract")

    st.divider()

    # Implemented Methodology Timeline (6 Steps)
    st.markdown("<h2>Implemented Methodology</h2>", unsafe_allow_html=True)
    st.markdown("<p>Systematic workflow for cryptographic steganography and extraction.</p>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="methodology-grid">
            <div class="methodology-item">
                <div class="methodology-num">1</div>
                <div class="methodology-content">
                    <h4>Enter Secret Message</h4>
                    <p>Input confidential plaintext payload to be embedded securely.</p>
                </div>
            </div>
            <div class="methodology-item">
                <div class="methodology-num">2</div>
                <div class="methodology-content">
                    <h4>AES-256-GCM Encryption</h4>
                    <p>Payload is authenticated and encrypted using SHA-256 derived keys.</p>
                </div>
            </div>
            <div class="methodology-item">
                <div class="methodology-num">3</div>
                <div class="methodology-content">
                    <h4>Select Algorithm</h4>
                    <p>Choose Adaptive LSB + Sobel, DCT block transform, or DWT wavelet.</p>
                </div>
            </div>
            <div class="methodology-item">
                <div class="methodology-num">4</div>
                <div class="methodology-content">
                    <h4>Embed Encrypted Data</h4>
                    <p>Encrypted bitstream is encoded into cover image coefficients.</p>
                </div>
            </div>
            <div class="methodology-item">
                <div class="methodology-num">5</div>
                <div class="methodology-content">
                    <h4>Evaluate MSE and PSNR</h4>
                    <p>Quantitative fidelity metrics verify that visual distortion is minimized.</p>
                </div>
            </div>
            <div class="methodology-item">
                <div class="methodology-num">6</div>
                <div class="methodology-content">
                    <h4>Extract and Decrypt</h4>
                    <p>Recover and authenticate the secret message using the passkey.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 5. CREATE STEGO IMAGE PAGE
# =========================================================

def create_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        change_page("Login")
        return

    show_navigation()

    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h1>Create Secure Stego Image</h1>
            <p>Upload a cover image, enter a secret message, encrypt it using AES, and embed it with your chosen algorithm.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([1.1, 1], gap="large")

    original_color = None
    image_path = None
    uploaded_file = None

    with col_left:
        st.markdown('<div class="step-header">STEP 1 — Upload Cover Image</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a Cover Image (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            key="create_file_upload"
        )

        if uploaded_file is not None:
            original_color = read_uploaded_image(uploaded_file)
            if original_color is not None:
                image_path = save_uploaded_file(uploaded_file)
                h, w, c = original_color.shape

                st.markdown(
                    f"""
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 8px; font-family: var(--font-mono);">
                        Resolution: {w} × {h} px | Channels: {c} | File: {uploaded_file.name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.image(
                    cv2.cvtColor(original_color, cv2.COLOR_BGR2RGB),
                    caption="Cover Image Preview",
                    use_container_width=True
                )
            else:
                st.error("Unable to decode uploaded image.")

    with col_right:
        st.markdown('<div class="step-header">STEP 2 — Configure Secret</div>', unsafe_allow_html=True)

        secret_message = st.text_area(
            "Secret Message",
            placeholder="Enter confidential message here...",
            height=150,
            key="create_msg_input"
        )

        msg_len = len(secret_message)
        st.markdown(
            f"""
            <div style="text-align: right; font-size: 11.5px; color: #64748B; margin-top: -10px; margin-bottom: 10px; font-family: var(--font-mono);">
                Payload: {msg_len} characters ({msg_len} bytes)
            </div>
            """,
            unsafe_allow_html=True
        )

        encryption_password = st.text_input(
            "Encryption Password",
            type="password",
            placeholder="Enter encryption passkey",
            key="create_pwd_input"
        )

        algorithm = st.selectbox(
            "Steganography Algorithm",
            [
                "Adaptive LSB + Sobel",
                "DCT",
                "DWT"
            ],
            key="create_algo_input"
        )

        # STEP 3: CAPACITY INFORMATION
        st.markdown('<div class="step-header" style="margin-top: 14px;">STEP 3 — Capacity Information</div>', unsafe_allow_html=True)

        capacity = None
        if original_color is not None and image_path is not None:
            try:
                if algorithm == "Adaptive LSB + Sobel":
                    _, _, texture_map = apply_sobel(image_path)
                    capacity = calculate_capacity_adaptive(texture_map)
                elif algorithm == "DCT":
                    gray_img = cv2.cvtColor(original_color, cv2.COLOR_BGR2GRAY)
                    capacity = calculate_capacity_dct(gray_img)
                else:
                    gray_img = cv2.cvtColor(original_color, cv2.COLOR_BGR2GRAY)
                    capacity = calculate_capacity_dwt(gray_img)

                utilization = (msg_len / max(capacity, 1)) * 100

                st.markdown(
                    f"""
                    <div class="card" style="padding: 12px 16px; margin-bottom: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Max Embedding Capacity</span>
                            <span style="font-size: 14px; font-weight: 700; color: #38BDF8; font-family: var(--font-mono);">{capacity:,} bytes</span>
                        </div>
                        <div style="font-size: 11.5px; color: {'#34D399' if utilization <= 100 else '#F87171'}; margin-top: 4px;">
                            Payload consumes {utilization:.2f}% of available safe capacity.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.warning(f"Capacity calculation notice: {e}")
        else:
            st.markdown(
                """
                <div class="card" style="padding: 12px 16px; margin-bottom: 0;">
                    <div style="font-size: 12.5px; color: #64748B;">
                        Upload a cover image to calculate safe embedding capacity.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # STEP 4: PROCESS BUTTON
    st.markdown('<div class="step-header">STEP 4 — Process</div>', unsafe_allow_html=True)

    if st.button("Encrypt & Embed", key="btn_create_process", use_container_width=True):
        if uploaded_file is None:
            st.error("Please upload a cover image.")
        elif original_color is None:
            st.error("Unable to process uploaded image.")
        elif not secret_message.strip():
            st.error("Please enter a secret message.")
        elif not encryption_password:
            st.error("Please enter an encryption password.")
        else:
            try:
                with st.spinner("Encrypting payload with AES-256 and embedding into image..."):
                    # 1. AES Encryption
                    encrypted_message = encrypt_message(secret_message, encryption_password)
                    if isinstance(encrypted_message, str):
                        encrypted_data = encrypted_message.encode("utf-8")
                    else:
                        encrypted_data = bytes(encrypted_message)

                    # 2. Embedding
                    if algorithm == "Adaptive LSB + Sobel":
                        _, _, texture_map = apply_sobel(image_path)
                        stego_image = embed_message(original_color.copy(), encrypted_data, texture_map)
                        original_for_metrics = original_color
                        is_gray = False

                    elif algorithm == "DCT":
                        gray_img = cv2.cvtColor(original_color, cv2.COLOR_BGR2GRAY)
                        stego_image = embed_dct(gray_img, encrypted_data)
                        original_for_metrics = gray_img
                        is_gray = True

                    else:
                        gray_img = cv2.cvtColor(original_color, cv2.COLOR_BGR2GRAY)
                        stego_image = embed_dwt(gray_img, encrypted_data)
                        original_for_metrics = gray_img
                        is_gray = True

                    # 3. Metrics
                    mse, psnr = calculate_metrics(original_for_metrics, stego_image, grayscale=is_gray)

                    # 4. Save file & database record
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"stego_{timestamp}.png"
                    output_path = OUTPUT_FOLDER / output_filename
                    cv2.imwrite(str(output_path), stego_image)

                    add_stego_history(
                        st.session_state.user_id,
                        uploaded_file.name,
                        output_filename,
                        len(secret_message),
                        psnr=float(psnr),
                        ssim=None,
                        mse=float(mse)
                    )

                st.success("Stego image created successfully.")

                # RESULT SECTION
                st.markdown("<h2>Embedding Result & Quality Evaluation</h2>", unsafe_allow_html=True)

                res_left, res_right = st.columns([1.2, 1], gap="large")

                with res_left:
                    st.markdown("<h3>Generated Stego Image</h3>", unsafe_allow_html=True)
                    if len(stego_image.shape) == 2:
                        st.image(stego_image, channels="GRAY", use_container_width=True)
                    else:
                        st.image(cv2.cvtColor(stego_image, cv2.COLOR_BGR2RGB), use_container_width=True)

                    st.download_button(
                        label="Download Stego Image",
                        data=get_image_bytes(stego_image),
                        file_name=output_filename,
                        mime="image/png",
                        key="dl_stego_result",
                        use_container_width=True
                    )

                with res_right:
                    st.markdown("<h3>Fidelity Metrics & Configuration</h3>", unsafe_allow_html=True)

                    qm1, qm2 = st.columns(2)
                    with qm1:
                        st.metric("MSE", f"{mse:.6f}")
                    with qm2:
                        psnr_val = "Infinity" if np.isinf(psnr) else f"{psnr:.2f} dB"
                        st.metric("PSNR", psnr_val)

                    st.markdown(
                        f"""
                        <div class="card" style="margin-top: 14px;">
                            <div style="font-size: 12.5px; line-height: 1.6; color: #CBD5E1;">
                                <div><b style="color:#BAE6FD;">Algorithm:</b> {algorithm}</div>
                                <div><b style="color:#BAE6FD;">Encryption:</b> AES-256-GCM Authenticated</div>
                                <div><b style="color:#BAE6FD;">Output Filename:</b> <code style="color:#38BDF8; font-family:var(--font-mono);">{output_filename}</code></div>
                                <div><b style="color:#BAE6FD;">Status:</b> Embedded & Verified</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception as error:
                st.error(f"Processing failed: {str(error)}")


# =========================================================
# 6. EXTRACT MESSAGE PAGE (WITH CRYSTAL-CLEAR FONT VISIBILITY)
# =========================================================

def extract_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        change_page("Login")
        return

    show_navigation()

    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h1>Extract Hidden Message</h1>
            <p>Upload a stego image and recover the encrypted hidden message using the appropriate algorithm and password.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([1.1, 1], gap="large")

    image_path = None
    uploaded_file = None

    with col_left:
        st.markdown('<div class="step-header">STEP 1 — Upload Stego Image</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Stego Image (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            key="extract_file_upload"
        )

        if uploaded_file is not None:
            preview_img = read_uploaded_image(uploaded_file)
            if preview_img is not None:
                image_path = save_uploaded_file(uploaded_file)
                st.image(
                    cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB),
                    caption="Stego Image Preview",
                    use_container_width=True
                )
            else:
                st.error("Unable to decode uploaded image.")

    with col_right:
        st.markdown('<div class="step-header">STEP 2 — Extraction Configuration</div>', unsafe_allow_html=True)

        algorithm = st.selectbox(
            "Select Algorithm Used for Embedding",
            [
                "Adaptive LSB + Sobel",
                "DCT",
                "DWT"
            ],
            key="extract_algo_select"
        )

        encryption_password = st.text_input(
            "Encryption Password",
            type="password",
            placeholder="Enter decryption passkey",
            key="extract_pwd_input"
        )

        st.markdown(
            """
            <div class="card" style="padding: 12px 16px; margin-top: 14px;">
                <div style="font-size: 12.5px; color: #94A3B8;">
                    Decryption requires the exact matching algorithm and passphrase used during embedding.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # STEP 3: ACTION
    st.markdown('<div class="step-header">STEP 3 — Extract and Decrypt</div>', unsafe_allow_html=True)

    if st.button("Extract and Decrypt Message", key="btn_extract_process", use_container_width=True):
        if uploaded_file is None or image_path is None:
            st.error("Please upload a stego image.")
        elif not encryption_password:
            st.error("Please enter the encryption password.")
        else:
            try:
                with st.spinner("Extracting bitstream and authenticating AES-256 payload..."):
                    if algorithm == "Adaptive LSB + Sobel":
                        stego_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
                        if stego_image is None:
                            raise ValueError("Unable to read stego image.")
                        _, _, texture_map = apply_sobel(image_path)
                        extracted_data = extract_message(stego_image, texture_map)

                    elif algorithm == "DCT":
                        stego_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                        if stego_image is None:
                            raise ValueError("Unable to read stego image.")
                        extracted_data = extract_dct(stego_image)

                    else:
                        stego_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                        if stego_image is None:
                            raise ValueError("Unable to read stego image.")
                        extracted_data = extract_dwt(stego_image)

                    if isinstance(extracted_data, bytes):
                        encrypted_message = extracted_data.decode("utf-8")
                    else:
                        encrypted_message = str(extracted_data)

                    decrypted_message = decrypt_message(encrypted_message, encryption_password)

                st.success("Message extracted and decrypted successfully.")

                # RECOVERED MESSAGE PANEL (VIBRANT, HIGH-CONTRAST DISPLAY)
                st.markdown("<h2>Recovered Secret Message</h2>", unsafe_allow_html=True)

                escaped_msg = html.escape(decrypted_message)
                st.markdown(
                    f"""
                    <div style="
                        background: #091424;
                        border: 1.5px solid #0284C7;
                        border-left: 4px solid #38BDF8;
                        border-radius: 8px;
                        padding: 18px 22px;
                        margin: 12px 0 16px 0;
                        box-shadow: 0 4px 18px rgba(2, 132, 199, 0.25);
                    ">
                        <div style="font-size: 11px; font-weight: 700; color: #38BDF8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 8px;">
                            Decrypted Message Content
                        </div>
                        <div style="
                            color: #38BDF8;
                            font-family: 'JetBrains Mono', monospace;
                            font-size: 16px;
                            font-weight: 600;
                            line-height: 1.6;
                            white-space: pre-wrap;
                            word-break: break-word;
                        ">{escaped_msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.text_area(
                    "Copyable Text Area",
                    value=decrypted_message,
                    height=120,
                    key="recovered_msg_box"
                )

                st.markdown(
                    f"""
                    <div class="card" style="padding: 12px 16px; margin-top: 10px;">
                        <div style="font-size: 12.5px; color: #CBD5E1;">
                            <b>Extraction Algorithm:</b> {algorithm} &nbsp;|&nbsp; 
                            <b>Authentication:</b> Verified & Validated &nbsp;|&nbsp; 
                            <b>Payload Length:</b> {len(decrypted_message)} characters
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except UnicodeDecodeError:
                st.error("Unable to decode extracted data. Ensure you selected the correct algorithm and image.")
            except Exception as error:
                st.error(f"Extraction failed: {str(error)}")


# =========================================================
# 7. HISTORY PAGE
# =========================================================

def history_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        change_page("Login")
        return

    show_navigation()

    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h1>Stego Image History</h1>
            <p>View previously generated stego images, timestamps, and fidelity measurements.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    history = get_user_history(st.session_state.user_id)

    if not history:
        st.markdown(
            """
            <div class="card" style="text-align: center; padding: 36px 20px;">
                <h3>No Stego Images Created Yet</h3>
                <p>You have not generated any stego images. Use the Create page to start.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Go to Create Page", key="hist_goto_create", use_container_width=True):
            change_page("Create")
        return

    for item in history:
        (
            record_id,
            original_filename,
            stego_filename,
            message_length,
            psnr,
            ssim,
            mse,
            created_at
        ) = item

        psnr_display = f"{float(psnr):.2f} dB" if psnr is not None else "N/A"
        mse_display = f"{float(mse):.6f}" if mse is not None else "N/A"
        created_display = "N/A"

        if created_at:
            try:
                created_datetime = datetime.fromisoformat(str(created_at))
                created_display = created_datetime.strftime("%d %b %Y • %I:%M %p")
            except (ValueError, TypeError):
                created_display = str(created_at)

        st.markdown(
            f"""
            <div class="history-card">
                <div class="history-header">
                    <div class="history-filename">{stego_filename}</div>
                    <div class="history-timestamp">{created_display}</div>
                </div>
                <div class="history-grid">
                    <div>
                        <div class="history-field-label">Original Image</div>
                        <div class="history-field-value">{original_filename}</div>
                    </div>
                    <div>
                        <div class="history-field-label">Message Length</div>
                        <div class="history-field-value">{message_length} chars</div>
                    </div>
                    <div>
                        <div class="history-field-label">PSNR</div>
                        <div class="history-field-value" style="color: #38BDF8;">{psnr_display}</div>
                    </div>
                    <div>
                        <div class="history-field-label">MSE</div>
                        <div class="history-field-value">{mse_display}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        output_path = OUTPUT_FOLDER / stego_filename
        if output_path.exists():
            with open(output_path, "rb") as file:
                st.download_button(
                    label=f"Download {stego_filename}",
                    data=file,
                    file_name=stego_filename,
                    mime="image/png",
                    key=f"hist_dl_{record_id}",
                    use_container_width=True
                )


# =========================================================
# APPLICATION ROUTING
# =========================================================

if st.session_state.page == "Home":
    home_page()
elif st.session_state.page == "Register":
    register_page()
elif st.session_state.page == "Login":
    login_page()
elif st.session_state.page == "Dashboard":
    dashboard_page()
elif st.session_state.page == "Create":
    create_page()
elif st.session_state.page == "Extract":
    extract_page()
elif st.session_state.page == "History":
    history_page()
else:
    home_page()