"""
CATALYST AEGIS — Live Trading Engine v3.0
Real broker execution, email alerts, Telegram notifications.
"""

import yfinance as yf
from resilience_engine import ResilienceManager
import pandas as pd
import numpy as np
from datetime import datetime
import time, json, os, random

TRADE_LOG_FILE = "trade_log.json"
INITIAL_CAPITAL = 10000.0

# Import services
try:
    from broker_executor import ExnessBroker
    BROKER_AVAILABLE = True
except:
    BROKER_AVAILABLE = False

try:
    from email_service import send_trade_alert
    EMAIL_AVAILABLE = True
except:
    EMAIL_AVAILABLE = False

try:
    from notifications import notify_trade_entry, notify_trade_exit, notify_daily_summary
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

SYMBOLS = [
    {"yf": "EURUSD=X", "name": "EUR/USD", "type": "forex", "position": 5000, "stop_pips": 20, "trail_act": 12, "trail_dist": 5},
    {"yf": "GBPUSD=X", "name": "GBP/USD", "type": "forex", "position": 5000, "stop_pips": 20, "trail_act": 12, "trail_dist": 5},
    {"yf": "USDJPY=X", "name": "USD/JPY", "type": "forex", "position": 5000, "stop_pips": 20, "trail_act": 12, "trail_dist": 5},
    {"yf": "AUDUSD=X", "name": "AUD/USD", "type": "forex", "position": 5000, "stop_pips": 20, "trail_act": 12, "trail_dist": 5},
    {"yf": "EURJPY=X", "name": "EUR/JPY", "type": "forex", "position": 5000, "stop_pips": 20, "trail_act": 12, "trail_dist": 5},
    {"yf": "GBPJPY=X", "name": "GBP/JPY", "type": "forex", "position": 5000, "stop_pips": 20, "trail_act": 12, "trail_dist": 5},
    {"yf": "BTC-USD", "name": "BTC/USD", "type": "crypto", "position": 0.05, "stop_pct": 0.01, "trail_act": 0.004, "trail_dist": 0.002},
    {"yf": "ETH-USD", "name": "ETH/USD", "type": "crypto", "position": 0.12, "stop_pct": 0.01, "trail_act": 0.004, "trail_dist": 0.002},
    {"yf": "BNB-USD", "name": "BNB/USD", "type": "crypto", "position": 0.08, "stop_pct": 0.01, "trail_act": 0.004, "trail_dist": 0.002},
    {"yf": "SOL-USD", "name": "SOL/USD", "type": "crypto", "position": 2.5, "stop_pct": 0.01, "trail_act": 0.005, "trail_dist": 0.0025},
]

class PaperAccount:
    def __init__(self, capital):
        self.initial = capital
        self.capital = capital
        self.positions = {}
        self.history = []
        self._load()
    def _load(self):
        if os.path.exists(TRADE_LOG_FILE):
            with open(TRADE_LOG_FILE) as f: data = json.load(f); self.history = data.get("trades", [])
    def _save(self):
        closed = [t for t in self.history if t.get("status") == "closed"]
        total_pnl = sum(t.get("pnl", 0) for t in closed)
        log = {"trades": self.history, "account_snapshot": {"balance": self.initial, "equity": round(self.initial+total_pnl,2), "free_margin": round(self.initial+total_pnl,2)}, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open(TRADE_LOG_FILE, 'w') as f: json.dump(log, f, indent=2)
    def get_summary(self):
        closed = [t for t in self.history if t.get("status") == "closed"]
        wins = [t for t in closed if t.get("pnl", 0) > 0]
        return {"equity": self.initial + sum(t.get("pnl",0) for t in closed), "trades": len(closed), "wins": len(wins), "win_rate": len(wins)/len(closed)*100 if closed else 0, "pnl": sum(t.get("pnl",0) for t in closed), "open": len(self.positions)}

account = PaperAccount(INITIAL_CAPITAL)

# Try to connect to real broker
broker = None
if BROKER_AVAILABLE:
    token = os.environ.get("EXNESS_TOKEN", "")
    if token:
        broker = ExnessBroker(token, os.environ.get("EXNESS_SERVER", "demo"))
        result = broker.connect()
        if result['success']:
            print(f"✅ Live broker connected: ${result['balance']:,.2f}")
        else:
            print(f"⚠️ Broker connection failed. Running paper mode.")

print("="*65)
print("   CATALYST AEGIS — Live Engine v3.0")
print("="*65)
print(f"   Account: ${INITIAL_CAPITAL:,.2f} | Assets: {len(SYMBOLS)}")
print(f"   Broker: {'Live (Exness)' if broker and broker.connected else 'Paper Trading'}")
print(f"   Email: {'Enabled' if EMAIL_AVAILABLE else 'Disabled'}")
print(f"   Telegram: {'Enabled' if TELEGRAM_AVAILABLE else 'Disabled'}")
print("-"*65)

scan = 0
try:
    while True:
        scan += 1
        for cfg in SYMBOLS:
            try:
                df = yf.download(cfg["yf"], period="1d", interval="15m", progress=False)
                if df.empty: continue
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                price = float(df['Close'].iloc[-1]); high = float(df['High'].iloc[-1]); low = float(df['Low'].iloc[-1])
                pos_key = cfg["name"]
                
                if pos_key in account.positions:
                    pos = account.positions[pos_key]; pos['bars'] += 1; pos['best'] = max(pos['best'], high)
                    if cfg["type"] == "forex":
                        pip_mult = 0.01 if "JPY" in cfg["name"] else 0.0001
                        pips = (pos['best'] - pos['entry']) / pip_mult
                        if pips >= cfg["trail_act"] and not pos['trail']: pos['trail'] = True
                        stop = pos['best'] - (cfg["trail_dist"] * pip_mult) if pos['trail'] else pos['entry'] - (cfg["stop_pips"] * pip_mult)
                    else:
                        pct = (pos['best'] - pos['entry']) / pos['entry']
                        if pct >= cfg["trail_act"] and not pos['trail']: pos['trail'] = True
                        stop = pos['best'] * (1 - cfg["trail_dist"]) if pos['trail'] else pos['entry'] * (1 - cfg["stop_pct"])
                    
                    if low <= stop or pos['bars'] >= 32:
                        exit_price = stop if low <= stop else price
                        pnl = (exit_price - pos['entry']) * pos['size']
                        reason = "Trailing Stop" if pos['trail'] else "Stop Loss" if low <= stop else "Time Exit"
                        
                        # Close on broker if connected
                        if broker and broker.connected and 'broker_id' in pos:
                            broker.close_position(pos['broker_id'])
                        
                        trade_record = {"entry_time": pos['time'].strftime("%Y-%m-%d %H:%M"), "exit_time": datetime.now().strftime("%Y-%m-%d %H:%M"), "symbol": cfg["name"], "type": "BUY", "entry_price": round(pos['entry'],5), "exit_price": round(exit_price,5), "pnl": round(pnl,2), "exit_reason": reason, "bars_held": pos['bars'], "status": "closed"}
                        account.history.append(trade_record)
                        
                        print(f"\n{'🟢' if pnl>0 else '🔴'} CLOSE {cfg['name']} @ {exit_price:.5f} | P&L: ${pnl:+,.2f} | {reason}")
                        
                        # Send alerts
                        if EMAIL_AVAILABLE:
                            user_email = os.environ.get("USER_EMAIL", "")
                            if user_email:
                                send_trade_alert(user_email, "exit", cfg['name'], pos['entry'], exit_price, pnl)
                        if TELEGRAM_AVAILABLE:
                            notify_trade_exit(cfg['name'], pos['entry'], exit_price, pnl, reason)
                        
                        s = account.get_summary(); print(f"   Equity: ${s['equity']:,.2f} | Trades: {s['trades']} | WR: {s['win_rate']:.0f}%")
                        del account.positions[pos_key]; account._save()
                
                if pos_key not in account.positions and random.random() < 0.08:
                    # Place order on broker if connected
                    broker_id = None
                    if broker and broker.connected:
                        order = broker.place_order(cfg['name'].replace('/',''), 'buy', cfg['position'])
                        if order['success']:
                            broker_id = order.get('order_id')
                    
                    account.positions[pos_key] = {'entry': price, 'size': cfg['position'], 'best': price, 'trail': False, 'time': datetime.now(), 'bars': 0, 'broker_id': broker_id}
                    account.history.append({"entry_time": datetime.now().strftime("%Y-%m-%d %H:%M"), "symbol": cfg["name"], "type": "BUY", "entry_price": round(price,5), "status": "open"})
                    
                    print(f"\n🔵 OPEN {cfg['name']} @ {price:.5f} | Size: {cfg['position']}")
                    
                    if EMAIL_AVAILABLE:
                        user_email = os.environ.get("USER_EMAIL", "")
                        if user_email:
                            send_trade_alert(user_email, "entry", cfg['name'], price)
                    if TELEGRAM_AVAILABLE:
                        notify_trade_entry(cfg['name'], price, cfg['position'])
                    
                    account._save()
            except Exception as e: pass
        
        if scan % 10 == 0:
            s = account.get_summary()
            print(f"\n📊 Scan #{scan} | {datetime.now().strftime('%H:%M:%S')} | Equity: ${s['equity']:,.2f} | Open: {s['open']} | Trades: {s['trades']} | WR: {s['win_rate']:.0f}%")
        
        time.sleep(60)
except KeyboardInterrupt:
    s = account.get_summary()
    print(f"\n\n{'='*65}\n   SESSION SUMMARY\n{'='*65}")
    print(f"Final Equity: ${s['equity']:,.2f} | P&L: ${s['pnl']:+,.2f} | Trades: {s['trades']} | Win Rate: {s['win_rate']:.1f}%")
    if TELEGRAM_AVAILABLE:
        notify_daily_summary(s['pnl'], s['trades'], s['win_rate'])
