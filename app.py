import subprocess
import sys
import streamlit as st

# FORCE INSTALLATION ON STARTUP
def install_requirements():
    try:
        import yahooquery
        import pandas_ta
    except ImportError:
        # This manually installs the libraries if Streamlit's installer fails
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yahooquery==2.3.7", "pandas-ta==0.3.14b0"])
        st.rerun()

install_requirements()

import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta

st.set_page_config(page_title="IDX Resilience Pro", layout="wide")
st.title("🏛️ IDX Resilience Engine (Fixed)")

@st.cache_data(ttl=600)
def fetch_data(tickers_str):
    try:
        syms = [s.strip().upper() + '.JK' for s in tickers_str.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        if isinstance(hist, pd.DataFrame): hist = hist.dropna(subset=['close'])
        return hist, t.get_modules(['summaryProfile'])
    except:
        return None, {}

query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
if st.sidebar.button("Run Analysis"):
    hist, mods = fetch_data(query)
    if hist is None or hist.empty:
        st.warning("Data source temporarily unavailable. Please retry.")
    else:
        results = []
        for s in hist.index.get_level_values(0).unique():
            df = hist.loc[s]
            sector = mods.get(s, {}).get('summaryProfile', {}).get('sector', 'IDX Listed')
            price = df.iloc[-1]['close']
            df.ta.rsi(append=True)
            rsi = df.iloc[-1].filter(like='RSI').iloc[0]
            results.append({"Stock": s.replace(".JK",""), "Sector": sector, "Price": f"{price:,.0f}", "RSI": f"{rsi:.1f}"})
        st.table(pd.DataFrame(results))
