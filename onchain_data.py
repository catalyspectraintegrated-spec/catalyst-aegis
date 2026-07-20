"""
CATALYST AEGIS — On-Chain Data Module
Whale alerts, funding rates, exchange flows, and blockchain metrics.
Uses free public APIs.
"""

import requests
from datetime import datetime

# ============================================================
# WHALE ALERTS
# ============================================================
def get_whale_transactions(asset="BTC", min_value=1000000):
    """
    Fetch large transactions from Whale Alert API (free tier).
    Returns list of recent whale movements.
    """
    try:
        # Free API endpoint (rate limited)
        url = f"https://api.whale-alert.io/v1/transactions"
        params = {
            "api_key": "free",
            "min_value": min_value,
            "limit": 10
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            transactions = []
            for tx in data.get("transactions", []):
                transactions.append({
                    "symbol": tx.get("symbol", "Unknown"),
                    "amount": tx.get("amount", 0),
                    "value_usd": tx.get("amount_usd", 0),
                    "from": tx.get("from", {}).get("owner", "Unknown"),
                    "to": tx.get("to", {}).get("owner", "Unknown"),
                    "timestamp": datetime.fromtimestamp(tx.get("timestamp", 0)).isoformat()
                })
            return transactions
    except:
        pass
    return []

# ============================================================
# FUNDING RATES (Perpetual Futures)
# ============================================================
def get_funding_rates():
    """
    Get current funding rates for major crypto perpetual swaps.
    Positive = longs pay shorts (bullish sentiment).
    Negative = shorts pay longs (bearish sentiment).
    """
    rates = {}
    try:
        # Binance public API
        resp = requests.get("https://fapi.binance.com/fapi/v1/premiumIndex", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            symbols_of_interest = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
            for item in data:
                if item["symbol"] in symbols_of_interest:
                    rates[item["symbol"].replace("USDT", "/USD")] = {
                        "funding_rate": float(item["lastFundingRate"]) * 100,  # as percentage
                        "mark_price": float(item["markPrice"]),
                    }
    except:
        pass
    return rates

# ============================================================
# EXCHANGE FLOWS (Net Inflow/Outflow)
# ============================================================
def get_exchange_flows():
    """
    Get net exchange flow data (simplified).
    Positive = coins moving TO exchanges (potential selling pressure).
    Negative = coins moving OFF exchanges (potential holding/bullish).
    """
    try:
        # CoinGecko free API for exchange volume data
        resp = requests.get("https://api.coingecko.com/api/v3/exchanges", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            top_exchanges = []
            for exchange in data[:5]:
                top_exchanges.append({
                    "name": exchange.get("name"),
                    "volume_24h_btc": exchange.get("trade_volume_24h_btc", 0),
                    "trust_score": exchange.get("trust_score", 0)
                })
            return top_exchanges
    except:
        pass
    return []

# ============================================================
# NETWORK ACTIVITY (Active Addresses)
# ============================================================
def get_network_stats(asset="bitcoin"):
    """
    Get blockchain network statistics.
    """
    try:
        # Blockchain.com API (free)
        if asset.lower() == "bitcoin":
            resp = requests.get("https://api.blockchain.info/stats", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "hash_rate": data.get("hash_rate", 0),
                    "total_transactions": data.get("n_btc_mined", 0),
                    "market_price_usd": data.get("market_price_usd", 0),
                    "total_fees_btc": data.get("total_fees_btc", 0) / 100000000,
                }
    except:
        pass
    return {}

# ============================================================
# AGGREGATED SENTIMENT SCORE
# ============================================================
def get_onchain_sentiment():
    """
    Combine on-chain metrics into a simple sentiment score.
    Returns a score from -100 (extremely bearish) to +100 (extremely bullish).
    """
    score = 0
    
    # Funding rates: extremely positive = overleveraged longs = bearish
    funding = get_funding_rates()
    for asset, data in funding.items():
        if data["funding_rate"] > 0.1:  # Very high funding = bearish
            score -= 20
        elif data["funding_rate"] < -0.05:  # Negative funding = bullish
            score += 15
    
    # Network activity: increasing = bullish
    network = get_network_stats()
    if network:
        # More transactions generally = more usage = bullish
        score += 10  # Placeholder — in production, compare to historical average
    
    # Clamp to -100 to +100
    return max(-100, min(100, score))

# ============================================================
# SUMMARY FOR DASHBOARD
# ============================================================
def get_onchain_summary():
    """Get a summary of on-chain metrics for the dashboard."""
    funding = get_funding_rates()
    whales = get_whale_transactions()
    sentiment = get_onchain_sentiment()
    
    summary = {
        "sentiment_score": sentiment,
        "sentiment_label": "Bullish" if sentiment > 20 else "Bearish" if sentiment < -20 else "Neutral",
        "funding_rates": funding,
        "recent_whales": len(whales),
        "timestamp": datetime.now().isoformat()
    }
    return summary
