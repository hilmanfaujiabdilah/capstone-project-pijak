import hmac
import os
import hashlib
from datetime import datetime, timedelta

from click import style

import streamlit as st


DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"
SESSION_TOKEN_KEY = "auth_token"
SESSION_EXPIRY_KEY = "auth_expiry"
TOKEN_EXPIRY_HOURS = 24


def _secret_value(section: str, key: str, default: str | None = None) -> str | None:
    try:
        return st.secrets.get(section, {}).get(key, default)
    except Exception:
        return default


def auth_credentials() -> tuple[str, str]:
    username = os.getenv("APP_USERNAME") or _secret_value("auth", "username", DEFAULT_USERNAME)
    password = os.getenv("APP_PASSWORD") or _secret_value("auth", "password", DEFAULT_PASSWORD)
    return str(username), str(password)


def create_auth_token(username: str) -> str:
    """Create an authentication token for the session."""
    timestamp = datetime.now().isoformat()
    token_data = f"{username}:{timestamp}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    return token


def validate_auth_token(token: str, username: str) -> bool:
    """Validate if the token is still valid."""
    # Check both from session state and URL params for expiry
    expiry_time = st.session_state.get(SESSION_EXPIRY_KEY) or st.query_params.get("expiry")
    stored_token = st.session_state.get(SESSION_TOKEN_KEY) or st.query_params.get("token")
    
    if not expiry_time:
        return False
    
    try:
        expiry = datetime.fromisoformat(expiry_time)
        return datetime.now() < expiry and stored_token == token
    except Exception:
        return False


def refresh_auth() -> bool:
    """Refresh authentication without requiring login."""
    token = st.query_params.get("token")
    username = st.query_params.get("user")
    expiry = st.query_params.get("expiry")
    
    if token and username and expiry:
        # Validate token
        if validate_auth_token(token, username):
            # Initialize session state from URL params
            st.session_state.authenticated = True
            st.session_state.auth_username = username
            st.session_state[SESSION_TOKEN_KEY] = token
            st.session_state[SESSION_EXPIRY_KEY] = expiry
            
            # Extend expiry time in URL for next refresh
            new_expiry = (datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat()
            st.query_params.expiry = new_expiry
            st.session_state[SESSION_EXPIRY_KEY] = new_expiry
            
            return True
    
    return False


def get_session_token() -> str | None:
    """Get current session token."""
    return st.session_state.get(SESSION_TOKEN_KEY)


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))


def logout_button() -> None:
    if is_authenticated() and st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("auth_username", None)
        st.session_state.pop(SESSION_TOKEN_KEY, None)
        st.session_state.pop(SESSION_EXPIRY_KEY, None)
        # Clear URL parameters
        st.query_params.clear()
        st.rerun()


def require_login() -> None:
    # Try to refresh auth first if token exists in URL
    if refresh_auth():
        return
    
    if is_authenticated():
        return
    
    # hide sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
         }
         [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
         }
    """, unsafe_allow_html=True)

    expected_username, expected_password = auth_credentials()

    st.markdown(
        """
        <div class="login-hero">
            <h1>Login Inference</h1>
            <p>Masuk untuk membuka dashboard dan halaman prediksi sentimen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", placeholder="Masukkan password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

    if submitted:
        valid_username = hmac.compare_digest(username.strip(), expected_username)
        valid_password = hmac.compare_digest(password, expected_password)
        if valid_username and valid_password:
            # Create token for this session
            token = create_auth_token(username.strip())
            expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            expiry_str = expiry.isoformat()
            
            st.session_state.authenticated = True
            st.session_state.auth_username = username.strip()
            st.session_state[SESSION_TOKEN_KEY] = token
            st.session_state[SESSION_EXPIRY_KEY] = expiry_str
            
            # Add token and expiry to URL for persistence across refreshes
            st.query_params.token = token
            st.query_params.user = username.strip()
            st.query_params.expiry = expiry_str
            
            st.rerun()
        else:
            st.error("Username atau password salah.")

    if expected_username == DEFAULT_USERNAME and expected_password == DEFAULT_PASSWORD:
        st.warning("Login default aktif: username `admin`, password `admin123`")

    st.stop()
