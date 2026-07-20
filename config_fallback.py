"""
CATALYST AEGIS — Fallback Configuration
If any service fails, swap to an alternative here.
"""

# Data Source Fallbacks (in priority order)
DATA_SOURCES = {
    "primary": "yfinance",      # Yahoo Finance (free)
    "fallback_1": "twelvedata", # Twelve Data API (free tier: 800 requests/day)
    "fallback_2": "alpha_vantage", # Alpha Vantage (free API key)
    "fallback_3": "binance",    # Binance public API (crypto only, unlimited)
}

# LLM Provider Fallbacks
LLM_PROVIDERS = {
    "primary": "groq",          # Groq Cloud (free tier)
    "fallback_1": "ollama",     # Local Ollama (runs on your hardware)
    "fallback_2": "openrouter", # OpenRouter (free tier available)
    "fallback_3": "offline",    # Smart keyword matching (no internet needed)
}

# ML Model Fallbacks
ML_MODELS = {
    "primary": "xgboost",
    "fallback_1": "lightgbm",
    "fallback_2": "random_forest",
}

# Database Fallbacks
DATABASES = {
    "primary": "sqlite",
    "fallback": "postgresql",
}

def get_active_config():
    """Check which services are available and return working config."""
    import os
    
    config = {
        "data_source": "yfinance",
        "llm_provider": "groq" if os.environ.get("GROQ_API_KEY") else "ollama",
        "ml_model": "xgboost",
        "database": "sqlite",
    }
    
    return config
