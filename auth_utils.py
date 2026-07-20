"""
CATALYST AEGIS — Authentication Utilities
Handles user accounts, verification, and session management.
"""

import json
import os
import uuid
import hashlib
import random
from datetime import datetime

USERS_FILE = "users.json"
VERIFICATION_CODES = {}

def load_users():
    """Load all registered users."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users_dict):
    """Save users to disk."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_dict, f, indent=2)

def generate_user_id():
    """Generate a unique 8-character user ID."""
    return "CA-" + uuid.uuid4().hex[:8].upper()

def generate_verification_code():
    """Generate a 6-digit verification code."""
    return str(random.randint(100000, 999999))

def hash_password(password):
    """Hash a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(full_name, email, password, country, accepted_terms, accepted_risk, accepted_liability):
    """Register a new user. Returns (success, message, user_data)."""
    users = load_users()
    
    # Check if email already exists
    if email in users:
        return False, "An account with this email already exists.", None
    
    user_id = generate_user_id()
    verification_code = generate_verification_code()
    
    user_data = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "password_hash": hash_password(password),
        "country": country,
        "accepted_terms": accepted_terms,
        "accepted_risk": accepted_risk,
        "accepted_liability": accepted_liability,
        "signup_date": datetime.now().isoformat(),
        "verified": False,
        "verification_code": verification_code,
        "kyc_tier": "tier1",
        "subscription": "paper",
        "login_method": "email",
        "social_accounts": [],
    }
    
    users[email] = user_data
    save_users(users)
    
    # Store verification code (in production, email this to user)
    VERIFICATION_CODES[email] = verification_code
    
    return True, "Account created. Please verify your email.", user_data

def verify_email(email, code):
    """Verify a user's email with the code."""
    users = load_users()
    
    if email not in users:
        return False, "Account not found."
    
    stored_code = users[email].get("verification_code", "")
    if code == stored_code or code == "000000":  # "000000" for demo/testing
        users[email]["verified"] = True
        users[email]["verification_code"] = None
        save_users(users)
        return True, "Email verified successfully!"
    
    return False, "Invalid verification code."

def authenticate_user(email, password):
    """Authenticate a user by email and password. Returns (success, message, user_data)."""
    users = load_users()
    
    if email not in users:
        return False, "No account found with this email.", None
    
    user = users[email]
    if user.get("password_hash") != hash_password(password):
        return False, "Incorrect password.", None
    
    return True, "Login successful!", user

def authenticate_social(email, full_name, provider):
    """Authenticate or register via social login. Returns (success, message, user_data)."""
    users = load_users()
    
    if email in users:
        # Existing user — add this social provider
        user = users[email]
        if provider not in user.get("social_accounts", []):
            user["social_accounts"] = user.get("social_accounts", []) + [provider]
            user["verified"] = True  # Social login is pre-verified
            save_users(users)
        return True, f"Welcome back, {user['full_name']}!", user
    
    # New user via social login
    user_id = generate_user_id()
    user_data = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "password_hash": None,
        "country": "Unknown",
        "accepted_terms": True,
        "accepted_risk": True,
        "accepted_liability": True,
        "signup_date": datetime.now().isoformat(),
        "verified": True,  # Social login skips email verification
        "verification_code": None,
        "kyc_tier": "tier1",
        "subscription": "paper",
        "login_method": provider,
        "social_accounts": [provider],
    }
    
    users[email] = user_data
    save_users(users)
    return True, "Account created via " + provider + "!", user_data

def get_verification_code(email):
    """Get the verification code for a user (for demo/testing display)."""
    users = load_users()
    if email in users:
        return users[email].get("verification_code", "")
    return ""
