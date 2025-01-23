import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "db.sqlite3"
PROJECTS_PATH = DATA_DIR / "projects.csv"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Application settings
TOTAL_BUDGET = 5_000_000  # £5M in pounds
MAX_PROJECTS = 293

# Authentication settings
TOKEN_EXPIRY_HOURS = 24
MAX_VERIFICATION_ATTEMPTS = 5
VERIFICATION_COOLDOWN_MINUTES = 15

# Allowlist settings
ALLOWED_EMAILS = {
    "test@example.com",
    # Add more allowed emails here
}

# Email settings
EMAIL_FROM = "noreply@political-awards.org"
EMAIL_SUBJECT = "Verify your Political Awards allocation account"

# Database settings
DB_POOL_SIZE = 5
DB_TIMEOUT = 30  # seconds

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 60

# Session keys
SESSION_USER_EMAIL = "user_email"
SESSION_IS_VERIFIED = "is_verified"
SESSION_LAST_ALLOCATION = "last_allocation"
SESSION_VERIFICATION_ATTEMPTS = "verification_attempts" 