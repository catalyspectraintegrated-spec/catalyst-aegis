"""
CATALYST AEGIS — User Analytics Engine
Personal P&L charts, win rate by asset, performance metrics.
"""

import json
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

TRADE_LOG_FILE = "trade_log.json"

def load_user_trades():
    """Load trade history."""
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE) as f:
            return json.load(f).get("trades", [])
    return []

def get_personal_metrics():
    """Calculate personal trading metrics."""
    trades = load_user_trades()
    closed = [t for t in trades if t.get("status") == "closed"]
    
    if not closed:
        return {
            "total_trades": 0, "win_rate": 0, "total_pnl": 0,
            "avg_win": 0, "avg_loss": 0, "best_trade": 0, "worst_trade": 0,
            "profit_factor": 0, "sharpe_ratio": 0, "max_drawdown": 0,
            "monthly_returns": [], "win_rate_by_asset": {}
        }
    
    wins = [t for t in closed if t.get("pnl", 0) > 0]
    losses = [t for t in closed if t.get("pnl", 0) <= 0]
    total_pnl = sum(t.get("pnl", 0) for t in closed)
    
    # Basic metrics
    win_rate = len(wins) / len(closed) * 100 if closed else 0
    avg_win = np.mean([t["pnl"] for t in wins]) if wins else 0
    avg_loss = np.mean([t["pnl"] for t in losses]) if losses else 0
    best_trade = max([t["pnl"] for t in closed]) if closed else 0
    worst_trade = min([t["pnl"] for t in closed]) if closed else 0
    
    # Profit factor
    gross_profit = sum(t["pnl"] for t in wins)
    gross_loss = abs(sum(t["pnl"] for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Win rate by asset
    assets = set(t.get("symbol", "Unknown") for t in closed)
    win_rate_by_asset = {}
    for asset in assets:
        asset_trades = [t for t in closed if t.get("symbol") == asset]
        asset_wins = [t for t in asset_trades if t.get("pnl", 0) > 0]
        win_rate_by_asset[asset] = {
            "trades": len(asset_trades),
            "win_rate": len(asset_wins) / len(asset_trades) * 100 if asset_trades else 0,
            "pnl": sum(t.get("pnl", 0) for t in asset_trades)
        }
    
    # Monthly returns
    monthly = {}
    for t in closed:
        month = t.get("exit_time", "")[:7]
        if month:
            monthly[month] = monthly.get(month, 0) + t.get("pnl", 0)
    monthly_returns = [{"month": k, "pnl": v} for k, v in sorted(monthly.items())]
    
    # Max drawdown
    equity_curve = [10000]
    for t in closed:
        equity_curve.append(equity_curve[-1] + t.get("pnl", 0))
    equity = np.array(equity_curve)
    peak = np.maximum.accumulate(equity)
    max_dd = np.min((equity - peak) / peak) * 100 if len(equity) > 1 else 0
    
    # Sharpe ratio (simplified)
    returns = [t.get("pnl", 0) / 10000 for t in closed]
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0
    
    return {
        "total_trades": len(closed),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "best_trade": round(best_trade, 2),
        "worst_trade": round(worst_trade, 2),
        "profit_factor": round(profit_factor, 2),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown": round(max_dd, 2),
        "monthly_returns": monthly_returns,
        "win_rate_by_asset": win_rate_by_asset
    }
