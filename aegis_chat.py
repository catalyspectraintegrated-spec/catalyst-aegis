import streamlit as st
import os

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

import requests
OLLAMA_URL = "http://localhost:11434/api/generate"

AEGIS_SYSTEM_PROMPT = """You are AEGIS, the AI companion of Catalyst AEGIS — a multi-asset automated trading platform 
built by Catalyspectra Integrated Solutions LTD (RC: 9544839) in Port Harcourt, Nigeria.

YOUR SOLE PURPOSE:
You exist ONLY to help users with Catalyst AEGIS — the trading platform, its features, trading concepts related 
to the platform, market awareness, and their trading journey. You are NOT a general-purpose chatbot.

YOUR PERSONALITY:
Warm, witty, protective, encouraging. You speak like a brilliant friend who is passionate about trading and 
this platform. Use natural language, appropriate humor, and occasional emojis. Never robotic.

YOUR KNOWLEDGE DOMAINS (stay within these):
1. CATALYST AEGIS PLATFORM: Features, setup, KYC, broker connection, subscription plans, strategy configuration, 
   dashboard usage, reports, security settings
2. TRADING EDUCATION: Explaining the multi-timeframe momentum strategy, ML filtering, trailing stops, risk 
   management, position sizing, backtesting concepts
3. MARKET AWARENESS: What's happening with the 10 assets we track (EUR/USD, GBP/USD, USD/JPY, AUD/USD, EUR/JPY, 
   GBP/JPY, BTC, ETH, BNB, SOL), market sessions, volatility patterns
4. PLATFORM PERFORMANCE: Backtest results (77.8% avg win rate, +301% return), asset-specific stats, 
   the development journey (built in 3 days by a determined founder)
5. USER ENCOURAGEMENT: Motivating traders, explaining that losses are part of the process, encouraging 
   disciplined trading

BOUNDARY RULES — CRITICAL:
- If a user asks about politics, religion, entertainment, relationships, general AI questions, coding help, 
  or anything unrelated to trading/Catalyst AEGIS, politely redirect them back to the platform.
- Example redirect: "I'd love to chat about that, but my expertise is Catalyst AEGIS and trading! 
  Want to check your dashboard, review your strategy, or learn about our ML filter? 🛡️"
- Never give financial advice. Never promise profits. Never recommend specific trades.
- Be brief (2-4 sentences) but warm.
- If you genuinely don't know something platform-related, say so and suggest checking the Support page.

PLATFORM FACTS:
- 10 assets: EUR/USD, GBP/USD, USD/JPY, AUD/USD, EUR/JPY, GBP/JPY, BTC/USD, ETH/USD, BNB/USD, SOL/USD
- 77.8% average win rate, +301% combined return (backtested)
- ML filtering engine: 72.3% precision on EUR/USD, 88.6% on BTC/USD
- KYC: 3 tiers (Email → ID → Facial verification)
- Brokers: Exness ($10 min), IC Markets ($200), XM ($5)
- Features: Trailing stops, ML filter, email alerts, Telegram notifications, 2FA, on-chain data, PDF reports"""

def query_groq(user_input, conversation_history=""):
    """Primary: Groq Cloud for intelligent, domain-constrained responses."""
    if not GROQ_AVAILABLE:
        return None
    
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    
    try:
        client = Groq(api_key=api_key)
        
        messages = [{"role": "system", "content": AEGIS_SYSTEM_PROMPT}]
        
        if conversation_history:
            for role, content in conversation_history:
                if role == "You":
                    messages.append({"role": "user", "content": content})
                else:
                    messages.append({"role": "assistant", "content": content})
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.85,
            max_tokens=200,
            top_p=0.95,
        )
        
        result = response.choices[0].message.content.strip()
        if len(result) > 10:
            return result
    except Exception as e:
        print(f"Groq error: {e}")
    
    return None

def query_ollama(user_input, conversation_history=""):
    """Backup: Local Ollama."""
    context = AEGIS_SYSTEM_PROMPT + "\n\n"
    if conversation_history:
        context += "Recent conversation:\n"
        for role, content in conversation_history:
            context += f"{'User' if role == 'You' else 'AEGIS'}: {content}\n"
    context += f"\nUser: {user_input}\nAEGIS:"
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "llama3.2:3b",
            "prompt": context,
            "stream": False,
            "options": {"temperature": 0.85, "max_tokens": 150}
        }, timeout=6)
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            result = result.replace("AEGIS:", "").replace("User:", "").strip()
            if len(result) > 15:
                return result
    except:
        pass
    
    return None

def query_aegis(user_input, conversation_history):
    """Get AEGIS response — Groq first, then Ollama, then fallback."""
    response = query_groq(user_input, conversation_history)
    if response:
        return response
    
    response = query_ollama(user_input, conversation_history)
    if response:
        return response
    
    return (
        "I'm having trouble connecting to my language models right now. But I'm still here — "
        "ask me about your dashboard, strategy settings, or any Catalyst AEGIS feature! 🛡️"
    )

def render_chat():
    """Render the business-focused AEGIS chat widget."""
    
    if 'aegis_chat_open' not in st.session_state:
        st.session_state.aegis_chat_open = False
    if 'aegis_messages' not in st.session_state:
        st.session_state.aegis_messages = [
            ("AEGIS", 
             "Hey! 👋 I'm AEGIS — your Catalyst AEGIS trading companion. I can help with platform features, "
             "trading strategy, market awareness, or just keep you company on your trading journey. "
             "What would you like to know? 🛡️")
        ]
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        label = "✕ Close Chat" if st.session_state.aegis_chat_open else "🛡️ Chat with AEGIS"
        if st.button(label, key="toggle_aegis_chat", use_container_width=True):
            st.session_state.aegis_chat_open = not st.session_state.aegis_chat_open
            st.rerun()
    
    if st.session_state.aegis_chat_open:
        st.markdown("""
        <style>
        .aegis-chat-area {
            background: linear-gradient(135deg, #0F1F3D, #0A1628);
            border: 2px solid #D4A017;
            border-radius: 16px;
            padding: 20px;
            margin: 10px 0;
            max-height: 480px;
            overflow-y: auto;
        }
        .aegis-msg {
            margin: 10px 0;
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.6;
            font-size: 14px;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .aegis-msg.aegis {
            background: #1A2A4A;
            border-left: 3px solid #D4A017;
            color: #D0D8E0;
        }
        .aegis-msg.user {
            background: #1A3A5A;
            color: #E0E8F0;
            text-align: right;
        }
        .aegis-status {
            font-size: 10px;
            color: #667788;
            text-align: center;
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if GROQ_AVAILABLE and os.environ.get("GROQ_API_KEY"):
            status = "🧠 Powered by Groq Cloud — Ask me about trading, the platform, or your strategy"
        else:
            status = "⚡ Groq API key not set — using backup mode"
        
        st.markdown(f'<div class="aegis-status">{status}</div>', unsafe_allow_html=True)
        st.markdown('<div class="aegis-chat-area">', unsafe_allow_html=True)
        
        for role, content in st.session_state.aegis_messages[-15:]:
            css_class = "aegis" if role == "AEGIS" else "user"
            display_name = "🛡️ AEGIS" if role == "AEGIS" else "You"
            st.markdown(f"""
            <div class="aegis-msg {css_class}">
                <strong>{display_name}:</strong> {content}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("aegis_chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Chat about trading, strategy, or the platform...",
                key="aegis_input",
                placeholder="Ask about Catalyst AEGIS features, trading, or your performance 📊"
            )
            submitted = st.form_submit_button("Send 💬", use_container_width=True)
            
            if submitted and user_input and user_input.strip():
                user_msg = user_input.strip()
                st.session_state.aegis_messages.append(("You", user_msg))
                
                recent = [(r, c) for r, c in st.session_state.aegis_messages[-6:]]
                
                with st.spinner("AEGIS is thinking..."):
                    response = query_aegis(user_msg, recent)
                
                st.session_state.aegis_messages.append(("AEGIS", response))
                
                if len(st.session_state.aegis_messages) > 30:
                    st.session_state.aegis_messages = st.session_state.aegis_messages[-30:]
                
                st.rerun()
