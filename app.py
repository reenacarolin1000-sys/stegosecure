import streamlit as st
import cv2
import numpy as np
import hashlib
import os
import re
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
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_FOLDER = BASE_DIR / "assets"
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

LOGO_PATH = ASSETS_FOLDER / "stegosecure_logo.png"

ASSETS_FOLDER.mkdir(exist_ok=True)
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN APPLICATION
    ===================================================== */

    .stApp {
        background-color: #132238;
        color: #E8EDF5;
    }


    /* =====================================================
       MAIN CONTENT WIDTH
    ===================================================== */

    .main .block-container {
        max-width: 1450px;
        padding-top: 20px;
        padding-bottom: 60px;
        padding-left: 5%;
        padding-right: 5%;
    }


    /* =====================================================
       REMOVE STREAMLIT DEFAULT ELEMENTS
    ===================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        display: none;
    }


    /* =====================================================
       TEXT
    ===================================================== */

    h1 {
        color: #F2F5F9 !important;
        font-weight: 700 !important;
    }

    h2 {
        color: #E8EDF5 !important;
    }

    h3 {
        color: #E8EDF5 !important;
    }

    p {
        color: #BFC9D8 !important;
    }

    label {
        color: #C9D2DF !important;
    }


    /* =====================================================
       BUTTONS
    ===================================================== */

    .stButton > button {
        background-color: #243B5A !important;
        color: #FFFFFF !important;
        border: 1px solid #4A6A8E !important;
        border-radius: 8px !important;
        padding: 9px 16px !important;
        min-height: 42px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #19466F !important;
        color: #FFFFFF !important;
        border-color: #4DA3FF !important;
    }


    /* =====================================================
       FORM BUTTONS
    ===================================================== */

    div[data-testid="stFormSubmitButton"] > button {
        background-color: #243B5A !important;
        color: white !important;
        border: 1px solid #4A6A8E !important;
        border-radius: 8px !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #19466F !important;
        border-color: #4DA3FF !important;
    }


    /* =====================================================
       INPUTS
    ===================================================== */

    .stTextInput input {
        background-color: #203653 !important;
        color: white !important;
        border: 1px solid #5D7797 !important;
        border-radius: 8px !important;
    }

    .stTextArea textarea {
        background-color: #203653 !important;
        color: white !important;
        border: 1px solid #5D7797 !important;
        border-radius: 8px !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #203653 !important;
        color: white !important;
        border-radius: 8px !important;
    }


    /* =====================================================
       FILE UPLOADER
    ===================================================== */

    [data-testid="stFileUploader"] {
        background-color: #1B2F49;
        border-radius: 10px;
        padding: 10px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #1B2F49;
        border: 1px dashed #4A6A8E;
        border-radius: 10px;
    }


    /* =====================================================
       CARDS
    ===================================================== */

    .card {
        background-color: #182B43;
        border: 1px solid #2A415D;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 15px;
    }

    .metric-card {
        background-color: #203653;
        border: 1px solid #355574;
        border-radius: 12px;
        padding: 20px;
        min-height: 120px;
    }


    /* =====================================================
       METRICS
    ===================================================== */

    [data-testid="stMetric"] {
        background-color: #182B43;
        border: 1px solid #355574;
        padding: 18px;
        border-radius: 10px;
    }


    /* =====================================================
       HORIZONTAL LINE
    ===================================================== */

    hr {
        border-color: #35516E !important;
    }


    /* =====================================================
       ALERTS
    ===================================================== */

    .stSuccess {
        background-color: #173B3C !important;
    }

    .stInfo {
        background-color: #1B3654 !important;
    }


    /* =====================================================
       HEADER
    ===================================================== */

    .header-brand {
        font-size: 30px;
        font-weight: 700;
        color: #F2F5F9;
        white-space: nowrap;
    }

    .header-divider {
        height: 1px;
        background-color: #35516E;
        margin-top: 15px;
        margin-bottom: 35px;
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

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def change_page(page):
    """Change application page."""

    st.session_state.page = page
    st.rerun()


def hash_password(password):
    """Hash password using SHA-256."""

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def sanitize_filename(filename):
    """
    Convert filename into a safe ASCII filename.

    This prevents OpenCV errors caused by:
    - Emoji
    - Unicode characters
    - Special symbols
    """

    name, extension = os.path.splitext(filename)

    name = name.encode(
        "ascii",
        "ignore"
    ).decode()

    name = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        name
    )

    if not name:
        name = "uploaded_image"

    extension = extension.lower()

    if extension not in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:
        extension = ".png"

    return name + extension


def save_uploaded_file(uploaded_file):
    """Save uploaded file with a safe filename."""

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    safe_name = sanitize_filename(
        uploaded_file.name
    )

    filename = (
        f"{timestamp}_{safe_name}"
    )

    file_path = UPLOAD_FOLDER / filename

    with open(file_path, "wb") as file:
        file.write(
            uploaded_file.getbuffer()
        )

    return str(file_path)


def read_uploaded_image(uploaded_file):
    """
    Read uploaded image directly from bytes.

    This avoids filename and Unicode path problems.
    """

    file_bytes = np.asarray(
        bytearray(uploaded_file.getvalue()),
        dtype=np.uint8
    )

    image = cv2.imdecode(
        file_bytes,
        cv2.IMREAD_COLOR
    )

    return image


def get_image_bytes(image):
    """Convert OpenCV image into PNG bytes."""

    success, encoded_image = cv2.imencode(
        ".png",
        image
    )

    if not success:
        raise ValueError(
            "Unable to encode image."
        )

    return encoded_image.tobytes()


def calculate_metrics(original, stego):
    """Calculate MSE and PSNR."""

    if original is None or stego is None:
        raise ValueError(
            "Invalid images for metric calculation."
        )

    original_for_metric = original.copy()
    stego_for_metric = stego.copy()

    if len(original_for_metric.shape) != len(
        stego_for_metric.shape
    ):

        if len(original_for_metric.shape) == 3:
            original_for_metric = cv2.cvtColor(
                original_for_metric,
                cv2.COLOR_BGR2GRAY
            )

        if len(stego_for_metric.shape) == 3:
            stego_for_metric = cv2.cvtColor(
                stego_for_metric,
                cv2.COLOR_BGR2GRAY
            )

    if (
        original_for_metric.shape
        != stego_for_metric.shape
    ):

        stego_for_metric = cv2.resize(
            stego_for_metric,
            (
                original_for_metric.shape[1],
                original_for_metric.shape[0]
            )
        )

    mse = calculate_mse(
        original_for_metric,
        stego_for_metric
    )

    psnr = calculate_psnr(
        original_for_metric,
        stego_for_metric
    )

    return mse, psnr


def calculate_capacity_adaptive(texture_map):
    """
    Calculate approximate Adaptive LSB capacity.

    Smooth regions   = 1 bit
    Moderate regions = 2 bits
    Strong edges     = 3 bits
    """

    smooth = np.sum(texture_map == 0)
    moderate = np.sum(texture_map == 1)
    strong = np.sum(texture_map == 2)

    total_bits = (
        smooth * 1
        + moderate * 2
        + strong * 3
    )

    usable_bits = max(
        0,
        total_bits - 32
    )

    return usable_bits // 8


def calculate_capacity_dct(image):
    """
    Approximate DCT capacity.

    Assumes one bit per 8x8 block.
    """

    height, width = image.shape[:2]

    blocks = (
        (height // 8)
        * (width // 8)
    )

    usable_bits = max(
        0,
        blocks - 32
    )

    return usable_bits // 8


def calculate_capacity_dwt(image):
    """
    Approximate DWT capacity.

    Uses a conservative estimate.
    """

    height, width = image.shape[:2]

    coefficients = (
        (height // 2)
        * (width // 2)
    )

    usable_bits = max(
        0,
        coefficients - 32
    )

    return usable_bits // 8


# =========================================================
# NAVIGATION HEADER
# =========================================================

def show_navigation():
    """
    Display horizontal application header.

    Left:
    - Logo
    - StegoSecure branding

    Right:
    - Navigation buttons
    """

    header_left, spacer, header_right = st.columns(
        [3.5, 1.5, 6],
        vertical_alignment="center"
    )

    # =====================================================
    # LEFT SIDE: LOGO + BRAND
    # =====================================================

    with header_left:

        logo_col, brand_col = st.columns(
            [1, 4],
            vertical_alignment="center"
        )

        with logo_col:

            if LOGO_PATH.exists():

                st.image(
                    str(LOGO_PATH),
                    width=58
                )

            else:

                st.markdown(
                    """
                    <div style="
                        width:55px;
                        height:55px;
                        border-radius:10px;
                        background:#243B5A;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:white;
                        font-size:25px;
                        font-weight:700;
                    ">
                    S
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with brand_col:

            st.markdown(
                """
                <div class="header-brand">
                    StegoSecure
                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================
    # RIGHT SIDE: NAVIGATION
    # =====================================================

    with header_right:

        if st.session_state.logged_in:

            (
                nav_home,
                nav_dashboard,
                nav_create,
                nav_extract,
                nav_history,
                nav_logout
            ) = st.columns(6)

            with nav_home:

                if st.button(
                    "Home",
                    key="header_home",
                    width="stretch"
                ):
                    change_page("Home")

            with nav_dashboard:

                if st.button(
                    "Dashboard",
                    key="header_dashboard",
                    width="stretch"
                ):
                    change_page("Dashboard")

            with nav_create:

                if st.button(
                    "Create",
                    key="header_create",
                    width="stretch"
                ):
                    change_page("Create")

            with nav_extract:

                if st.button(
                    "Extract",
                    key="header_extract",
                    width="stretch"
                ):
                    change_page("Extract")

            with nav_history:

                if st.button(
                    "History",
                    key="header_history",
                    width="stretch"
                ):
                    change_page("History")

            with nav_logout:

                if st.button(
                    "Sign Out",
                    key="header_logout",
                    width="stretch"
                ):

                    st.session_state.logged_in = False
                    st.session_state.user_id = None
                    st.session_state.username = None

                    change_page("Home")

        else:

            (
                nav_home,
                nav_login,
                nav_register
            ) = st.columns(3)

            with nav_home:

                if st.button(
                    "Home",
                    key="header_home",
                    width="stretch"
                ):
                    change_page("Home")

            with nav_login:

                if st.button(
                    "Login",
                    key="header_login",
                    width="stretch"
                ):
                    change_page("Login")

            with nav_register:

                if st.button(
                    "Register",
                    key="header_register",
                    width="stretch"
                ):
                    change_page("Register")

    st.markdown(
        """
        <div class="header-divider"></div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    show_navigation()

    st.title(
        "Secure Image Steganography System"
    )

    st.write(
        """
        StegoSecure is an image steganography application
        designed to securely hide confidential information
        inside digital images.
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="card">
            <h3>Adaptive LSB</h3>
            <p>
            Uses Sobel edge detection and adaptive
            least significant bit embedding.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="card">
            <h3>DCT Steganography</h3>
            <p>
            Embeds secret information in frequency-domain
            DCT coefficients.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="card">
            <h3>DWT Steganography</h3>
            <p>
            Uses wavelet decomposition and embeds
            information in high-frequency coefficients.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Security Pipeline")

    st.write(
        """
        Secret Message → AES-256 Encryption →
        Steganographic Embedding → Stego Image
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.logged_in:

        button_col1, button_col2 = st.columns(2)

        with button_col1:

            if st.button(
                "Create Account",
                key="home_register",
                width="stretch"
            ):
                change_page("Register")

        with button_col2:

            if st.button(
                "Login",
                key="home_login",
                width="stretch"
            ):
                change_page("Login")

    else:

        if st.button(
            "Go to Dashboard",
            key="home_dashboard",
            width="stretch"
        ):
            change_page("Dashboard")


# =========================================================
# REGISTER PAGE
# =========================================================

def register_page():

    show_navigation()

    st.title("Create Account")

    st.write(
        "Create an account to start using StegoSecure."
    )

    st.divider()

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        with st.form("register_form"):

            username = st.text_input(
                "Username"
            )

            email = st.text_input(
                "Email"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create Account",
                width="stretch"
            )

            if submitted:

                if (
                    not username
                    or not email
                    or not password
                    or not confirm_password
                ):

                    st.error(
                        "Please fill in all fields."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif len(password) < 6:

                    st.error(
                        "Password must contain at least 6 characters."
                    )

                else:

                    password_hash = hash_password(
                        password
                    )

                    success = create_user(
                        username.strip(),
                        email.strip(),
                        password_hash
                    )

                    if success:

                        st.success(
                            "Account created successfully!"
                        )

                        st.info(
                            "Please login to continue."
                        )

                    else:

                        st.error(
                            "Username or email already exists."
                        )


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    show_navigation()

    st.title("Login")

    st.write(
        "Login to access your StegoSecure dashboard."
    )

    st.divider()

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        with st.form("login_form"):

            username = st.text_input(
                "Username"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login",
                width="stretch"
            )

            if submitted:

                if not username or not password:

                    st.error(
                        "Please enter username and password."
                    )

                else:

                    user = get_user(
                        username.strip()
                    )

                    if user:

                        stored_hash = user[3]

                        entered_hash = hash_password(
                            password
                        )

                        if (
                            stored_hash
                            == entered_hash
                        ):

                            st.session_state.logged_in = True
                            st.session_state.user_id = user[0]
                            st.session_state.username = user[1]

                            st.success(
                                "Login successful!"
                            )

                            change_page(
                                "Dashboard"
                            )

                        else:

                            st.error(
                                "Incorrect password."
                            )

                    else:

                        st.error(
                            "User not found."
                        )


# =========================================================
# DASHBOARD PAGE
# =========================================================

def dashboard_page():

    if not st.session_state.logged_in:

        change_page("Login")
        return

    show_navigation()

    st.title(
        f"Welcome, {st.session_state.username}!"
    )

    st.write(
        "Manage your secure steganography operations."
    )

    st.divider()

    history = get_user_history(
        st.session_state.user_id
    )

    total_images = len(history)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Stego Images Created",
            total_images
        )

    with col2:

        st.metric(
            "Available Algorithms",
            "3"
        )

    with col3:

        st.metric(
            "Encryption",
            "AES-256"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Quick Actions")

    action1, action2 = st.columns(2)

    with action1:

        st.markdown(
            """
            <div class="card">
            <h3>Create a Stego Image</h3>
            <p>
            Upload a cover image, encrypt your secret
            message and embed it securely.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Create Secure Stego Image",
            key="dashboard_create",
            width="stretch"
        ):
            change_page("Create")

    with action2:

        st.markdown(
            """
            <div class="card">
            <h3>Extract Hidden Message</h3>
            <p>
            Upload a stego image and recover the
            encrypted hidden message.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Extract Hidden Message",
            key="dashboard_extract",
            width="stretch"
        ):
            change_page("Extract")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Implemented Methodology")

    st.markdown(
        """
        <div class="card">

        <b>Step 1:</b>
        User enters confidential message.

        <br><br>

        <b>Step 2:</b>
        Message is encrypted using AES-256-GCM.

        <br><br>

        <b>Step 3:</b>
        User selects Adaptive LSB, DCT or DWT.

        <br><br>

        <b>Step 4:</b>
        Encrypted data is embedded into the image.

        <br><br>

        <b>Step 5:</b>
        Image quality is evaluated using MSE and PSNR.

        <br><br>

        <b>Step 6:</b>
        During extraction, hidden data is recovered
        and decrypted.

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# CREATE STEGO IMAGE PAGE
# =========================================================

def create_page():

    if not st.session_state.logged_in:

        change_page("Login")
        return

    show_navigation()

    st.title("Create Secure Stego Image")

    st.write(
        """
        Upload a cover image, enter a secret message,
        encrypt it using AES and embed it using the
        selected steganography algorithm.
        """
    )

    st.divider()

    left_col, right_col = st.columns(2)

    original_color = None
    image_path = None

    # =====================================================
    # LEFT SIDE - IMAGE
    # =====================================================

    with left_col:

        st.subheader("Cover Image")

        uploaded_file = st.file_uploader(
            "Choose an image",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="create_uploader"
        )

        if uploaded_file is not None:

            original_color = read_uploaded_image(
                uploaded_file
            )

            if original_color is not None:

                image_path = save_uploaded_file(
                    uploaded_file
                )

                st.image(
                    cv2.cvtColor(
                        original_color,
                        cv2.COLOR_BGR2RGB
                    ),
                    width="stretch"
                )

            else:

                st.error(
                    "Unable to read uploaded image."
                )

    # =====================================================
    # RIGHT SIDE - MESSAGE
    # =====================================================

    with right_col:

        st.subheader("Secret Message")

        secret_message = st.text_area(
            "Message",
            placeholder=(
                "Enter your confidential message here..."
            ),
            height=170,
            key="create_message"
        )

        encryption_password = st.text_input(
            "Encryption Password",
            type="password",
            key="create_password"
        )

        algorithm = st.selectbox(
            "Steganography Algorithm",
            [
                "Adaptive LSB + Sobel",
                "DCT",
                "DWT"
            ],
            key="create_algorithm"
        )

    # =====================================================
    # CAPACITY
    # =====================================================

    if (
        original_color is not None
        and image_path is not None
    ):

        try:

            if algorithm == "Adaptive LSB + Sobel":

                _, _, texture_map = apply_sobel(
                    image_path
                )

                capacity = (
                    calculate_capacity_adaptive(
                        texture_map
                    )
                )

            elif algorithm == "DCT":

                gray_image = cv2.cvtColor(
                    original_color,
                    cv2.COLOR_BGR2GRAY
                )

                capacity = calculate_capacity_dct(
                    gray_image
                )

            else:

                gray_image = cv2.cvtColor(
                    original_color,
                    cv2.COLOR_BGR2GRAY
                )

                capacity = calculate_capacity_dwt(
                    gray_image
                )

            st.info(
                f"Approximate embedding capacity: "
                f"{capacity:,} bytes"
            )

        except Exception as error:

            st.warning(
                f"Unable to calculate capacity: {error}"
            )

    st.divider()

    # =====================================================
    # EMBED BUTTON
    # =====================================================

    if st.button(
        "Encrypt and Embed Message",
        key="embed_button",
        width="stretch"
    ):

        if uploaded_file is None:

            st.error(
                "Please upload a cover image."
            )

        elif original_color is None:

            st.error(
                "Unable to process uploaded image."
            )

        elif not secret_message.strip():

            st.error(
                "Please enter a secret message."
            )

        elif not encryption_password:

            st.error(
                "Please enter an encryption password."
            )

        else:

            try:

                # =========================================
                # AES ENCRYPTION
                # =========================================

                with st.spinner(
                    "Encrypting secret message..."
                ):

                    encrypted_message = encrypt_message(
                        secret_message,
                        encryption_password
                    )

                st.success(
                    "AES-256-GCM encryption completed."
                )

                # Convert encrypted message to bytes
                if isinstance(
                    encrypted_message,
                    str
                ):

                    encrypted_data = (
                        encrypted_message.encode("utf-8")
                    )

                else:

                    encrypted_data = bytes(
                        encrypted_message
                    )

                # =========================================
                # ADAPTIVE LSB
                # =========================================

                if (
                    algorithm
                    == "Adaptive LSB + Sobel"
                ):

                    _, _, texture_map = apply_sobel(
                        image_path
                    )

                    stego_image = embed_message(
                        original_color.copy(),
                        encrypted_data,
                        texture_map
                    )

                    original_for_metrics = (
                        original_color
                    )

                # =========================================
                # DCT
                # =========================================

                elif algorithm == "DCT":

                    gray_image = cv2.cvtColor(
                        original_color,
                        cv2.COLOR_BGR2GRAY
                    )

                    stego_image = embed_dct(
                        gray_image,
                        encrypted_data
                    )

                    original_for_metrics = (
                        gray_image
                    )

                # =========================================
                # DWT
                # =========================================

                else:

                    gray_image = cv2.cvtColor(
                        original_color,
                        cv2.COLOR_BGR2GRAY
                    )

                    stego_image = embed_dwt(
                        gray_image,
                        encrypted_data
                    )

                    original_for_metrics = (
                        gray_image
                    )

                # =========================================
                # CALCULATE METRICS
                # =========================================

                mse, psnr = calculate_metrics(
                    original_for_metrics,
                    stego_image
                )

                # =========================================
                # SAVE OUTPUT
                # =========================================

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                output_filename = (
                    f"stego_{timestamp}.png"
                )

                output_path = (
                    OUTPUT_FOLDER
                    / output_filename
                )

                cv2.imwrite(
                    str(output_path),
                    stego_image
                )

                # =========================================
                # SAVE HISTORY
                # =========================================

                add_stego_history(
                    st.session_state.user_id,
                    uploaded_file.name,
                    output_filename,
                    len(secret_message),
                    psnr=psnr,
                    ssim=None,
                    mse=mse
                )

                # =========================================
                # SUCCESS
                # =========================================

                st.success(
                    "Stego image created successfully!"
                )

                st.subheader(
                    "Generated Stego Image"
                )

                if len(stego_image.shape) == 2:

                    st.image(
                        stego_image,
                        channels="GRAY",
                        width="stretch"
                    )

                else:

                    st.image(
                        cv2.cvtColor(
                            stego_image,
                            cv2.COLOR_BGR2RGB
                        ),
                        width="stretch"
                    )

                st.subheader(
                    "Image Quality Metrics"
                )

                metric1, metric2 = st.columns(2)

                with metric1:

                    st.metric(
                        "MSE",
                        f"{mse:.6f}"
                    )

                with metric2:

                    if np.isinf(psnr):

                        st.metric(
                            "PSNR",
                            "Infinity"
                        )

                    else:

                        st.metric(
                            "PSNR",
                            f"{psnr:.2f} dB"
                        )

                st.download_button(
                    label="Download Stego Image",
                    data=get_image_bytes(
                        stego_image
                    ),
                    file_name=output_filename,
                    mime="image/png",
                    key="download_stego",
                    width="stretch"
                )

                st.info(
                    f"""
                    Algorithm used: {algorithm}

                    AES encryption was applied before
                    steganographic embedding.
                    """
                )

            except Exception as error:

                st.error(
                    f"Processing failed: {str(error)}"
                )


# =========================================================
# EXTRACT MESSAGE PAGE
# =========================================================

def extract_page():

    if not st.session_state.logged_in:

        change_page("Login")
        return

    show_navigation()

    st.title("Extract Hidden Message")

    st.write(
        """
        Upload a stego image and use the same algorithm
        and encryption password to recover the hidden message.
        """
    )

    st.divider()

    left_col, right_col = st.columns(2)

    image_path = None

    # =====================================================
    # LEFT - STEGO IMAGE
    # =====================================================

    with left_col:

        st.subheader("Stego Image")

        uploaded_file = st.file_uploader(
            "Upload Stego Image",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="extract_uploader"
        )

        if uploaded_file is not None:

            preview_image = read_uploaded_image(
                uploaded_file
            )

            if preview_image is not None:

                image_path = save_uploaded_file(
                    uploaded_file
                )

                st.image(
                    cv2.cvtColor(
                        preview_image,
                        cv2.COLOR_BGR2RGB
                    ),
                    width="stretch"
                )

            else:

                st.error(
                    "Unable to read uploaded image."
                )

    # =====================================================
    # RIGHT - EXTRACTION SETTINGS
    # =====================================================

    with right_col:

        st.subheader("Extraction Settings")

        algorithm = st.selectbox(
            "Select Algorithm Used for Embedding",
            [
                "Adaptive LSB + Sobel",
                "DCT",
                "DWT"
            ],
            key="extract_algorithm"
        )

        encryption_password = st.text_input(
            "Encryption Password",
            type="password",
            key="extract_password"
        )

    st.divider()

    # =====================================================
    # EXTRACT BUTTON
    # =====================================================

    if st.button(
        "Extract and Decrypt Message",
        key="extract_button",
        width="stretch"
    ):

        if uploaded_file is None:

            st.error(
                "Please upload a stego image."
            )

        elif image_path is None:

            st.error(
                "Unable to process uploaded image."
            )

        elif not encryption_password:

            st.error(
                "Please enter the encryption password."
            )

        else:

            try:

                with st.spinner(
                    "Extracting hidden message..."
                ):

                    # =====================================
                    # ADAPTIVE LSB EXTRACTION
                    # =====================================

                    if (
                        algorithm
                        == "Adaptive LSB + Sobel"
                    ):

                        stego_image = cv2.imread(
                            image_path,
                            cv2.IMREAD_COLOR
                        )

                        if stego_image is None:

                            raise ValueError(
                                "Unable to read stego image."
                            )

                        _, _, texture_map = apply_sobel(
                            image_path
                        )

                        extracted_data = extract_message(
                            stego_image,
                            texture_map
                        )

                    # =====================================
                    # DCT EXTRACTION
                    # =====================================

                    elif algorithm == "DCT":

                        stego_image = cv2.imread(
                            image_path,
                            cv2.IMREAD_GRAYSCALE
                        )

                        if stego_image is None:

                            raise ValueError(
                                "Unable to read stego image."
                            )

                        extracted_data = extract_dct(
                            stego_image
                        )

                    # =====================================
                    # DWT EXTRACTION
                    # =====================================

                    else:

                        stego_image = cv2.imread(
                            image_path,
                            cv2.IMREAD_GRAYSCALE
                        )

                        if stego_image is None:

                            raise ValueError(
                                "Unable to read stego image."
                            )

                        extracted_data = extract_dwt(
                            stego_image
                        )

                # =========================================
                # CONVERT EXTRACTED DATA
                # =========================================

                if isinstance(
                    extracted_data,
                    bytes
                ):

                    encrypted_message = (
                        extracted_data.decode(
                            "utf-8"
                        )
                    )

                else:

                    encrypted_message = str(
                        extracted_data
                    )

                # =========================================
                # AES DECRYPTION
                # =========================================

                decrypted_message = decrypt_message(
                    encrypted_message,
                    encryption_password
                )

                st.success(
                    "Message extracted successfully!"
                )

                st.subheader(
                    "Recovered Secret Message"
                )

                st.text_area(
                    "Decrypted Message",
                    value=decrypted_message,
                    height=180,
                    key="recovered_message"
                )

                st.info(
                    f"Extraction Algorithm: {algorithm}"
                )

            except UnicodeDecodeError:

                st.error(
                    """
                    Unable to decode the extracted data.

                    Make sure you selected the correct
                    steganography algorithm and image.
                    """
                )

            except Exception as error:

                st.error(
                    f"Extraction failed: {str(error)}"
                )


# =========================================================
# HISTORY PAGE
# =========================================================

def history_page():

    if not st.session_state.logged_in:

        change_page("Login")
        return

    show_navigation()

    st.title("Steganography History")

    st.write(
        "View previously generated stego images."
    )

    st.divider()

    history = get_user_history(
        st.session_state.user_id
    )

    if not history:

        st.info(
            "No stego images created yet."
        )

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

        psnr_display = (
            f"{float(psnr):.2f} dB"
            if psnr is not None
            else "N/A"
        )

        mse_display = (
            f"{float(mse):.6f}"
            if mse is not None
            else "N/A"
        )

        st.markdown(
            f"""
            <div class="card">

            <h3>
                Stego Image #{record_id}
            </h3>

            <p>
                <b>Original Image:</b>
                {original_filename}
            </p>

            <p>
                <b>Stego File:</b>
                {stego_filename}
            </p>

            <p>
                <b>Message Length:</b>
                {message_length} characters
            </p>

            <p>
                <b>PSNR:</b>
                {psnr_display}
            </p>

            <p>
                <b>MSE:</b>
                {mse_display}
            </p>

            <p>
                <b>Created:</b>
                {created_at}
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# PAGE ROUTING
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