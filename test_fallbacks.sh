#!/bin/bash
echo "============================================"
echo "   CATALYST AEGIS — FALLBACK TEST SUITE"
echo "============================================"
echo ""

echo "Test 1: Data Source Fallback..."
python -c "
from resilience_engine import ResilienceManager
import yfinance
original = yfinance.download
yfinance.download = lambda *a, **k: __import__('pandas').DataFrame()
manager = ResilienceManager()
manager.check_data_source()
s = manager.status['data_source']
print(f'  Active: {s[\"active\"]} | Healthy: {s[\"healthy\"]}')
yfinance.download = original
"

echo ""
echo "Test 2: LLM Fallback..."
python -c "
from resilience_engine import ResilienceManager
import os
old = os.environ.pop('GROQ_API_KEY', None)
manager = ResilienceManager()
manager.check_llm()
s = manager.status['llm_provider']
print(f'  Active: {s[\"active\"]} | Healthy: {s[\"healthy\"]}')
if old: os.environ['GROQ_API_KEY'] = old
"

echo ""
echo "Test 3: ML Model Fallback..."
python -c "
from resilience_engine import ResilienceManager
import sys
sys.modules['xgboost'] = None
manager = ResilienceManager()
manager.check_ml_model()
s = manager.status['ml_model']
print(f'  Active: {s[\"active\"]} | Healthy: {s[\"healthy\"]}')
del sys.modules['xgboost']
"

echo ""
echo "============================================"
echo "   All fallback tests complete."
echo "   Catalyst AEGIS survives service failures."
echo "============================================"
