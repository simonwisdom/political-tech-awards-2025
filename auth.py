import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from typing import Optional, Tuple

from config import (
    TOKEN_EXPIRY_HOURS,
    MAX_VERIFICATION_ATTEMPTS,
    VERIFICATION_COOLDOWN_MINUTES,
    EMAIL_FROM,
    EMAIL_SUBJECT,
    SESSION_USER_EMAIL,
    SESSION_IS_VERIFIED,
    SESSION_VERIFICATION_ATTEMPTS,
    ALLOWED_EMAILS
)
import database as db

def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)

def send_verification_email(to_email: str, token: str) -> bool:
    """Send verification email with token."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = EMAIL_SUBJECT

        verification_link = f"http://localhost:8501/?token={token}&email={to_email}"
        body = f"""
        Please verify your email to access the Political Awards allocation system.
        Click the following link to verify your email:
        
        {verification_link}
        
        This link will expire in {TOKEN_EXPIRY_HOURS} hours.
        """
        
        msg.attach(MIMEText(body, 'plain'))

        # For development, just print the verification link
        st.sidebar.info(f"Development mode: Use this link to verify:\n\n{verification_link}")
        return True

        # In production, uncomment this to actually send emails
        # with smtplib.SMTP('smtp.yourserver.com', 587) as server:
        #     server.starttls()
        #     server.login('your_email', 'your_password')
        #     server.send_message(msg)
        # return True

    except Exception as e:
        st.error(f"Failed to send verification email: {str(e)}")
        return False

def initialize_session_state():
    """Initialize session state variables."""
    if SESSION_USER_EMAIL not in st.session_state:
        st.session_state[SESSION_USER_EMAIL] = None
    if SESSION_IS_VERIFIED not in st.session_state:
        st.session_state[SESSION_IS_VERIFIED] = False
    if SESSION_VERIFICATION_ATTEMPTS not in st.session_state:
        st.session_state[SESSION_VERIFICATION_ATTEMPTS] = 0

def start_verification(email: str) -> Tuple[bool, str]:
    """Start the verification process for an email."""
    initialize_session_state()
    
    # Check if email is in allowlist
    if email not in ALLOWED_EMAILS:
        return False, "This email is not authorized to access the system."
    
    # Check verification attempts
    if (st.session_state[SESSION_VERIFICATION_ATTEMPTS] >= 
        MAX_VERIFICATION_ATTEMPTS):
        return False, "Too many verification attempts. Please try again later."

    # Create user if doesn't exist
    db.create_user(email)
    
    # Generate and store token
    token = generate_verification_token()
    db.store_verification_token(email, token, TOKEN_EXPIRY_HOURS)
    
    # Send verification email
    if not send_verification_email(email, token):
        return False, "Failed to send verification email."
    
    st.session_state[SESSION_USER_EMAIL] = email
    st.session_state[SESSION_VERIFICATION_ATTEMPTS] += 1
    
    return True, "Verification email sent. Please check your inbox."

def verify_email(email: str, token: str) -> Tuple[bool, str]:
    """Verify email with token."""
    initialize_session_state()
    
    if not email or not token:
        return False, "Invalid verification link."
    
    if db.verify_token(email, token):
        db.verify_user(email)
        st.session_state[SESSION_USER_EMAIL] = email
        st.session_state[SESSION_IS_VERIFIED] = True
        st.session_state[SESSION_VERIFICATION_ATTEMPTS] = 0
        return True, "Email verified successfully."
    
    return False, "Invalid or expired verification link."

def is_verified() -> bool:
    """Check if current user is verified."""
    initialize_session_state()
    return bool(st.session_state[SESSION_IS_VERIFIED])

def get_current_user() -> Optional[str]:
    """Get current user's email."""
    initialize_session_state()
    return st.session_state[SESSION_USER_EMAIL]

def logout():
    """Log out current user."""
    initialize_session_state()
    st.session_state[SESSION_USER_EMAIL] = None
    st.session_state[SESSION_IS_VERIFIED] = False
    st.session_state[SESSION_VERIFICATION_ATTEMPTS] = 0 