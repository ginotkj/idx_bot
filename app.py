import streamlit as st
import pandas as pd

# 1. SAFETY IMPORTS
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    READY = True
except ImportError:
    READY = False

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")

if not READY:
    st.error("🚨 System Error: Libraries are still installing. Please wait 2 minutes and Refresh.")
    st.stop()

# 2. DATA ENGINE
@st.cache_data(ttl=600)
def fetch_data(tickers_str):
    try:
        syms = [s.strip().upper() + '.JK' for s in tickers_str.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        
        # FIX: Drop empty rows to prevent 'nan' results
        if isinstance(hist, pd.DataFrame): 
            hist = hist.dropna(subset=['close'])
            
        return hist, t.get_modules(['summaryProfile'])
    except:
        return None, {}

# 3. UI
st.title("🏛️ IDX Resilience Engine")
query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Analysis"):
    with st.spinner("Accessing IDX Data..."):
        hist, mods = fetch_data(query)
        if hist is None or hist.empty:
            st.warning("Yahoo Finance is blocking requests. Please wait 5 mins.")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s]
                
                # FIX: Sector fallback for 'Unknown Sector' error
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
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
