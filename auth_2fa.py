"""
CATALYST AEGIS — Two-Factor Authentication
TOTP-based 2FA using Google Authenticator compatible codes.
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime

def generate_2fa_secret(user_email):
    """Generate a new TOTP secret for a user."""
    secret = pyotp.random_base32()
    # Store this secret in the user's profile
    return secret

def get_totp_uri(user_email, secret):
    """Generate the TOTP URI for QR code."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name="Catalyst AEGIS"
    )

def generate_qr_code(uri):
    """Generate a QR code image as base64."""
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def verify_2fa_code(secret, code):
    """Verify a TOTP code."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def is_2fa_enabled(user_data):
    """Check if 2FA is enabled for a user."""
    return user_data.get('2fa_secret') is not None and user_data.get('2fa_enabled', False)

def enable_2fa(user_data, secret):
    """Enable 2FA for a user."""
    user_data['2fa_secret'] = secret
    user_data['2fa_enabled'] = True
    user_data['2fa_enabled_date'] = datetime.now().isoformat()
    return user_data

def disable_2fa(user_data):
    """Disable 2FA for a user."""
    user_data['2fa_secret'] = None
    user_data['2fa_enabled'] = False
    return user_data
