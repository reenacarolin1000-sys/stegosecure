import streamlit as st
import cv2
import numpy as np
import hashlib
import tempfile
import os
from pathlib import Path
from datetime import datetime


# =========================================================
# IMPORT PROJECT MODULES
# =========================================================

from algorithms.aes import encrypt_message, decrypt_message

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
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

initialize_database()


# =========================================================
# CREATE REQUIRED FOLDERS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =====================================================
   MAIN APPLICATION
===================================================== */

.stApp {
    background-color: #132238;
    color: #E8EDF5;
}


/* =====================================================
   REMOVE DEFAULT STREAMLIT ELEMENTS
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
    padding: 10px 18px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    transition: 0.2s ease !important;
}

.stButton > button:hover {
    background-color: #19466F !important;
    color: #FFFFFF !important;
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
}


/* =====================================================
   FILE UPLOADER
===================================================== */

[data-testid="stFileUploader"] {
    background-color: #1B2F49;
    border-radius: 10px;
    padding: 10px;
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

</style>
""", unsafe_allow_html=True)


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

def change_page(page):
    st.session_state.page = page
    st.rerun()


def hash_password(password):
    """Hash password using SHA-256."""

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def save_uploaded_file(uploaded_file):
    """Save uploaded image temporarily."""

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{timestamp}_{uploaded_file.name}"
    )

    file_path = UPLOAD_FOLDER / filename

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(file_path)


def calculate_metrics(original, stego, grayscale=False):
    """
    Calculate MSE and PSNR.
    """

    if grayscale:

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

    mse = calculate_mse(
        original,
        stego
    )

    psnr = calculate_psnr(
        original,
        stego
    )

    return mse, psnr


# =========================================================
# HEADER / NAVIGATION
# =========================================================

def show_navigation():

    col1, col2, col3, col4, col5 = st.columns(
        [3.5, 1, 1, 1, 1]
    )

    with col1:
        st.markdown(
            """
            <h2 style='margin-top:5px;'>
            🔐 StegoSecure
            </h2>
            """,
            unsafe_allow_html=True
        )

    with col2:
        if st.button(
            "Home",
            use_container_width=True
        ):
            change_page("Home")

    if st.session_state.logged_in:

        with col3:
            if st.button(
                "Dashboard",
                use_container_width=True
            ):
                change_page("Dashboard")

        with col4:
            if st.button(
                "Extract",
                use_container_width=True
            ):
                change_page("Extract")

        with col5:
            if st.button(
                "Sign Out",
                use_container_width=True
            ):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_id = None

                change_page("Home")

    else:

        with col3:
            if st.button(
                "Login",
                use_container_width=True
            ):
                change_page("Login")

        with col4:
            if st.button(
                "Register",
                use_container_width=True
            ):
                change_page("Register")

    st.divider()


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    show_navigation()

    st.markdown(
        """
        <div style="margin-top:40px;">
        <p style="
            color:#8FAFD0 !important;
            letter-spacing:4px;
            font-weight:bold;
        ">
        IMAGE STEGANOGRAPHY
        </p>

        <h1 style="font-size:52px;">
        Protect information inside ordinary images.
        </h1>

        <p style="
            font-size:20px;
            max-width:850px;
            line-height:1.8;
        ">
        StegoSecure combines AES encryption with multiple image
        steganography techniques to securely conceal confidential
        information within digital images.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("## About StegoSecure")

    st.write(
        """
        StegoSecure is an image steganography application designed
        to protect confidential information while concealing it
        inside digital images.
        """
    )

    st.write(
        """
        The secret message is first encrypted using AES-256-GCM.
        The encrypted information can then be embedded using
        Adaptive LSB, DCT, or DWT techniques.
        """
    )

    st.divider()

    st.markdown("## Techniques Used")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="card">
            <h3>Adaptive LSB</h3>
            <p>
            Uses Sobel edge detection to classify image regions.
            Smooth, moderate and strong-edge regions receive
            different embedding capacities.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="card">
            <h3>DCT</h3>
            <p>
            Embeds encrypted data by modifying middle-frequency
            Discrete Cosine Transform coefficients in image blocks.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="card">
            <h3>DWT</h3>
            <p>
            Uses Haar Discrete Wavelet Transform and embeds
            information into high-frequency coefficients.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown("## Security Pipeline")

    st.info(
        """
        Secret Message → AES-256-GCM Encryption →
        Steganography Algorithm →
        Stego Image → Extraction →
        AES Decryption
        """
    )

    if not st.session_state.logged_in:

        col1, col2 = st.columns([1, 5])

        with col1:
            if st.button(
                "Get Started",
                use_container_width=True
            ):
                change_page("Register")


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
            use_container_width=True
        )

        if submitted:

            if (
                not username
                or not email
                or not password
            ):

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                password_hash = hash_password(
                    password
                )

                success = create_user(
                    username,
                    email,
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
            use_container_width=True
        )

        if submitted:

            user = get_user(username)

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

        st.warning(
            "Please login first."
        )

        change_page("Login")

        return

    show_navigation()

    st.title("Dashboard")

    st.write(
        f"Welcome back, {st.session_state.username}."
    )

    st.write(
        "Manage your StegoSecure activity from one place."
    )

    st.divider()

    history = get_user_history(
        st.session_state.user_id
    )

    total_images = len(history)

    latest_psnr = (
        history[0][4]
        if history and history[0][4]
        else None
    )

    last_activity = (
        history[0][7]
        if history
        else None
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
            <p>Stego Images Created</p>
            <h1>{total_images}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        psnr_text = (
            f"{latest_psnr:.2f} dB"
            if latest_psnr
            else "Not available"
        )

        st.markdown(
            f"""
            <div class="metric-card">
            <p>Latest PSNR</p>
            <h1>{psnr_text}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        activity_text = (
            last_activity[:16]
            if last_activity
            else "Not available"
        )

        st.markdown(
            f"""
            <div class="metric-card">
            <p>Last Activity</p>
            <h2>{activity_text}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="card">
            <h3>Create a Stego Image</h3>
            <p>
            Upload a cover image, encrypt your secret message,
            and embed it using one of the available algorithms.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Create Stego Image",
            use_container_width=True
        ):
            change_page("Create")

    with col2:

        st.markdown(
            """
            <div class="card">
            <h3>Review History</h3>
            <p>
            View previously processed images and their
            image quality measurements.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "View History",
            use_container_width=True
        ):
            change_page("History")


# =========================================================
# CREATE STEGO IMAGE PAGE
# =========================================================

def create_page():

    if not st.session_state.logged_in:

        change_page("Login")

        return

    show_navigation()

    st.title("Create Stego Image")

    st.write(
        """
        Encrypt a secret message and embed it securely
        inside a cover image.
        """
    )

    st.divider()

    left_col, right_col = st.columns(2)

    with left_col:

        st.markdown("### Cover Image")

        uploaded_image = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_image:

            file_bytes = np.asarray(
                bytearray(
                    uploaded_image.read()
                ),
                dtype=np.uint8
            )

            preview_image = cv2.imdecode(
                file_bytes,
                cv2.IMREAD_COLOR
            )

            if preview_image is not None:

                st.image(
                    cv2.cvtColor(
                        preview_image,
                        cv2.COLOR_BGR2RGB
                    ),
                    use_container_width=True
                )

    with right_col:

        st.markdown("### Secret Message")

        secret_message = st.text_area(
            "Message",
            height=180
        )

        encryption_key = st.text_input(
            "Encryption Key",
            type="password"
        )

        algorithm = st.selectbox(
            "Steganography Algorithm",
            [
                "Adaptive LSB",
                "DCT",
                "DWT"
            ]
        )

    st.divider()

    if st.button(
        "Encrypt and Embed Message",
        use_container_width=True
    ):

        if not uploaded_image:

            st.error(
                "Please upload a cover image."
            )

            return

        if not secret_message:

            st.error(
                "Please enter a secret message."
            )

            return

        if not encryption_key:

            st.error(
                "Please enter an encryption key."
            )

            return

        try:

            with st.spinner(
                "Encrypting and embedding message..."
            ):

                # -----------------------------------------
                # Save uploaded image
                # -----------------------------------------

                uploaded_image.seek(0)

                image_path = save_uploaded_file(
                    uploaded_image
                )

                # -----------------------------------------
                # Read image
                # -----------------------------------------

                original_image = cv2.imread(
                    image_path
                )

                if original_image is None:

                    raise ValueError(
                        "Unable to read uploaded image."
                    )

                # -----------------------------------------
                # AES ENCRYPTION
                # -----------------------------------------

                encrypted_message = encrypt_message(
                    secret_message,
                    encryption_key
                )

                encrypted_data = (
                    encrypted_message.encode("utf-8")
                )

                # -----------------------------------------
                # OUTPUT PATH
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

                # =========================================
                # ADAPTIVE LSB
                # =========================================

                if algorithm == "Adaptive LSB":

                    _, _, texture_map = apply_sobel(
                        image_path
                    )

                    stego_image = embed_message(
                        original_image,
                        encrypted_data,
                        texture_map
                    )

                    cv2.imwrite(
                        str(output_path),
                        stego_image
                    )

                    mse, psnr = calculate_metrics(
                        original_image,
                        stego_image
                    )

                # =========================================
                # DCT
                # =========================================

                elif algorithm == "DCT":

                    stego_image = embed_dct(
                        original_image,
                        encrypted_data
                    )

                    cv2.imwrite(
                        str(output_path),
                        stego_image
                    )

                    mse, psnr = calculate_metrics(
                        original_image,
                        stego_image,
                        grayscale=True
                    )

                # =========================================
                # DWT
                # =========================================

                elif algorithm == "DWT":

                    gray_image = cv2.cvtColor(
                        original_image,
                        cv2.COLOR_BGR2GRAY
                    )

                    stego_image = embed_dwt(
                        gray_image,
                        encrypted_data
                    )

                    cv2.imwrite(
                        str(output_path),
                        stego_image
                    )

                    mse, psnr = calculate_metrics(
                        original_image,
                        stego_image,
                        grayscale=True
                    )

                # -----------------------------------------
                # DATABASE HISTORY
                # -----------------------------------------

                add_stego_history(
                    user_id=st.session_state.user_id,
                    original_filename=uploaded_image.name,
                    stego_filename=output_filename,
                    message_length=len(secret_message),
                    psnr=float(psnr),
                    mse=float(mse)
                )

            # =============================================
            # SUCCESS OUTPUT
            # =============================================

            st.success(
                "Message encrypted and embedded successfully!"
            )

            st.markdown("## Embedding Result")

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "### Original Image"
                )

                st.image(
                    cv2.cvtColor(
                        original_image,
                        cv2.COLOR_BGR2RGB
                    ),
                    use_container_width=True
                )

            with col2:

                st.markdown(
                    "### Stego Image"
                )

                if len(stego_image.shape) == 2:

                    st.image(
                        stego_image,
                        use_container_width=True
                    )

                else:

                    st.image(
                        cv2.cvtColor(
                            stego_image,
                            cv2.COLOR_BGR2RGB
                        ),
                        use_container_width=True
                    )

            st.divider()

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "Algorithm",
                    algorithm
                )

            with m2:
                st.metric(
                    "MSE",
                    f"{mse:.6f}"
                )

            with m3:
                st.metric(
                    "PSNR",
                    f"{psnr:.2f} dB"
                )

            st.divider()

            with open(
                output_path,
                "rb"
            ) as file:

                st.download_button(
                    label="Download Stego Image",
                    data=file,
                    file_name=output_filename,
                    mime="image/png",
                    use_container_width=True
                )

        except Exception as error:

            st.error(
                f"Processing failed: {str(error)}"
            )


# =========================================================
# EXTRACTION PAGE
# =========================================================

def extract_page():

    if not st.session_state.logged_in:

        change_page("Login")

        return

    show_navigation()

    st.title("Extract Secret Message")

    st.write(
        """
        Upload a stego image and extract the encrypted
        hidden message.
        """
    )

    st.divider()

    uploaded_stego = st.file_uploader(
        "Upload Stego Image",
        type=["png", "jpg", "jpeg"],
        key="extract_upload"
    )

    encryption_key = st.text_input(
        "Decryption Key",
        type="password"
    )

    algorithm = st.selectbox(
        "Algorithm Used for Embedding",
        [
            "Adaptive LSB",
            "DCT",
            "DWT"
        ],
        key="extract_algorithm"
    )

    if uploaded_stego:

        uploaded_stego.seek(0)

        temp_path = save_uploaded_file(
            uploaded_stego
        )

        preview = cv2.imread(
            temp_path
        )

        if preview is not None:

            st.image(
                cv2.cvtColor(
                    preview,
                    cv2.COLOR_BGR2RGB
                ),
                width=500
            )

    st.divider()

    if st.button(
        "Extract and Decrypt Message",
        use_container_width=True
    ):

        if not uploaded_stego:

            st.error(
                "Please upload a stego image."
            )

            return

        if not encryption_key:

            st.error(
                "Please enter the decryption key."
            )

            return

        try:

            with st.spinner(
                "Extracting hidden message..."
            ):

                stego_path = temp_path

                # =========================================
                # ADAPTIVE LSB EXTRACTION
                # =========================================

                if algorithm == "Adaptive LSB":

                    stego_image = cv2.imread(
                        stego_path
                    )

                    _, _, texture_map = apply_sobel(
                        stego_path
                    )

                    extracted_data = extract_message(
                        stego_image,
                        texture_map
                    )

                # =========================================
                # DCT EXTRACTION
                # =========================================

                elif algorithm == "DCT":

                    stego_image = cv2.imread(
                        stego_path,
                        cv2.IMREAD_GRAYSCALE
                    )

                    extracted_data = extract_dct(
                        stego_image
                    )

                # =========================================
                # DWT EXTRACTION
                # =========================================

                elif algorithm == "DWT":

                    stego_image = cv2.imread(
                        stego_path,
                        cv2.IMREAD_GRAYSCALE
                    )

                    extracted_data = extract_dwt(
                        stego_image
                    )

                # -----------------------------------------
                # Convert extracted bytes
                # -----------------------------------------

                encrypted_message = (
                    extracted_data.decode("utf-8")
                )

                # -----------------------------------------
                # AES DECRYPTION
                # -----------------------------------------

                original_message = decrypt_message(
                    encrypted_message,
                    encryption_key
                )

            st.success(
                "Message extracted and decrypted successfully!"
            )

            st.markdown("## Extracted Secret Message")

            st.text_area(
                "Recovered Message",
                value=original_message,
                height=180,
                disabled=True
            )

            st.info(
                f"Extraction Algorithm: {algorithm}"
            )

        except Exception as error:

            st.error(
                "Unable to extract/decrypt the message."
            )

            st.warning(
                f"Details: {str(error)}"
            )


# =========================================================
# HISTORY PAGE
# =========================================================

def history_page():

    if not st.session_state.logged_in:

        change_page("Login")

        return

    show_navigation()

    st.title("Stego Image History")

    st.write(
        "Previously generated stego images and quality metrics."
    )

    st.divider()

    history = get_user_history(
        st.session_state.user_id
    )

    if not history:

        st.info(
            "No stego images have been created yet."
        )

        return

    for item in history:

        (
            history_id,
            original_filename,
            stego_filename,
            message_length,
            psnr,
            ssim,
            mse,
            created_at
        ) = item

        with st.expander(
            f"📷 {stego_filename}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Original Image:** {original_filename}"
                )

                st.write(
                    f"**Message Length:** "
                    f"{message_length} characters"
                )

                st.write(
                    f"**Created:** {created_at}"
                )

            with col2:

                psnr_value = (
                    f"{psnr:.2f} dB"
                    if psnr
                    else "N/A"
                )

                mse_value = (
                    f"{mse:.6f}"
                    if mse is not None
                    else "N/A"
                )

                st.write(
                    f"**PSNR:** {psnr_value}"
                )

                st.write(
                    f"**MSE:** {mse_value}"
                )

                st.write(
                    f"**SSIM:** "
                    f"{ssim if ssim else 'Not calculated'}"
                )

            output_path = (
                OUTPUT_FOLDER /
                stego_filename
            )

            if output_path.exists():

                with open(
                    output_path,
                    "rb"
                ) as file:

                    st.download_button(
                        "Download Image",
                        data=file,
                        file_name=stego_filename,
                        mime="image/png",
                        key=f"download_{history_id}"
                    )


# =========================================================
# ROUTING
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