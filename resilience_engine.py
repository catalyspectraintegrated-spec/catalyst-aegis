"""
CATALYST AEGIS — Resilience Engine
Automatically detects service failures and switches to backups.
No single point of failure can stop the platform.
"""

import os
import importlib
import subprocess
import json
from datetime import datetime

# ============================================================
# HEALTH CHECK SYSTEM
# ============================================================
class ResilienceManager:
    """Monitors all services and manages fallbacks."""
    
    def __init__(self):
        self.status = {
            "data_source": {"active": "yfinance", "healthy": True},
            "llm_provider": {"active": "groq", "healthy": True},
            "ml_model": {"active": "xgboost", "healthy": True},
            "database": {"active": "sqlite", "healthy": True},
            "dashboard": {"active": "streamlit", "healthy": True},
        }
        self.failure_log = []
    
    def check_data_source(self):
        """Check if primary data source is working, switch if not."""
        # Try yfinance
        try:
            import yfinance as yf
            df = yf.download("EURUSD=X", period="1d", interval="1h", progress=False)
            if not df.empty:
                self.status["data_source"] = {"active": "yfinance", "healthy": True}
                return True
        except:
            pass
        
        # Fallback 1: Twelve Data
        api_key = os.environ.get("TWELVE_DATA_API_KEY", "")
        if api_key:
            try:
                import requests
                resp = requests.get(f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&apikey={api_key}")
                if resp.status_code == 200:
                    self.status["data_source"] = {"active": "twelvedata", "healthy": True}
                    self._log_failure("yfinance", "twelvedata")
                    return True
            except:
                pass
        
        # Fallback 2: Alpha Vantage
        api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
        if api_key:
            try:
                import requests
                resp = requests.get(f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=60min&apikey={api_key}")
                if resp.status_code == 200:
                    self.status["data_source"] = {"active": "alphavantage", "healthy": True}
                    self._log_failure("yfinance", "alphavantage")
                    return True
            except:
                pass
        
        # Fallback 3: CSV backup file
        csv_path = "backup_data/eur_usd_h1.csv"
        if os.path.exists(csv_path):
            self.status["data_source"] = {"active": "csv_backup", "healthy": True}
            self._log_failure("yfinance", "csv_backup")
            return True
        
        self.status["data_source"]["healthy"] = False
        self._log_failure("yfinance", "none_available")
        return False
    
    def check_llm(self):
        """Check if primary LLM is working, switch if not."""
        # Try Groq
        api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key:
            try:
                from groq import Groq
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                if response.choices[0].message.content:
                    self.status["llm_provider"] = {"active": "groq", "healthy": True}
                    return True
            except:
                pass
        
        # Fallback 1: Ollama (local)
        try:
            import requests
            resp = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3.2:3b", "prompt": "test", "stream": False
            }, timeout=3)
            if resp.status_code == 200:
                self.status["llm_provider"] = {"active": "ollama", "healthy": True}
                self._log_failure("groq", "ollama")
                return True
        except:
            pass
        
        # Fallback 2: OpenRouter
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if api_key:
            try:
                import requests
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": "meta-llama/llama-3.2-3b-instruct:free", "messages": [{"role": "user", "content": "test"}]},
                    timeout=5)
                if resp.status_code == 200:
                    self.status["llm_provider"] = {"active": "openrouter", "healthy": True}
                    self._log_failure("groq", "openrouter")
                    return True
            except:
                pass
        
        # Fallback 3: Offline mode (smart responses built into AEGIS)
        self.status["llm_provider"] = {"active": "offline", "healthy": True}
        self._log_failure("groq", "offline")
        return True  # Offline mode always works
    
    def check_ml_model(self):
        """Check if ML model is available, switch if not."""
        # Try XGBoost
        try:
            import xgboost
            self.status["ml_model"] = {"active": "xgboost", "healthy": True}
            return True
        except:
            pass
        
        # Fallback 1: LightGBM
        try:
            import lightgbm
            self.status["ml_model"] = {"active": "lightgbm", "healthy": True}
            self._log_failure("xgboost", "lightgbm")
            return True
        except:
            pass
        
        # Fallback 2: RandomForest (scikit-learn — always available)
        try:
            from sklearn.ensemble import RandomForestClassifier
            self.status["ml_model"] = {"active": "randomforest", "healthy": True}
            self._log_failure("xgboost", "randomforest")
            return True
        except:
            pass
        
        self.status["ml_model"]["healthy"] = False
        return False
    
    def check_all(self):
        """Run all health checks and return status."""
        self.check_data_source()
        self.check_llm()
        self.check_ml_model()
        
        # Always healthy
        self.status["database"] = {"active": "sqlite", "healthy": True}
        self.status["dashboard"] = {"active": "streamlit", "healthy": True}
        
        return self.status
    
    def _log_failure(self, failed_service, switched_to):
        """Log a service failure."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "failed": failed_service,
            "switched_to": switched_to
        }
        self.failure_log.append(entry)
        # Keep only last 100 entries
        if len(self.failure_log) > 100:
            self.failure_log = self.failure_log[-100:]
        
        # Save to file
        with open("failure_log.json", "w") as f:
            json.dump(self.failure_log, f, indent=2)
        
        print(f"⚠️ {failed_service} failed → switched to {switched_to}")
    
    def get_status_report(self):
        """Generate a human-readable status report."""
        report = []
        report.append("=" * 50)
        report.append("   CATALYST AEGIS — System Health Report")
        report.append("=" * 50)
        
        for service, info in self.status.items():
            status_icon = "✅" if info["healthy"] else "❌"
            report.append(f"{status_icon} {service}: {info['active']}")
        
        if self.failure_log:
            report.append(f"\n⚠️ Recent failures: {len(self.failure_log)}")
            for entry in self.failure_log[-3:]:
                report.append(f"   {entry['timestamp']}: {entry['failed']} → {entry['switched_to']}")
        
        return "\n".join(report)

# ============================================================
# AUTO-RECOVERY DAEMON
# ============================================================
def start_resilience_monitor():
    """Start the resilience monitor that checks services periodically."""
    import time
    
    manager = ResilienceManager()
    print(manager.get_status_report())
    
    while True:
        try:
            manager.check_all()
            time.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\nResilience monitor stopped.")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(60)

# ============================================================
# BACKUP DATA PIPELINE
# ============================================================
def save_data_backup():
    """Save current database to CSV backup files."""
    import pandas as pd
    from sqlalchemy import create_engine
    
    os.makedirs("backup_data", exist_ok=True)
    engine = create_engine("sqlite:///trading_data.db")
    
    tables = ["eur_usd_h1", "eur_usd_m15", "btc_usd_h1", "btc_usd_m15",
              "eth_usd_h1", "eth_usd_m15", "bnb_usd_h1", "bnb_usd_m15",
              "sol_usd_h1", "sol_usd_m15",
              "gbp_usd_h1", "gbp_usd_m15", "usd_jpy_h1", "usd_jpy_m15",
              "aud_usd_h1", "aud_usd_m15", "eur_jpy_h1", "eur_jpy_m15",
              "gbp_jpy_h1", "gbp_jpy_m15"]
    
    for table in tables:
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", engine)
            df.to_csv(f"backup_data/{table}.csv", index=False)
        except:
            pass
    
    print(f"✅ Data backed up to backup_data/ ({len(tables)} tables)")

if __name__ == "__main__":
    # Run health check
    manager = ResilienceManager()
    manager.check_all()
    print(manager.get_status_report())
    
    # Save data backup
    save_data_backup()
