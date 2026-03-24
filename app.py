import streamlit as st
import pandas as pd
import numpy as np

# 1. IMPORT PROTECTION
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    READY = True
except ImportError:
    READY = False

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")

# 2. FAIL-SAFE DATA FETCHING
@st.cache_data(ttl=600)
def get_clean_data(tickers_str):
    try:
        raw = [s.strip().upper() for s in tickers_str.split(',')]
        syms = [s + ('' if s.endswith('.JK') else '.JK') for s in raw]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        
        if hist is None or (isinstance(hist, pd.DataFrame) and hist.empty):
            return None, {}
        
        try:
            # Fetch sector and financial data
            mods = t.get_modules(['summaryProfile', 'financialData'])
        except:
            mods = {}
        return hist, mods
    except:
        return None, {}

# 3. UI ENGINE
st.title("🏛️ IDX Resilience Engine")

if not READY:
    st.error("🚨 System Error: Libraries missing. Please check requirements.txt.")
    st.stop()

query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
if st.sidebar.button("Run Analysis"):
    with st.spinner("Accessing Market..."):
        hist, mods = get_clean_data(query)

        if hist is None:
            st.warning("⚠️ Yahoo is rate-limiting. Please wait 5 minutes.")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                # FIX: Remove ghost rows that cause 'nan'
                df = hist.loc[s].copy().dropna(subset=['close'])
                if len(df) < 10: continue

                # FIX: Sector handling
                info = mods.get(s, {}) if isinstance(mods, dict) else {}
                sector = info.get('summaryProfile', {}).get('sector', 'N/A')
                
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                
                results.append({
                    "Stock": s.replace(".JK", ""),
                    "Sector": sector,
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "Verdict": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            
            if results:
                st.table(pd.DataFrame(results))
