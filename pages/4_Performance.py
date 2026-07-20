import streamlit as st
import pandas as pd
import os, base64, json
from user_analytics import get_personal_metrics

st.set_page_config(page_title="Performance", page_icon="📈", layout="wide")

user = st.session_state.get('user')
is_verified = user and user.get('verified', False) if user else False

st.title("📈 Performance & Reports")

tab1, tab2, tab3, tab4 = st.tabs(["Platform Results", "My Analytics", "Download Reports", "Custom Backtest"])

with tab1:
    st.subheader("📊 Catalyst AEGIS Backtest Results")
    perf = pd.DataFrame({
        "Asset":["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","BTC/USD","ETH/USD","BNB/USD","SOL/USD"],
        "Win Rate":["100.0%","68.6%","70.7%","71.9%","68.1%","70.0%","94.4%","82.8%","72.4%","78.9%"],
        "Return":["+0.72%","+0.43%","+87.14%","+0.20%","+80.00%","+130.76%","+1.71%","+0.13%","+0.01%","+0.10%"]
    })
    st.dataframe(perf, use_container_width=True, hide_index=True)
    c1,c2,c3=st.columns(3)
    c1.metric("Avg Win Rate","77.8%"); c2.metric("Combined Return","+301.2%"); c3.metric("P&L ($10k)","+$30,121")

with tab2:
    st.subheader("📊 My Personal Analytics")
    
    if not is_verified:
        st.warning("🔒 Sign up and verify to see your personal analytics.")
    else:
        metrics = get_personal_metrics()
        
        if metrics['total_trades'] == 0:
            st.info("No trades yet. Start trading to see your analytics.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Trades", metrics['total_trades'])
            with col2: st.metric("Win Rate", f"{metrics['win_rate']}%")
            with col3: st.metric("Total P&L", f"${metrics['total_pnl']:+,.2f}")
            with col4: st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Avg Win", f"${metrics['avg_win']:+,.2f}")
            with col2: st.metric("Avg Loss", f"${metrics['avg_loss']:+,.2f}")
            with col3: st.metric("Best Trade", f"${metrics['best_trade']:+,.2f}")
            with col4: st.metric("Max Drawdown", f"{metrics['max_drawdown']}%")
            
            st.markdown("---")
            st.subheader("Win Rate by Asset")
            if metrics['win_rate_by_asset']:
                wr_data = []
                for asset, data in metrics['win_rate_by_asset'].items():
                    wr_data.append({
                        "Asset": asset,
                        "Trades": data['trades'],
                        "Win Rate": f"{data['win_rate']:.1f}%",
                        "P&L": f"${data['pnl']:+,.2f}"
                    })
                st.dataframe(pd.DataFrame(wr_data), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("Monthly Returns")
            if metrics['monthly_returns']:
                mr_data = pd.DataFrame(metrics['monthly_returns'])
                mr_data.columns = ["Month", "P&L"]
                st.dataframe(mr_data, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("📥 Download Reports")
    if os.path.exists("reports"):
        for f in sorted(os.listdir("reports"),reverse=True):
            with open(os.path.join("reports",f),"rb") as fp: data=fp.read()
            b64=base64.b64encode(data).decode()
            if is_verified:
                st.markdown(f"📄 **{f}** — <a href='data:application/pdf;base64,{b64}' download='{f}'>Download PDF</a>", unsafe_allow_html=True)
            else:
                st.markdown(f"📄 **{f}** — 🔒 Sign up to download")
    if is_verified:
        if st.button("Generate New Report", type="primary"):
            import subprocess; subprocess.run(["python","reporting_engine.py"]); st.success("Report generated!")

with tab4:
    st.subheader("🧪 Custom Strategy Backtest")
    st.info("🚀 Coming soon: Upload your own strategy parameters and backtest against historical data.")
    st.markdown("""
    This feature will allow you to:
    - Define custom entry/exit rules
    - Select specific assets to test
    - Run backtests against 6+ months of data
    - Compare performance against Catalyst AEGIS default strategy
    - Export results as PDF
    """)

from mobile_css import add_mobile_css
add_mobile_css()
from aegis_chat import render_chat
render_chat()
