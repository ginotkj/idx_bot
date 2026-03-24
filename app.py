import subprocess
import sys
import streamlit as st

# 1. MANUAL REPAIR ENGINE
# This runs BEFORE any other imports to fix the "ModuleNotFoundError"
def repair_environment():
    try:
        import yahooquery
        import pandas_ta
        import plotly
    except ImportError:
        # If libraries are missing, we force-install them manually
        with st.spinner("🔧 Technical Setup: Installing market analysis tools..."):
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "pip"
            ])
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "yahooquery==2.3.7", 
                "pandas-ta==0.3.14b0", 
                "plotly==5.18.0"
            ])
        st.rerun()

repair_environment()

# 2. STANDARD IMPORTS
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.express as px

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")
st.title("🏛️ IDX Resilience Engine")

# 3. DATA ENGINE
@st.cache_data(ttl=600)
def fetch_data(tickers_str):
    try:
        clean = [s.strip().upper() for s in tickers_str.split(',')]
        syms = [s + ('' if s.endswith('.JK') else '.JK') for s in clean]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        if isinstance(hist, pd.DataFrame): 
            hist = hist.dropna(subset=['close'])
        return hist, t.get_modules(['summaryProfile'])
    except Exception as e:
        return None, str(e)

# 4. INTERFACE
query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
if st.sidebar.button("Run Analysis"):
    with st.spinner("Downloading IDX Data..."):
        hist, mods = fetch_data(query)
        
        if hist is None or hist.empty:
            st.error(f"Data Fetch Failed. Error: {mods}")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s].copy()
                # Sector lookup
                info = mods.get(s, {}) if isinstance(mods, dict) else {}
                sector = info.get('summaryProfile', {}).get('sector', 'IDX Listed')
                # Tech Analysis
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                price = df.iloc[-1]['close']
                
                results.append({
                    "Stock": s.replace(".JK", ""), 
                    "Sector": sector, 
                    "Price": f"{price:,.0f}", 
                    "RSI": f"{rsi_val:.1f}",
                    "Action": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
            fig = px.line(hist.reset_index(), x='date', y='close', color='symbol', title="Price Trends")
            st.plotly_chart(fig, use_container_width=True)
