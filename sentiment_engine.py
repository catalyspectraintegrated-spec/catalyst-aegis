import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

def get_llm_sentiment(text, asset="EUR/USD"):
    """Send text to local LLM and get structured sentiment."""
    prompt = f"""You are a financial sentiment analyzer. Analyze the following news headline for its impact on {asset}.

Return ONLY valid JSON with these fields:
- sentiment: "bullish", "bearish", or "neutral"
- confidence: 0.0 to 1.0
- impact: "high", "medium", or "low"
- reason: brief explanation (max 10 words)

Headline: "{text}"

JSON:"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "max_tokens": 150}
        }, timeout=15)
        
        if response.status_code == 200:
            result = response.json()["response"].strip()
            # Extract JSON from response
            if "{" in result and "}" in result:
                start = result.index("{")
                end = result.rindex("}") + 1
                parsed = json.loads(result[start:end])
                return {
                    "sentiment": parsed.get("sentiment", "neutral"),
                    "confidence": float(parsed.get("confidence", 0.5)),
                    "impact": parsed.get("impact", "medium"),
                    "reason": parsed.get("reason", "")
                }
    except Exception as e:
        pass
    
    return {"sentiment": "neutral", "confidence": 0.5, "impact": "low", "reason": "error"}

def fetch_crypto_news():
    """Fetch recent crypto headlines from free RSS feeds."""
    headlines = []
    
    # CoinDesk RSS
    try:
        resp = requests.get("https://www.coindesk.com/arc/outboundfeeds/rss/", timeout=10)
        root = ET.fromstring(resp.content)
        for item in root.findall(".//item")[:10]:
            title = item.find("title").text if item.find("title") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            headlines.append({"headline": title, "source": "CoinDesk", "date": pub_date})
    except:
        pass
    
    # CryptoSlate RSS
    try:
        resp = requests.get("https://cryptoslate.com/feed/", timeout=10)
        root = ET.fromstring(resp.content)
        for item in root.findall(".//item")[:10]:
            title = item.find("title").text if item.find("title") is not None else ""
            headlines.append({"headline": title, "source": "CryptoSlate", "date": ""})
    except:
        pass
    
    return headlines

def fetch_forex_news():
    """Fetch recent forex headlines from free RSS feeds."""
    headlines = []
    
    # ForexLive RSS
    try:
        resp = requests.get("https://www.forexlive.com/feed/", timeout=10)
        root = ET.fromstring(resp.content)
        for item in root.findall(".//item")[:10]:
            title = item.find("title").text if item.find("title") is not None else ""
            headlines.append({"headline": title, "source": "ForexLive", "date": ""})
    except:
        pass
    
    # Investing.com RSS
    try:
        resp = requests.get("https://www.investing.com/rss/news_25.rss", timeout=10)
        root = ET.fromstring(resp.content)
        for item in root.findall(".//item")[:10]:
            title = item.find("title").text if item.find("title") is not None else ""
            headlines.append({"headline": title, "source": "Investing.com", "date": ""})
    except:
        pass
    
    return headlines

def generate_sentiment_features(asset="BTC/USD"):
    """Main function: fetch news, analyze sentiment, return feature dict."""
    if "BTC" in asset or "crypto" in asset.lower():
        headlines = fetch_crypto_news()
    else:
        headlines = fetch_forex_news()
    
    if not headlines:
        return {
            "sentiment_bullish_pct": 0.5,
            "sentiment_bearish_pct": 0.0,
            "sentiment_neutral_pct": 0.5,
            "avg_confidence": 0.5,
            "high_impact_count": 0,
            "total_headlines": 0
        }
    
    results = []
    for h in headlines[:15]:  # Limit to 15 headlines
        sentiment = get_llm_sentiment(h["headline"], asset)
        sentiment["headline"] = h["headline"]
        sentiment["source"] = h["source"]
        results.append(sentiment)
    
    # Aggregate
    bullish = sum(1 for r in results if r["sentiment"] == "bullish")
    bearish = sum(1 for r in results if r["sentiment"] == "bearish")
    neutral = sum(1 for r in results if r["sentiment"] == "neutral")
    total = len(results)
    
    features = {
        "sentiment_bullish_pct": bullish / total if total > 0 else 0.5,
        "sentiment_bearish_pct": bearish / total if total > 0 else 0.0,
        "sentiment_neutral_pct": neutral / total if total > 0 else 0.5,
        "avg_confidence": sum(r["confidence"] for r in results) / total if total > 0 else 0.5,
        "high_impact_count": sum(1 for r in results if r["impact"] == "high"),
        "total_headlines": total
    }
    
    print(f"\n📰 {asset} Sentiment Analysis ({total} headlines):")
    print(f"   Bullish: {bullish} | Bearish: {bearish} | Neutral: {neutral}")
    for r in results[:5]:
        emoji = "🟢" if r["sentiment"] == "bullish" else "🔴" if r["sentiment"] == "bearish" else "⚪"
        print(f"   {emoji} [{r['source']}] {r['headline'][:80]}...")
    
    return features

if __name__ == "__main__":
    print("="*50)
    print("   LLM Sentiment Engine Test")
    print("="*50)
    
    print("\n--- BTC/USD Sentiment ---")
    btc_features = generate_sentiment_features("BTC/USD")
    print(f"\nFeatures: {json.dumps(btc_features, indent=2)}")
    
    print("\n--- EUR/USD Sentiment ---")
    eur_features = generate_sentiment_features("EUR/USD")
    print(f"\nFeatures: {json.dumps(eur_features, indent=2)}")
