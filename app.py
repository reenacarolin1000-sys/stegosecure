import os

import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash

from database.database import (
    initialize_database,
    create_user,
    get_user,
    get_user_history
)

from algorithms.aes import (
    encrypt_message,
    ciphertext_to_binary
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StegoSecure",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "stegosecure_logo.png"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background-color: #081B33;
        color: #F5F8FC;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 25px;
        padding-bottom: 60px;
    }

    body {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Arial,
            sans-serif;
    }


    /* ========================================================
       HIDE STREAMLIT CONTROLS
       ======================================================== */

    [data-testid="stDeployButton"] {
        display: none !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background-color: #081B33 !important;
    }


    /* ========================================================
       HEADER
       ======================================================== */

    .header-divider {
        height: 1px;

        background-color: #294969;

        margin-top: 8px;

        margin-bottom: 45px;
    }


    /* ========================================================
       BRAND NAME
       ======================================================== */

    .brand-name {
        color: #F5F8FC;

        font-size: 25px;

        font-weight: 700;

        line-height: 58px;

        white-space: nowrap;

        letter-spacing: -0.4px;
    }


    /* ========================================================
       NAVIGATION BUTTONS
       ======================================================== */

    .nav-button button {
        background-color: #12345A !important;

        color: #EAF4FF !important;

        border: 1px solid #31577D !important;

        border-radius: 7px !important;

        min-height: 45px !important;

        font-size: 15px !important;

        font-weight: 600 !important;

        box-shadow: none !important;

        outline: none !important;
    }

    .nav-button button:hover {
        background-color: #19466F !important;

        color: #FFFFFF !important;

        border-color: #4DA3FF !important;

        box-shadow: none !important;
    }

    .nav-button button:focus,
    .nav-button button:focus-visible,
    .nav-button button:active {
        background-color: #19466F !important;

        color: #FFFFFF !important;

        border: 1px solid #4DA3FF !important;

        box-shadow: none !important;

        outline: none !important;
    }


    /* ========================================================
       GENERAL BUTTONS
       ======================================================== */

    .stButton button {
        background-color: #12345A;

        color: #F5F8FC;

        border: 1px solid #3A5D82;

        border-radius: 7px;

        min-height: 46px;

        font-size: 15px;

        font-weight: 600;

        box-shadow: none;
    }

    .stButton button:hover {
        background-color: #19466F;

        color: #FFFFFF;

        border-color: #4DA3FF;

        box-shadow: none;
    }


    /* ========================================================
       PRIMARY BUTTON
       ======================================================== */

    .primary-button button {
        background-color: #3B91E8 !important;

        color: #FFFFFF !important;

        border: 1px solid #3B91E8 !important;

        border-radius: 7px !important;

        min-height: 48px !important;

        font-size: 16px !important;

        font-weight: 650 !important;
    }

    .primary-button button:hover {
        background-color: #55A5F5 !important;

        border-color: #55A5F5 !important;

        color: #071A30 !important;
    }


    /* ========================================================
       HEADINGS
       ======================================================== */

    h1 {
        color: #F5F8FC !important;

        font-size: 48px !important;

        font-weight: 750 !important;

        line-height: 1.2 !important;

        letter-spacing: -1px !important;
    }

    h2 {
        color: #F5F8FC !important;

        font-size: 31px !important;

        font-weight: 700 !important;
    }

    h3 {
        color: #F5F8FC !important;

        font-size: 21px !important;

        font-weight: 650 !important;
    }

    p {
        color: #C5D4E7;

        font-size: 17px;

        line-height: 1.7;
    }


    /* ========================================================
       HOME PAGE
       ======================================================== */

    .eyebrow {
        color: #55A5F5;

        font-size: 14px;

        font-weight: 700;

        letter-spacing: 1.4px;

        margin-top: 50px;

        margin-bottom: 14px;
    }

    .home-description {
        max-width: 820px;

        color: #C5D4E7;

        font-size: 19px;

        line-height: 1.75;

        margin-bottom: 35px;
    }

    .section-divider {
        height: 1px;

        background-color: #294969;

        margin: 45px 0;
    }


    /* ========================================================
       CARDS
       ======================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #102A4C;

        border: 1px solid #294969;

        border-radius: 10px;
    }


    /* ========================================================
       FEATURE LABEL
       ======================================================== */

    .feature-label {
        color: #55A5F5;

        font-size: 13px;

        font-weight: 700;

        letter-spacing: 1px;

        margin-bottom: 10px;
    }


    /* ========================================================
       AUTHENTICATION
       ======================================================== */

    .auth-description {
        color: #AFC2D8;

        font-size: 17px;

        text-align: center;

        margin-bottom: 30px;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput label,
    .stTextArea label,
    .stFileUploader label {
        color: #E9F1FA !important;

        font-size: 15px !important;

        font-weight: 600 !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        background-color: #102A4C !important;

        color: #F5F8FC !important;

        border: 1px solid #355579 !important;

        border-radius: 7px !important;

        font-size: 16px !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #4DA3FF !important;

        box-shadow: 0 0 0 1px #4DA3FF !important;
    }


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploaderDropzone"] {
        background-color: #102A4C;

        border: 1px dashed #466887;

        border-radius: 8px;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background-color: #102A4C;

        border: 1px solid #294969;

        border-radius: 9px;

        padding: 20px;
    }

    [data-testid="stMetricLabel"] {
        color: #AFC2D8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F5F8FC !important;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        color: #8299B3;

        text-align: center;

        font-size: 14px;

        margin-top: 60px;

        padding-top: 25px;

        border-top: 1px solid #294969;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)


# ============================================================
# HEADER
# ============================================================

logo_column, brand_column, empty_column, home_column, login_column, register_column = st.columns(
    [0.75, 2.0, 4.0, 1.2, 1.2, 1.2],
    gap="small"
)


# ============================================================
# LOGO
# ============================================================

with logo_column:

    if os.path.exists(LOGO_PATH):

        st.image(
            LOGO_PATH,
            width=58
        )

    else:

        st.write("S")


# ============================================================
# BRAND NAME
# ============================================================

with brand_column:

    st.markdown(
        """
        <div class="brand-name">
            StegoSecure
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HOME BUTTON
# ============================================================

with home_column:

    st.markdown(
        '<div class="nav-button">',
        unsafe_allow_html=True
    )

    if st.button(
        "Home",
        key="header_home_button",
        use_container_width=True
    ):

        st.session_state.page = "Home"

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# LOGIN BUTTON
# ============================================================

with login_column:

    st.markdown(
        '<div class="nav-button">',
        unsafe_allow_html=True
    )

    if st.button(
        "Login",
        key="header_login_button",
        use_container_width=True
    ):

        st.session_state.page = "Login"

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# REGISTER BUTTON
# ============================================================

with register_column:

    st.markdown(
        '<div class="nav-button">',
        unsafe_allow_html=True
    )

    if st.button(
        "Register",
        key="header_register_button",
        use_container_width=True
    ):

        st.session_state.page = "Register"

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


st.markdown(
    '<div class="header-divider"></div>',
    unsafe_allow_html=True
)


# ============================================================
# HOME PAGE
# ============================================================

def home_page():

    st.markdown(
        '<div class="eyebrow">IMAGE STEGANOGRAPHY</div>',
        unsafe_allow_html=True
    )

    st.title(
        "Protect information inside ordinary images."
    )

    st.markdown(
        """
        <div class="home-description">
        StegoSecure combines message encryption with image
        steganography to provide a secure way to conceal
        confidential information within digital images.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.header("About StegoSecure")

    st.write(
        """
        StegoSecure is a secure image steganography application
        designed to protect confidential information while
        concealing it within digital images.
        """
    )

    st.write(
        """
        The system first protects the secret message through
        encryption and then prepares the encrypted information
        for image-based embedding.
        """
    )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.header("Key capabilities")

    feature1, feature2, feature3 = st.columns(
        3,
        gap="medium"
    )


    # ========================================================
    # FEATURE 1
    # ========================================================

    with feature1:

        with st.container(border=True):

            st.markdown(
                '<div class="feature-label">SECURITY</div>',
                unsafe_allow_html=True
            )

            st.subheader("AES Encryption")

            st.write(
                """
                The secret message is encrypted before it is
                processed for the embedding stage.
                """
            )


    # ========================================================
    # FEATURE 2
    # ========================================================

    with feature2:

        with st.container(border=True):

            st.markdown(
                '<div class="feature-label">STEGANOGRAPHY</div>',
                unsafe_allow_html=True
            )

            st.subheader("Adaptive Embedding")

            st.write(
                """
                Image characteristics can be considered when
                selecting suitable regions for hiding information.
                """
            )


    # ========================================================
    # FEATURE 3
    # ========================================================

    with feature3:

        with st.container(border=True):

            st.markdown(
                '<div class="feature-label">EVALUATION</div>',
                unsafe_allow_html=True
            )

            st.subheader("Quality Evaluation")

            st.write(
                """
                PSNR, SSIM and MSE can be used to evaluate
                changes between the original and stego images.
                """
            )


    st.markdown(
        """
        <div class="footer">
        StegoSecure · Secure image-based message hiding
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.title("Sign in")

    st.markdown(
        """
        <div class="auth-description">
        Sign in to access your StegoSecure workspace.
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1.2, 2, 1.2]
    )

    with center:

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        st.write("")

        st.markdown(
            '<div class="primary-button">',
            unsafe_allow_html=True
        )

        if st.button(
            "Sign in",
            key="login_submit_button",
            use_container_width=True
        ):

            if not username or not password:

                st.warning(
                    "Please enter your username and password."
                )

            else:

                user = get_user(username)

                if user is None:

                    st.error(
                        "Invalid username or password."
                    )

                else:

                    user_id = user[0]

                    stored_username = user[1]

                    password_hash = user[3]

                    if verify_password(
                        password,
                        password_hash
                    ):

                        st.session_state.logged_in = True

                        st.session_state.user_id = user_id

                        st.session_state.username = stored_username

                        st.session_state.page = "Dashboard"

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "Back to Home",
            key="login_back_button",
            use_container_width=True
        ):

            st.session_state.page = "Home"

            st.rerun()


# ============================================================
# REGISTER PAGE
# ============================================================

def register_page():

    st.title("Create an account")

    st.markdown(
        """
        <div class="auth-description">
        Create your StegoSecure account.
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1.2, 2, 1.2]
    )

    with center:

        username = st.text_input(
            "Username",
            key="register_username"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password"
        )

        st.write("")

        st.markdown(
            '<div class="primary-button">',
            unsafe_allow_html=True
        )

        if st.button(
            "Create account",
            key="register_submit_button",
            use_container_width=True
        ):

            username = username.strip()

            email = email.strip()

            if not username or not email or not password:

                st.warning(
                    "Please complete all fields."
                )

            elif "@" not in email:

                st.warning(
                    "Please enter a valid email address."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            else:

                password_hash = hash_password(
                    password
                )

                created = create_user(
                    username,
                    email,
                    password_hash
                )

                if created:

                    st.success(
                        "Account created successfully."
                    )

                    st.info(
                        "You can now sign in."
                    )

                else:

                    st.error(
                        "Username or email already exists."
                    )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "Back to Home",
            key="register_back_button",
            use_container_width=True
        ):

            st.session_state.page = "Home"

            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard_page():

    username = st.session_state.username

    user_id = st.session_state.user_id

    history = get_user_history(user_id)

    total_images = len(history)

    latest_psnr = "Not available"

    latest_date = "Not available"


    if history:

        if history[0][4] is not None:

            latest_psnr = (
                f"{history[0][4]:.2f} dB"
            )

        latest_date = str(
            history[0][7]
        )[:10]


    st.title("Dashboard")

    st.write(
        f"Welcome back, {username}."
    )

    st.write(
        "Manage your StegoSecure activity from one place."
    )

    st.write("")


    metric1, metric2, metric3 = st.columns(
        3
    )


    with metric1:

        st.metric(
            "Stego Images Created",
            total_images
        )


    with metric2:

        st.metric(
            "Latest PSNR",
            latest_psnr
        )


    with metric3:

        st.metric(
            "Last Activity",
            latest_date
        )


    st.write("")
    st.write("")


    action1, action2 = st.columns(
        2,
        gap="large"
    )


    with action1:

        with st.container(border=True):

            st.subheader(
                "Create a stego image"
            )

            st.write(
                """
                Upload a cover image and protect a secret
                message before the embedding stage.
                """
            )

            if st.button(
                "Create Stego Image",
                key="dashboard_create_button",
                use_container_width=True
            ):

                st.session_state.page = "Create"

                st.rerun()


    with action2:

        with st.container(border=True):

            st.subheader(
                "Review history"
            )

            st.write(
                """
                View previously processed images and their
                quality measurements.
                """
            )

            if st.button(
                "View History",
                key="dashboard_history_button",
                use_container_width=True
            ):

                st.session_state.page = "History"

                st.rerun()


    st.write("")

    if st.button(
        "Sign out",
        key="dashboard_signout_button"
    ):

        st.session_state.logged_in = False

        st.session_state.user_id = None

        st.session_state.username = None

        st.session_state.page = "Home"

        st.rerun()


# ============================================================
# CREATE STEGO IMAGE PAGE
# ============================================================

def create_page():

    st.title("Create Stego Image")

    st.write(
        """
        Encrypt a secret message and prepare it for secure
        embedding into a cover image.
        """
    )

    st.write("")


    image_col, message_col = st.columns(
        2,
        gap="large"
    )


    with image_col:

        with st.container(border=True):

            st.subheader("Cover Image")

            uploaded_image = st.file_uploader(
                "Choose an image",
                type=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="cover_image_uploader"
            )

            if uploaded_image is not None:

                st.image(
                    uploaded_image,
                    caption="Selected cover image",
                    use_container_width=True
                )


    with message_col:

        with st.container(border=True):

            st.subheader("Secret Message")

            message = st.text_area(
                "Message",
                height=180,
                placeholder="Enter the message you want to hide...",
                key="secret_message_input"
            )

            encryption_key = st.text_input(
                "Encryption Key",
                type="password",
                placeholder="Enter your encryption key",
                key="encryption_key_input"
            )


    st.write("")


    st.markdown(
        '<div class="primary-button">',
        unsafe_allow_html=True
    )


    if st.button(
        "Encrypt Message",
        key="encrypt_message_button",
        use_container_width=True
    ):

        if uploaded_image is None:

            st.warning(
                "Please choose a cover image."
            )

        elif not message.strip():

            st.warning(
                "Please enter a secret message."
            )

        elif not encryption_key:

            st.warning(
                "Please enter an encryption key."
            )

        else:

            try:

                encrypted_message = encrypt_message(
                    message,
                    encryption_key
                )

                binary_data = ciphertext_to_binary(
                    encrypted_message
                )

                st.success(
                    "Message encrypted successfully."
                )

                with st.container(border=True):

                    st.subheader(
                        "Encryption Result"
                    )

                    st.write(
                        "The encrypted message is ready "
                        "for the embedding stage."
                    )

                    st.write(
                        f"Encrypted data size: "
                        f"{len(binary_data)} bits"
                    )

            except Exception as error:

                st.error(
                    f"Encryption error: {error}"
                )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    st.write("")


    if st.button(
        "Back to Dashboard",
        key="create_back_dashboard_button"
    ):

        st.session_state.page = "Dashboard"

        st.rerun()


# ============================================================
# HISTORY PAGE
# ============================================================

def history_page():

    st.title("Stego Image History")

    st.write(
        """
        Review the stego images associated with your account
        and their quality measurements.
        """
    )


    user_id = st.session_state.user_id

    history = get_user_history(user_id)


    if not history:

        with st.container(border=True):

            st.subheader(
                "No activity yet"
            )

            st.write(
                """
                Your processed stego images will appear here
                after the embedding process is completed.
                """
            )


    else:

        for record in history:

            original_filename = record[1]

            stego_filename = record[2]

            message_length = record[3]

            psnr = record[4]

            ssim = record[5]

            mse = record[6]

            created_at = record[7]


            with st.container(border=True):

                st.subheader(
                    stego_filename
                    if stego_filename
                    else "Stego Image"
                )


                information_col, metrics_col = st.columns(
                    2
                )


                with information_col:

                    st.write(
                        f"Original image: {original_filename}"
                    )

                    st.write(
                        f"Message length: {message_length}"
                    )

                    st.write(
                        f"Created: {created_at}"
                    )


                with metrics_col:

                    if psnr is not None:

                        st.write(
                            f"PSNR: {psnr:.2f} dB"
                        )

                    else:

                        st.write(
                            "PSNR: Not available"
                        )


                    if ssim is not None:

                        st.write(
                            f"SSIM: {ssim:.4f}"
                        )

                    else:

                        st.write(
                            "SSIM: Not available"
                        )


                    if mse is not None:

                        st.write(
                            f"MSE: {mse:.4f}"
                        )

                    else:

                        st.write(
                            "MSE: Not available"
                        )


    st.write("")


    if st.button(
        "Back to Dashboard",
        key="history_back_dashboard_button"
    ):

        st.session_state.page = "Dashboard"

        st.rerun()


# ============================================================
# PAGE ROUTER
# ============================================================

if st.session_state.page == "Home":

    home_page()


elif st.session_state.page == "Login":

    login_page()


elif st.session_state.page == "Register":

    register_page()


elif st.session_state.page == "Dashboard":

    if st.session_state.logged_in:

        dashboard_page()

    else:

        st.session_state.page = "Login"

        st.rerun()


elif st.session_state.page == "Create":

    if st.session_state.logged_in:

        create_page()

    else:

        st.session_state.page = "Login"

        st.rerun()


elif st.session_state.page == "History":

    if st.session_state.logged_in:

        history_page()

    else:

        st.session_state.page = "Login"

        st.rerun()