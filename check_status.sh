#!/bin/bash
echo "🛡️ Catalyst AEGIS — Status Check"
echo "================================"
echo ""

# Check Streamlit
if ps aux | grep -v grep | grep streamlit > /dev/null; then
    echo "✅ Dashboard: Running"
else
    echo "❌ Dashboard: Stopped"
fi

# Check Live Engine
if ps aux | grep -v grep | grep live_engine > /dev/null; then
    echo "✅ Live Engine: Running"
else
    echo "❌ Live Engine: Stopped"
fi

# Check Groq
if [ -n "$GROQ_API_KEY" ]; then
    echo "✅ Groq API: Configured"
else
    echo "⚠️ Groq API: Not set (using fallback)"
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama: Running"
else
    echo "⚠️ Ollama: Not running"
fi

echo ""
echo "================================"
echo "Run full health check:"
echo "  python resilience_engine.py"
