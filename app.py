import streamlit as st
import pandas as pd

# 1. FAIL-SAFE IMPORTS
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    READY = True
except ImportError:
    READY = False

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")

if not READY:
    st.error("🚨 System Update: Libraries are still installing. Please wait 2-3 minutes and refresh.")
    st.stop()

# 2. DATA ENGINE
@st.cache_data(ttl=600)
def fetch_data(tickers_str):
    try:
        syms = [s.strip().upper() + '.JK' for s in tickers_str.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        
        # Drop empty rows to prevent 'nan' prices
        if isinstance(hist, pd.DataFrame): 
            hist = hist.dropna(subset=['close'])
            
        return hist, t.get_modules(['summaryProfile'])
    except:
        return None, {}

# 3. INTERFACE
st.title("🏛️ IDX Resilience Engine")
query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Analysis"):
    with st.spinner("Fetching Market Data..."):
        hist, mods = fetch_data(query)
        if hist is None or hist.empty:
            st.warning("Yahoo Finance is temporarily busy. Wait 5 mins.")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s]
                # Fallback for sector information
                info = mods.get(s, {}) if isinstance(mods, dict) else {}
                sector = info.get('summaryProfile', {}).get('sector', 'IDX Listed')
                
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                
                results.append({
                    "Stock": s.replace(".JK", ""), 
                    "Sector": sector, 
                    "Price": f"{price:,.0f}", 
                    "RSI": f"{rsi_val:.1f}",
                    "Status": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
