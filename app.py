import streamlit as st
import textwrap

from werkzeug.security import generate_password_hash, check_password_hash

from database.database import (
    initialize_database,
    create_user,
    get_user,
    add_stego_history,
    get_user_history
)

from algorithms.aes import encrypt_message, ciphertext_to_binary


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)


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
# COLOR PALETTE
# ============================================================

BACKGROUND = "#0B1628"
SURFACE = "#12243A"
SURFACE_LIGHT = "#18314D"

PRIMARY = "#3B9EFF"
PRIMARY_HOVER = "#61B3FF"
PRIMARY_LIGHT = "#DCEEFF"

TEXT = "#F4F8FC"
TEXT_SECONDARY = "#B9C8D8"
TEXT_MUTED = "#8192A5"

BORDER = "#263D56"


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
# HTML HELPER
# ============================================================

def render_html(content):
    st.html(textwrap.dedent(content))


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {BACKGROUND};
        color: {TEXT};
    }}

    .main .block-container {{
        max-width: 1200px;
        padding-top: 30px;
        padding-bottom: 70px;
    }}

    body {{
        font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }}

    [data-testid="stToolbar"] {{
        visibility: hidden;
        height: 0;
    }}

    [data-testid="stDecoration"] {{
        display: none;
    }}

    [data-testid="stStatusWidget"] {{
        display: none;
    }}

    header {{
        background: transparent !important;
    }}

    /* --------------------------------------------------------
       NAVIGATION
       -------------------------------------------------------- */

    .top-nav {{
        padding: 18px 0;
        border-bottom: 1px solid {BORDER};
        margin-bottom: 45px;
    }}

    .logo {{
        color: {TEXT};
        font-size: 27px;
        font-weight: 700;
        letter-spacing: -0.6px;
    }}

    .logo-mark {{
        display: inline-flex;
        width: 34px;
        height: 34px;
        align-items: center;
        justify-content: center;
        background: {PRIMARY};
        color: white;
        border-radius: 8px;
        margin-right: 10px;
        font-size: 17px;
        font-weight: 700;
    }}

    .logo-description {{
        color: {TEXT_MUTED};
        font-size: 14px;
        margin-top: 4px;
        margin-left: 45px;
    }}

    /* --------------------------------------------------------
       HERO
       -------------------------------------------------------- */

    .hero {{
        text-align: center;
        padding: 25px 0 45px 0;
    }}

    .hero-label {{
        display: inline-block;
        color: {PRIMARY};
        background-color: rgba(59, 158, 255, 0.10);
        border: 1px solid rgba(59, 158, 255, 0.30);
        border-radius: 20px;
        padding: 8px 17px;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 24px;
    }}

    .hero-title {{
        color: {TEXT};
        font-size: 52px;
        line-height: 1.15;
        font-weight: 750;
        letter-spacing: -1.5px;
        max-width: 850px;
        margin: 0 auto;
    }}

    .hero-title span {{
        color: {PRIMARY};
    }}

    .hero-description {{
        color: {TEXT_SECONDARY};
        font-size: 19px;
        line-height: 1.7;
        max-width: 720px;
        margin: 24px auto 30px auto;
    }}

    /* --------------------------------------------------------
       BUTTONS
       -------------------------------------------------------- */

    .stButton > button {{
        background-color: {PRIMARY};
        color: white;
        border: 1px solid {PRIMARY};
        border-radius: 7px;
        min-height: 46px;
        font-size: 16px;
        font-weight: 600;
        padding: 8px 18px;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        background-color: {PRIMARY_HOVER};
        border-color: {PRIMARY_HOVER};
        color: white;
    }}

    /* --------------------------------------------------------
       HEADINGS
       -------------------------------------------------------- */

    .section-heading {{
        color: {TEXT};
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-top: 40px;
        margin-bottom: 24px;
    }}

    /* --------------------------------------------------------
       CARDS
       -------------------------------------------------------- */

    .intro-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 30px;
        min-height: 230px;
    }}

    .intro-card h3 {{
        color: {TEXT};
        font-size: 23px;
        font-weight: 650;
        margin-bottom: 15px;
    }}

    .intro-card p {{
        color: {TEXT_SECONDARY};
        font-size: 17px;
        line-height: 1.8;
        margin: 0;
    }}

    .feature-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 11px;
        padding: 28px;
        min-height: 190px;
    }}

    .feature-number {{
        color: {PRIMARY};
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 18px;
    }}

    .feature-title {{
        color: {TEXT};
        font-size: 21px;
        font-weight: 650;
        margin-bottom: 12px;
    }}

    .feature-description {{
        color: {TEXT_SECONDARY};
        font-size: 16px;
        line-height: 1.75;
    }}

    .step-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 12px;
    }}

    .step-number {{
        color: {PRIMARY};
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }}

    .step-title {{
        color: {TEXT};
        font-size: 19px;
        font-weight: 650;
        margin-bottom: 6px;
    }}

    .step-description {{
        color: {TEXT_SECONDARY};
        font-size: 16px;
        line-height: 1.65;
    }}

    /* --------------------------------------------------------
       AUTHENTICATION
       -------------------------------------------------------- */

    .auth-header {{
        text-align: center;
        margin: 40px auto 35px auto;
    }}

    .auth-title {{
        color: {TEXT};
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 10px;
    }}

    .auth-description {{
        color: {TEXT_SECONDARY};
        font-size: 17px;
    }}

    /* --------------------------------------------------------
       INPUTS
       -------------------------------------------------------- */

    .stTextInput label,
    .stTextArea label {{
        color: {TEXT};
        font-size: 16px;
        font-weight: 600;
    }}

    .stTextInput input,
    .stTextArea textarea {{
        background-color: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 7px;
        font-size: 16px;
        padding: 10px 12px;
    }}

    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {PRIMARY};
        box-shadow: 0 0 0 1px {PRIMARY};
    }}

    /* --------------------------------------------------------
       FILE UPLOADER
       -------------------------------------------------------- */

    [data-testid="stFileUploader"] {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 8px;
    }}

    [data-testid="stFileUploader"] label {{
        color: {TEXT};
        font-size: 16px;
    }}

    /* --------------------------------------------------------
       DASHBOARD
       -------------------------------------------------------- */

    .dashboard-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 11px;
        padding: 30px;
        margin-bottom: 16px;
    }}

    .dashboard-title {{
        color: {TEXT};
        font-size: 22px;
        font-weight: 650;
    }}

    .dashboard-text {{
        color: {TEXT_SECONDARY};
        font-size: 16px;
        line-height: 1.7;
    }}

    /* --------------------------------------------------------
       DIVIDER
       -------------------------------------------------------- */

    .custom-divider {{
        height: 1px;
        background-color: {BORDER};
        margin: 45px 0;
    }}

    /* --------------------------------------------------------
       FOOTER
       -------------------------------------------------------- */

    .footer {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 14px;
        padding: 50px 0 10px 0;
    }}

    .stMarkdown p {{
        color: {TEXT_SECONDARY};
        font-size: 17px;
        line-height: 1.75;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TOP NAVIGATION
# ============================================================

nav_left, nav_home, nav_login, nav_register = st.columns(
    [6.4, 1, 1, 1]
)

with nav_left:

    render_html(
        """
        <div class="top-nav">

            <div class="logo">
                <span class="logo-mark">S</span>
                StegoSecure
            </div>

            <div class="logo-description">
                Secure image-based message hiding
            </div>

        </div>
        """
    )


with nav_home:

    if st.button(
        "Home",
        key="nav_home",
        use_container_width=True
    ):
        st.session_state.page = "Home"
        st.rerun()


with nav_login:

    if st.button(
        "Login",
        key="nav_login",
        use_container_width=True
    ):
        st.session_state.page = "Login"
        st.rerun()


with nav_register:

    if st.button(
        "Register",
        key="nav_register",
        use_container_width=True
    ):
        st.session_state.page = "Register"
        st.rerun()


# ============================================================
# HOME PAGE
# ============================================================

def home_page():

    render_html(
        """
        <div class="hero">

            <div class="hero-label">
                Image Steganography
            </div>

            <div class="hero-title">
                Secure your message.
                <span>Hide it in plain sight.</span>
            </div>

            <div class="hero-description">
                StegoSecure helps protect a private message,
                encrypt it, and hide it inside an image while
                maintaining the visual appearance of the image.
            </div>

        </div>
        """
    )

    hero_left, hero_button, hero_right = st.columns([2, 1, 2])

    with hero_button:

        if st.button(
            "Get Started",
            key="hero_get_started",
            use_container_width=True
        ):
            st.session_state.page = "Register"
            st.rerun()

    render_html(
        """
        <div class="custom-divider"></div>

        <div class="section-heading">
            What is StegoSecure?
        </div>
        """
    )

    intro_left, intro_right = st.columns([1.3, 1], gap="large")

    with intro_left:

        render_html(
            """
            <div class="intro-card">

                <h3>
                    A simple way to protect hidden information
                </h3>

                <p>
                    StegoSecure is a web application designed to
                    hide confidential messages inside digital images.
                    Before the message is embedded, it is encrypted
                    to provide an additional layer of protection.
                </p>

                <br>

                <p>
                    The application also considers different regions
                    of the image when deciding how the information
                    should be embedded.
                </p>

            </div>
            """
        )

    with intro_right:

        render_html(
            """
            <div class="intro-card">

                <h3>
                    Designed for secure sharing
                </h3>

                <p>
                    The resulting image should appear visually
                    similar to the original image while carrying
                    the protected information.
                </p>

                <br>

                <p>
                    StegoSecure combines encryption and image
                    steganography in one application.
                </p>

            </div>
            """
        )

    render_html(
        """
        <div class="section-heading">
            Features
        </div>
        """
    )

    feature1, feature2, feature3 = st.columns(3, gap="medium")

    with feature1:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-number">
                    01
                </div>

                <div class="feature-title">
                    Message Encryption
                </div>

                <div class="feature-description">
                    The secret message is encrypted before it is
                    embedded into the image.
                </div>

            </div>
            """
        )

    with feature2:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-number">
                    02
                </div>

                <div class="feature-title">
                    Adaptive Embedding
                </div>

                <div class="feature-description">
                    Image regions are considered when deciding how
                    strongly the hidden information should be embedded.
                </div>

            </div>
            """
        )

    with feature3:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-number">
                    03
                </div>

                <div class="feature-title">
                    Image Quality
                </div>

                <div class="feature-description">
                    Image quality can be evaluated after embedding
                    to check whether the visual appearance is maintained.
                </div>

            </div>
            """
        )

    render_html(
        """
        <div class="section-heading">
            How to use
        </div>
        """
    )

    steps = [
        (
            "01",
            "Create an account",
            "Register for a StegoSecure account."
        ),
        (
            "02",
            "Choose an image",
            "Select the image that you want to use as the cover image."
        ),
        (
            "03",
            "Enter your message",
            "Type the confidential message that you want to hide."
        ),
        (
            "04",
            "Protect your message",
            "Provide the encryption key that will be used to protect the message."
        ),
        (
            "05",
            "Create the stego image",
            "The protected message will be processed and embedded into the image."
        ),
        (
            "06",
            "View your history",
            "Previously generated stego images can be viewed from the dashboard."
        )
    ]

    for number, title, description in steps:

        render_html(
            f"""
            <div class="step-card">

                <div class="step-number">
                    {number}
                </div>

                <div class="step-title">
                    {title}
                </div>

                <div class="step-description">
                    {description}
                </div>

            </div>
            """
        )

    render_html(
        """
        <div class="footer">
            StegoSecure
        </div>
        """
    )


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    left, center, right = st.columns([1, 2, 1])

    with center:

        render_html(
            """
            <div class="auth-header">

                <div class="auth-title">
                    Welcome back
                </div>

                <div class="auth-description">
                    Sign in to continue to StegoSecure.
                </div>

            </div>
            """
        )

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            key="login_submit",
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

                    if verify_password(password, password_hash):

                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.username = stored_username
                        st.session_state.page = "Dashboard"

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

        st.write("")

        if st.button(
            "Back to Home",
            key="login_back",
            use_container_width=True
        ):

            st.session_state.page = "Home"
            st.rerun()


# ============================================================
# REGISTER PAGE
# ============================================================

def register_page():

    left, center, right = st.columns([1, 2, 1])

    with center:

        render_html(
            """
            <div class="auth-header">

                <div class="auth-title">
                    Create your account
                </div>

                <div class="auth-description">
                    Register to start using StegoSecure.
                </div>

            </div>
            """
        )

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

        if st.button(
            "Create Account",
            key="register_submit",
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

                password_hash = hash_password(password)

                created = create_user(
                    username,
                    email,
                    password_hash
                )

                if created:

                    st.success(
                        "Account created successfully. You can now login."
                    )

                else:

                    st.error(
                        "Username or email already exists."
                    )

        st.write("")

        if st.button(
            "Back to Home",
            key="register_back",
            use_container_width=True
        ):

            st.session_state.page = "Home"
            st.rerun()


# ============================================================
# DASHBOARD PAGE
# ============================================================

def dashboard_page():

    username = st.session_state.username

    render_html(
        f"""
        <div class="section-heading">
            Welcome, {username}
        </div>
        """
    )

    st.write(
        "Manage your image steganography activities from here."
    )

    st.write("")

    dashboard1, dashboard2 = st.columns(2, gap="large")

    with dashboard1:

        render_html(
            """
            <div class="dashboard-card">

                <div class="dashboard-title">
                    Create Stego Image
                </div>

                <br>

                <div class="dashboard-text">
                    Upload an image and hide a protected message
                    inside it using the StegoSecure methodology.
                </div>

            </div>
            """
        )

        if st.button(
            "Create Stego Image",
            key="dashboard_create",
            use_container_width=True
        ):

            st.session_state.page = "Create"
            st.rerun()

    with dashboard2:

        render_html(
            """
            <div class="dashboard-card">

                <div class="dashboard-title">
                    Stego Image History
                </div>

                <br>

                <div class="dashboard-text">
                    View the stego images and processing details
                    associated with your account.
                </div>

            </div>
            """
        )

        if st.button(
            "View History",
            key="dashboard_history",
            use_container_width=True
        ):

            st.session_state.page = "History"
            st.rerun()

    st.write("")

    if st.button(
        "Logout",
        key="dashboard_logout"
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

    render_html(
        """
        <div class="section-heading">
            Create Stego Image
        </div>
        """
    )

    st.write(
        "Choose an image and enter the message you want to hide."
    )

    st.write("")

    image = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"],
        key="cover_image"
    )

    if image is not None:

        st.image(
            image,
            caption="Selected Cover Image",
            use_container_width=True
        )

    message = st.text_area(
        "Secret Message",
        height=180,
        placeholder="Enter the message you want to hide...",
        key="secret_message"
    )

    encryption_key = st.text_input(
        "Encryption Key",
        type="password",
        placeholder="Enter your encryption key",
        key="encryption_key"
    )

    st.write("")

    if st.button(
        "Create Stego Image",
        key="create_stego",
        use_container_width=True
    ):

        if image is None:

            st.warning(
                "Please choose an image."
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

                st.write(
                    "Encrypted message prepared for embedding."
                )

                st.write(
                    f"Encrypted data size: {len(binary_data)} bits"
                )

            except ValueError as error:

                st.error(
                    str(error)
                )

    st.write("")

    if st.button(
        "Back to Dashboard",
        key="create_back_dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Dashboard"
        st.rerun()


# ============================================================
# HISTORY PAGE
# ============================================================

def history_page():

    render_html(
        """
        <div class="section-heading">
            Stego Image History
        </div>
        """
    )

    st.write(
        "Previously created stego images associated with your account."
    )

    st.write("")

    user_id = st.session_state.user_id

    history = get_user_history(user_id)

    if not history:

        render_html(
            """
            <div class="dashboard-card">

                <div class="dashboard-title">
                    No images yet
                </div>

                <br>

                <div class="dashboard-text">
                    Once you create a stego image, its processing
                    details will be stored in your account history.
                </div>

            </div>
            """
        )

    else:

        for record in history:

            (
                record_id,
                original_filename,
                stego_filename,
                message_length,
                psnr,
                ssim,
                mse,
                created_at
            ) = record

            render_html(
                f"""
                <div class="dashboard-card">

                    <div class="dashboard-title">
                        {stego_filename or "Stego Image"}
                    </div>

                    <br>

                    <div class="dashboard-text">

                        Original image:
                        {original_filename}

                        <br><br>

                        Message length:
                        {message_length if message_length is not None else "Not available"}

                        <br><br>

                        PSNR:
                        {psnr if psnr is not None else "Not available"}

                        <br><br>

                        SSIM:
                        {ssim if ssim is not None else "Not available"}

                        <br><br>

                        MSE:
                        {mse if mse is not None else "Not available"}

                        <br><br>

                        Created:
                        {created_at}

                    </div>

                </div>
                """
            )

    st.write("")

    if st.button(
        "Back to Dashboard",
        key="history_back_dashboard",
        use_container_width=True
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