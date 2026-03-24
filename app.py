import streamlit as st
import pandas as pd
import numpy as np

# Safety check for libraries
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    READY = True
except ImportError:
    READY = False

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")

@st.cache_data(ttl=600)
def get_market_data(stocks_str):
    try:
        clean = [s.strip().upper() for s in stocks_str.split(',')]
        syms = [s + ('' if s.endswith('.JK') else '.JK') for s in clean]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        
        if hist is None or (isinstance(hist, pd.DataFrame) and hist.empty):
            return "BLOCKED"
        return hist
    except:
        return None

st.title("🏛️ IDX Resilience Engine")

if not READY:
    st.error("🚨 Libraries missing. Please check requirements.txt and Reboot.")
    st.stop()

query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
if st.sidebar.button("Run Analysis"):
    with st.spinner("Fetching Data..."):
        data = get_market_data(query)

        if data == "BLOCKED":
            st.warning("⚠️ Yahoo is rate-limiting the server. Wait 5 mins.")
        elif data is not None:
            results = []
            for s in data.index.get_level_values(0).unique():
                # Fix for 'nan' prices
                df = data.loc[s].copy().dropna(subset=['close'])
                if len(df) < 10: continue

                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                
                results.append({
                    "Stock": s.replace(".JK", ""),
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "Verdict": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            st.table(pd.DataFrame(results))
