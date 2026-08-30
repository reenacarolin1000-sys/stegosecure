import streamlit as st
import cv2
import numpy as np
import hashlib
import os
import re
import base64
from pathlib import Path
from datetime import datetime


# =========================================================
# PROJECT IMPORTS
# =========================================================

from algorithms.aes import (
    encrypt_message,
    decrypt_message
)

from algorithms.adaptive_lsb import (
    embed_message,
    extract_message
)

from algorithms.sobel import (
    apply_sobel
)

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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

LOGO_PATH = BASE_DIR / "stegosecure_logo.png"


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =====================================================
   MAIN BACKGROUND
===================================================== */

.stApp {
    background-color: #0E1B2A;
    color: white;
}


/* =====================================================
   HIDE STREAMLIT DEFAULT ELEMENTS
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


/* =====================================================
   HEADINGS
===================================================== */

h1 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

h2 {
    color: #FFFFFF !important;
}

h3 {
    color: #DCEBFF !important;
}

p {
    color: #C7D4E5 !important;
}


/* =====================================================
   BUTTONS - BLUE
===================================================== */

.stButton > button {
    background-color: #1677FF !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
}

.stButton > button:hover {
    background-color: #0E5FCC !important;
    color: white !important;
    border: none !important;
}


/* =====================================================
   FORM BUTTONS
===================================================== */

.stFormSubmitButton > button {
    background-color: #1677FF !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stFormSubmitButton > button:hover {
    background-color: #0E5FCC !important;
}


/* =====================================================
   INPUT FIELDS
===================================================== */

.stTextInput input {
    background-color: #172A40 !important;
    color: white !important;
    border: 1px solid #35597C !important;
    border-radius: 8px !important;
}

.stTextArea textarea {
    background-color: #172A40 !important;
    color: white !important;
    border: 1px solid #35597C !important;
    border-radius: 8px !important;
}

label {
    color: #DCEBFF !important;
}


/* =====================================================
   SELECT BOX
===================================================== */

div[data-baseweb="select"] > div {
    background-color: #172A40 !important;
    color: white !important;
    border-color: #35597C !important;
}


/* =====================================================
   CARDS
===================================================== */

.card {
    background-color: #13263A;
    border: 1px solid #294866;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 15px;
}

.metric-card {
    background-color: #152C44;
    border: 1px solid #2B5275;
    border-radius: 12px;
    padding: 18px;
}


/* =====================================================
   FILE UPLOADER
===================================================== */

[data-testid="stFileUploader"] {
    background-color: #13263A;
    border-radius: 10px;
    padding: 10px;
}


/* =====================================================
   SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background-color: #101F31;
}


/* =====================================================
   DIVIDER
===================================================== */

hr {
    border-color: #294866 !important;
}


/* =====================================================
   METRICS
===================================================== */

[data-testid="stMetric"] {
    background-color: #152C44;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #294866;
}

</style>
""", unsafe_allow_html=True)


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
    Create a safe ASCII filename.

    This prevents OpenCV errors caused by emoji,
    Unicode characters and special symbols.
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

    return name + extension.lower()


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


def calculate_metrics(original, stego):
    """Calculate MSE and PSNR."""

    if len(original.shape) != len(stego.shape):
        if len(original.shape) == 3:
            original = cv2.cvtColor(
                original,
                cv2.COLOR_BGR2GRAY
            )

        if len(stego.shape) == 3:
            stego = cv2.cvtColor(
                stego,
                cv2.COLOR_BGR2GRAY
            )

    if original.shape != stego.shape:
        stego = cv2.resize(
            stego,
            (original.shape[1], original.shape[0])
        )

    mse = calculate_mse(
        original,
        stego
    )

    psnr = calculate_psnr(
        original,
        stego
    )

    return mse, psnr


def calculate_capacity_adaptive(texture_map):
    """Calculate approximate capacity of Adaptive LSB."""

    smooth = np.sum(texture_map == 0)
    moderate = np.sum(texture_map == 1)
    strong = np.sum(texture_map == 2)

    total_bits = (
        smooth * 1 +
        moderate * 2 +
        strong * 3
    )

    usable_bits = max(0, total_bits - 32)

    return usable_bits // 8


def calculate_capacity_dct(image):
    """
    Approximate DCT capacity.

    One bit per 8x8 block.
    """

    height, width = image.shape[:2]

    blocks = (
        (height // 8) *
        (width // 8)
    )

    usable_bits = max(0, blocks - 32)

    return usable_bits // 8


def calculate_capacity_dwt(image):
    """
    DWT HH sub-band capacity.
    """

    height, width = image.shape[:2]

    coefficients = (
        (height // 2) *
        (width // 2)
    )

    usable_bits = max(
        0,
        coefficients - 32
    )

    return usable_bits // 8


def get_image_bytes(image):
    """Convert OpenCV image into PNG bytes."""

    success, buffer = cv2.imencode(
        ".png",
        image
    )

    if not success:
        raise ValueError(
            "Unable to encode image."
        )

    return buffer.tobytes()


def show_logo():
    """Display project logo."""

    if LOGO_PATH.exists():

        col1, col2 = st.columns(
            [1, 6]
        )

        with col1:
            st.image(
                str(LOGO_PATH),
                width=70
            )

        with col2:
            st.markdown(
                """
                <div style="
                    padding-top:8px;
                    font-size:30px;
                    font-weight:700;
                    color:white;
                ">
                    StegoSecure
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            """
            <h2 style="color:white;">
                StegoSecure
            </h2>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# NAVIGATION
# =========================================================

def show_navigation():

    with st.sidebar:

        if LOGO_PATH.exists():

            col1, col2 = st.columns(
                [1, 3]
            )

            with col1:
                st.image(
                    str(LOGO_PATH),
                    width=50
                )

            with col2:
                st.markdown(
                    """
                    <h3 style="
                        margin-top:10px;
                        color:white;
                    ">
                    StegoSecure
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.title("StegoSecure")

        st.divider()

        if st.button(
            "Home",
            width="stretch"
        ):
            change_page("Home")

        if st.session_state.logged_in:

            if st.button(
                "Dashboard",
                width="stretch"
            ):
                change_page("Dashboard")

            if st.button(
                "Create Stego Image",
                width="stretch"
            ):
                change_page("Create")

            if st.button(
                "Extract Message",
                width="stretch"
            ):
                change_page("Extract")

            if st.button(
                "History",
                width="stretch"
            ):
                change_page("History")

            st.divider()

            st.write(
                f"Logged in as: **{st.session_state.username}**"
            )

            if st.button(
                "Logout",
                width="stretch"
            ):

                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None

                change_page("Home")

        else:

            if st.button(
                "Login",
                width="stretch"
            ):
                change_page("Login")

            if st.button(
                "Create Account",
                width="stretch"
            ):
                change_page("Register")


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    show_navigation()

    st.markdown("<br>", unsafe_allow_html=True)

    show_logo()

    st.markdown("<br>", unsafe_allow_html=True)

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

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Create Account",
                width="stretch"
            ):
                change_page("Register")

        with col2:

            if st.button(
                "Login",
                width="stretch"
            ):
                change_page("Login")

    else:

        if st.button(
            "Go to Dashboard",
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
        "Create an account to use StegoSecure."
    )

    st.divider()

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
                not username.strip()
                or not email.strip()
                or not password
            ):

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 4:

                st.error(
                    "Password must contain at least 4 characters."
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

                    if stored_hash == entered_hash:

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

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Create Secure Stego Image",
            width="stretch"
        ):

            change_page("Create")

    with col2:

        if st.button(
            "Extract Hidden Message",
            width="stretch"
        ):

            change_page("Extract")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Implemented Methodology")

    st.markdown(
        """
        <div class="card">
        <b>Step 1:</b> User enters confidential message.<br><br>
        <b>Step 2:</b> Message is encrypted using AES-256-GCM.<br><br>
        <b>Step 3:</b> User selects Adaptive LSB, DCT or DWT.<br><br>
        <b>Step 4:</b> Encrypted data is embedded into the image.<br><br>
        <b>Step 5:</b> Image quality is evaluated using MSE and PSNR.<br><br>
        <b>Step 6:</b> During extraction, hidden data is recovered and decrypted.
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

    uploaded_file = st.file_uploader(
        "Upload Cover Image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    secret_message = st.text_area(
        "Secret Message",
        placeholder="Enter your confidential message here..."
    )

    encryption_password = st.text_input(
        "Encryption Password",
        type="password"
    )

    algorithm = st.selectbox(
        "Select Steganography Algorithm",
        [
            "Adaptive LSB + Sobel",
            "DCT",
            "DWT"
        ]
    )

    if uploaded_file is not None:

        image_path = save_uploaded_file(
            uploaded_file
        )

        original_color = cv2.imread(
            image_path,
            cv2.IMREAD_COLOR
        )

        if original_color is None:

            st.error(
                "Unable to read the uploaded image."
            )

            return

        st.subheader("Cover Image")

        st.image(
            original_color,
            channels="BGR",
            width="stretch"
        )

        st.divider()

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

                gray = cv2.cvtColor(
                    original_color,
                    cv2.COLOR_BGR2GRAY
                )

                capacity = calculate_capacity_dct(
                    gray
                )

            else:

                gray = cv2.cvtColor(
                    original_color,
                    cv2.COLOR_BGR2GRAY
                )

                capacity = calculate_capacity_dwt(
                    gray
                )

            st.info(
                f"Approximate embedding capacity: "
                f"{capacity} bytes"
            )

        except Exception:

            capacity = None

    if st.button(
        "Encrypt and Create Stego Image",
        width="stretch"
    ):

        if uploaded_file is None:

            st.error(
                "Please upload an image."
            )

            return

        if not secret_message.strip():

            st.error(
                "Please enter a secret message."
            )

            return

        if not encryption_password:

            st.error(
                "Please enter an encryption password."
            )

            return

        try:

            with st.spinner(
                "Encrypting and embedding secret message..."
            ):

                # -----------------------------------------
                # ENCRYPT MESSAGE
                # -----------------------------------------

                encrypted_message = encrypt_message(
                    secret_message,
                    encryption_password
                )

                encrypted_data = (
                    encrypted_message.encode(
                        "utf-8"
                    )
                )

                # -----------------------------------------
                # READ IMAGE
                # -----------------------------------------

                image_path = save_uploaded_file(
                    uploaded_file
                )

                original_color = cv2.imread(
                    image_path,
                    cv2.IMREAD_COLOR
                )

                if original_color is None:

                    raise ValueError(
                        "Unable to read uploaded image."
                    )

                # -----------------------------------------
                # ADAPTIVE LSB
                # -----------------------------------------

                if algorithm == "Adaptive LSB + Sobel":

                    _, _, texture_map = apply_sobel(
                        image_path
                    )

                    stego_image = embed_message(
                        original_color,
                        encrypted_data,
                        texture_map
                    )

                    original_for_metrics = (
                        original_color
                    )

                # -----------------------------------------
                # DCT
                # -----------------------------------------

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

                # -----------------------------------------
                # DWT
                # -----------------------------------------

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

                # -----------------------------------------
                # CALCULATE METRICS
                # -----------------------------------------

                mse, psnr = calculate_metrics(
                    original_for_metrics,
                    stego_image
                )

                # -----------------------------------------
                # SAVE OUTPUT
                # -----------------------------------------

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                output_filename = (
                    f"stego_{timestamp}.png"
                )

                output_path = (
                    OUTPUT_FOLDER /
                    output_filename
                )

                cv2.imwrite(
                    str(output_path),
                    stego_image
                )

                # -----------------------------------------
                # SAVE HISTORY
                # -----------------------------------------

                add_stego_history(
                    st.session_state.user_id,
                    uploaded_file.name,
                    output_filename,
                    len(secret_message),
                    psnr=psnr,
                    ssim=None,
                    mse=mse
                )

                # -----------------------------------------
                # SUCCESS
                # -----------------------------------------

                st.success(
                    "Stego image created successfully!"
                )

                st.subheader(
                    "Stego Image"
                )

                if len(stego_image.shape) == 2:

                    st.image(
                        stego_image,
                        channels="GRAY",
                        width="stretch"
                    )

                else:

                    st.image(
                        stego_image,
                        channels="BGR",
                        width="stretch"
                    )

                st.subheader(
                    "Image Quality Metrics"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "MSE",
                        f"{mse:.6f}"
                    )

                with col2:

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
                f"Error: {str(error)}"
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

    uploaded_file = st.file_uploader(
        "Upload Stego Image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ],
        key="extract_uploader"
    )

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

    if uploaded_file is not None:

        image_path = save_uploaded_file(
            uploaded_file
        )

        image = cv2.imread(
            image_path,
            cv2.IMREAD_COLOR
        )

        if image is not None:

            st.subheader(
                "Uploaded Stego Image"
            )

            st.image(
                image,
                channels="BGR",
                width="stretch"
            )

    if st.button(
        "Extract and Decrypt Message",
        width="stretch"
    ):

        if uploaded_file is None:

            st.error(
                "Please upload a stego image."
            )

            return

        if not encryption_password:

            st.error(
                "Please enter the encryption password."
            )

            return

        try:

            with st.spinner(
                "Extracting hidden information..."
            ):

                image_path = save_uploaded_file(
                    uploaded_file
                )

                # -----------------------------------------
                # ADAPTIVE LSB EXTRACTION
                # -----------------------------------------

                if algorithm == "Adaptive LSB + Sobel":

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

                # -----------------------------------------
                # DCT EXTRACTION
                # -----------------------------------------

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

                # -----------------------------------------
                # DWT EXTRACTION
                # -----------------------------------------

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

                # -----------------------------------------
                # CONVERT TO TEXT
                # -----------------------------------------

                encrypted_message = (
                    extracted_data.decode(
                        "utf-8"
                    )
                )

                # -----------------------------------------
                # AES DECRYPTION
                # -----------------------------------------

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
                    height=180
                )

                st.info(
                    f"Extraction Algorithm: {algorithm}"
                )

        except UnicodeDecodeError:

            st.error(
                """
                Unable to decode the extracted data.

                Make sure you selected the correct
                steganography algorithm.
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

        st.markdown(
            f"""
            <div class="card">
            <h3>Stego Image #{record_id}</h3>
            <p><b>Original Image:</b> {original_filename}</p>
            <p><b>Stego File:</b> {stego_filename}</p>
            <p><b>Message Length:</b> {message_length} characters</p>
            <p><b>PSNR:</b> {psnr if psnr is not None else "N/A"}</p>
            <p><b>MSE:</b> {mse if mse is not None else "N/A"}</p>
            <p><b>Created:</b> {created_at}</p>
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