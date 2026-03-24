import streamlit as st
import pandas as pd

# 1. FAIL-SAFE IMPORTS
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    READY = True
except ImportError:
    READY = False

st.set_page_config(page_title="IDX Resilience Pro", layout="wide")

if not READY:
    st.error("🚨 Libraries are still installing. Please check 'Manage App' logs.")
    st.stop()

# 2. ROBUST DATA ENGINE
@st.cache_data(ttl=600)
def fetch_idx_data(tickers_str):
    try:
        syms = [s.strip().upper() + '.JK' for s in tickers_str.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        
        # FIX: Drop empty rows to prevent 'nan' prices
        if isinstance(hist, pd.DataFrame): 
            hist = hist.dropna(subset=['close'])
            
        return hist, t.get_modules(['summaryProfile'])
    except:
        return None, {}

# 3. INTERFACE
st.title("🏛️ IDX Resilience Pro")
query = st.sidebar.text_input("Enter Tickers", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Analysis"):
    with st.spinner("Accessing IDX Terminal..."):
        hist, mods = fetch_idx_data(query)
        
        if hist is None or hist.empty:
            st.warning("Yahoo Finance is temporarily blocking requests. Wait 5 mins.")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s]
                if len(df) < 10: continue

                # FIX: Sector fallback to prevent '(Unknown Sector)'
                info = mods.get(s, {}) if isinstance(mods, dict) else {}
                sector = info.get('summaryProfile', {}).get('sector', 'Listed Stock')
                
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                
                results.append({
                    "Stock": s.replace(".JK", ""), 
                    "Sector": sector, 
                    "Price": f"{price:,.0f}", 
                    "RSI": f"{rsi_val:.1f}",
                    "Action": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
