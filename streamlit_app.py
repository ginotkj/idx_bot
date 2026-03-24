import subprocess
import sys
import streamlit as st

# 1. FORCED INSTALLER (Bypasses broken Cloud Cache)
def startup_installer():
    try:
        import yahooquery
        import pandas_ta
        import plotly
    except ImportError:
        # This manually forces the installation of all required tools
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "yahooquery==2.3.7", 
            "pandas-ta==0.3.14b0", 
            "plotly==5.18.0"
        ])
        st.rerun()

startup_installer()

# 2. STANDARD IMPORTS
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")
st.title("🏛️ IDX Resilience Engine")

# 3. DATA ENGINE
@st.cache_data(ttl=600)
def fetch_idx_data(tickers_str):
    try:
        syms = [s.strip().upper() + '.JK' for s in tickers_str.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        if isinstance(hist, pd.DataFrame): 
            hist = hist.dropna(subset=['close'])
        return hist, t.get_modules(['summaryProfile'])
    except:
        return None, {}

# 4. INTERFACE
query = st.sidebar.text_input("Enter Tickers (comma separated)", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Analysis"):
    with st.spinner("Fetching Market Data..."):
        hist, mods = fetch_idx_data(query)
        
        if hist is None or hist.empty:
            st.warning("Data source temporarily busy. Please wait 1 minute.")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s]
                # Technical Analysis
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                price = df.iloc[-1]['close']
                
                # Metadata
                info = mods.get(s, {}) if isinstance(mods, dict) else {}
                sector = info.get('summaryProfile', {}).get('sector', 'IDX Listed')
                
                results.append({
                    "Stock": s.replace(".JK", ""), 
                    "Sector": sector, 
                    "Price": f"{price:,.0f}", 
                    "RSI": f"{rsi_val:.1f}",
                    "Action": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            
            # Display Table
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
            
            # Display Chart
            fig = px.line(hist.reset_index(), x='date', y='close', color='symbol', title="IDX Price Trends")
            st.plotly_chart(fig, use_container_width=True)
