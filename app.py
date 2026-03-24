import subprocess
import sys
import streamlit as st

# 1. AUTOMATIC INSTALLER (Adds Plotly)
def install_dependencies():
    try:
        import yahooquery
        import pandas_ta
        import plotly
    except ImportError:
        # We add plotly here to fix the 'No module named plotly' error
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "yahooquery==2.3.7", 
            "pandas-ta==0.3.14b0", 
            "plotly==5.18.0"
        ])
        st.rerun()

install_dependencies()

# 2. APP IMPORTS
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="IDX Resilience Pro", layout="wide")
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
query = st.sidebar.text_input("Enter Tickers", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Analysis"):
    with st.spinner("Analyzing Market..."):
        hist, mods = fetch_idx_data(query)
        
        if hist is None or hist.empty:
            st.warning("Data source busy. Please try again.")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s]
                sector = mods.get(s, {}).get('summaryProfile', {}).get('sector', 'IDX Listed')
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi = df.iloc[-1].filter(like='RSI').iloc[0]
                
                results.append({
                    "Stock": s.replace(".JK", ""), 
                    "Sector": sector, 
                    "Price": f"{price:,.0f}", 
                    "RSI": f"{rsi:.1f}",
                    "Action": "BUY 🚀" if rsi < 35 else "WAIT ⏳"
                })
            
            # Show Table
            st.table(pd.DataFrame(results))
            
            # Simple Plotly Chart as a test
            fig = px.line(hist.reset_index(), x='date', y='close', color='symbol', title="Price Trends")
            st.plotly_chart(fig, use_container_width=True)
