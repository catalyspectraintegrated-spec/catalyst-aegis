"""
CATALYST AEGIS — Email Service
Handles verification emails, trade alerts, and reports.
Uses SMTP (Gmail, SendGrid, or custom SMTP).
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Configure these via environment variables
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@catalystaegis.com")
FROM_NAME = "Catalyst AEGIS"

def send_email(to_email, subject, body_html, attachment_path=None):
    """Send an email with optional attachment."""
    if not SMTP_USER or not SMTP_PASS:
        print("⚠️ SMTP not configured. Email not sent.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
                msg.attach(part)
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def send_verification_email(to_email, code, user_name):
    """Send email verification code."""
    subject = "Verify Your Catalyst AEGIS Account"
    body = f"""
    <div style="background:#0A1628;color:#D0D8E0;padding:30px;font-family:Arial;">
        <h1 style="color:#D4A017;">🛡️ Catalyst AEGIS</h1>
        <h2>Welcome, {user_name}!</h2>
        <p>Your verification code is:</p>
        <h1 style="color:#D4A017;font-size:36px;letter-spacing:5px;">{code}</h1>
        <p>Enter this code on the verification page to activate your account.</p>
        <p>If you didn't create this account, please ignore this email.</p>
        <hr>
        <p style="font-size:11px;">Catalyspectra Integrated Solutions LTD (RC: 9544839) | Not financial advice.</p>
    </div>
    """
    return send_email(to_email, subject, body)

def send_trade_alert(to_email, trade_type, symbol, entry_price, exit_price=None, pnl=None):
    """Send trade entry/exit alert."""
    if trade_type == "entry":
        subject = f"🔵 Trade Opened: {symbol}"
        body = f"""
        <div style="background:#0A1628;color:#D0D8E0;padding:30px;font-family:Arial;">
            <h1 style="color:#D4A017;">🛡️ Trade Alert</h1>
            <h2>New Position Opened</h2>
            <p><strong>Symbol:</strong> {symbol}</p>
            <p><strong>Entry Price:</strong> {entry_price}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
            <p>AEGIS is monitoring this position with trailing stop protection.</p>
        </div>
        """
    else:
        emoji = "🟢" if pnl > 0 else "🔴"
        subject = f"{emoji} Trade Closed: {symbol} | P&L: ${pnl:+,.2f}"
        body = f"""
        <div style="background:#0A1628;color:#D0D8E0;padding:30px;font-family:Arial;">
            <h1 style="color:#D4A017;">🛡️ Trade Alert</h1>
            <h2>Position Closed</h2>
            <p><strong>Symbol:</strong> {symbol}</p>
            <p><strong>Entry:</strong> {entry_price} | <strong>Exit:</strong> {exit_price}</p>
            <p><strong>P&L:</strong> <span style="color:{'#00ff88' if pnl > 0 else '#ff4444'};font-size:20px;">${pnl:+,.2f}</span></p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
        </div>
        """
    return send_email(to_email, subject, body)

def send_daily_report(to_email, report_path):
    """Send daily performance report."""
    subject = f"📊 Catalyst AEGIS Daily Report — {datetime.now().strftime('%Y-%m-%d')}"
    body = """
    <div style="background:#0A1628;color:#D0D8E0;padding:30px;font-family:Arial;">
        <h1 style="color:#D4A017;">🛡️ Daily Report</h1>
        <p>Your daily trading report is attached.</p>
        <p>Log in to your dashboard for real-time updates.</p>
    </div>
    """
    return send_email(to_email, subject, body, report_path)
