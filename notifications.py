"""
CATALYST AEGIS — Push Notifications
Sends Telegram alerts for trade events.
"""

import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(message):
    """Send a Telegram message."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        return resp.status_code == 200
    except:
        return False

def notify_trade_entry(symbol, entry_price, position_size):
    """Notify of a new trade."""
    msg = f"""
🛡️ <b>CATALYST AEGIS — Trade Opened</b>

<b>Symbol:</b> {symbol}
<b>Entry:</b> {entry_price}
<b>Size:</b> {position_size}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

<i>AEGIS is monitoring with trailing stop protection.</i>
"""
    return send_telegram(msg.strip())

def notify_trade_exit(symbol, entry_price, exit_price, pnl, reason):
    """Notify of a closed trade."""
    emoji = "🟢" if pnl > 0 else "🔴"
    msg = f"""
{emoji} <b>CATALYST AEGIS — Trade Closed</b>

<b>Symbol:</b> {symbol}
<b>Entry:</b> {entry_price} → <b>Exit:</b> {exit_price}
<b>P&L:</b> ${pnl:+,.2f}
<b>Reason:</b> {reason}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

<i>Shield active. Scanning for next catalyst.</i>
"""
    return send_telegram(msg.strip())

def notify_daily_summary(total_pnl, trades, win_rate):
    """Send end-of-day summary."""
    emoji = "🟢" if total_pnl > 0 else "🔴"
    msg = f"""
📊 <b>CATALYST AEGIS — Daily Summary</b>

{emoji} <b>P&L:</b> ${total_pnl:+,.2f}
<b>Trades:</b> {trades}
<b>Win Rate:</b> {win_rate:.1f}%
<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

<i>Full report available on your dashboard.</i>
"""
    return send_telegram(msg.strip())
