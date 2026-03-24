import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DEFENSIVE IMPORTS ---
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    LIB_READY = True
except ImportError:
    LIB_READY = False

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")

# --- 2. DATA ENGINE WITH BLOCK PROTECTION ---
@st.cache_data(ttl=600)
def fetch_idx_data(symbols_str):
    if not LIB_READY:
        return "LIBS_MISSING", None
    try:
        clean_list = [s.strip().upper() for s in symbols_str.split(',')]
        tickers = [s + ('' if s.endswith('.JK') else '.JK') for s in clean_list]
        
        t = Ticker(tickers, asynchronous=True)
        # Fetching only history first as it's the most stable
        hist = t.history(period="1y")
        
        if hist is None or (isinstance(hist, pd.DataFrame) and hist.empty):
            return "YAHOO_BLOCK", None
            
        # Try to get fundamentals, but don't crash if they fail
        try:
            mods = t.get_modules(['financialData'])
        except:
            mods = {}
            
        return hist, mods
    except Exception as e:
        return str(e), None

# --- 3. UI ---
st.title("🏛️ IDX Resilience Engine")

if not LIB_READY:
    st.error("🚨 System Error: Modules not installed. Check your requirements.txt.")
    st.stop()

query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
if st.sidebar.button("Run Analysis"):
    with st.spinner("Accessing IDX Data..."):
        hist_data, modules = fetch_idx_data(query)

        if hist_data == "YAHOO_BLOCK":
            st.warning("⚠️ Yahoo Finance is temporarily blocking this server's IP. Please try again in 10 minutes.")
        elif isinstance(hist_data, str):
            st.error(f"Error: {hist_data}")
        else:
            results = []
            # Get unique stocks from the data we actually received
            found_stocks = hist_data.index.get_level_values(0).unique()
            
            for s in found_stocks:
                # FIX: Remove rows with no price (fixes 'nan' issue)
                df = hist_data.loc[s].copy().dropna(subset=['close'])
                if len(df) < 20: continue

                # Technical Analysis
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col else 50
                
                results.append({
                    "Stock": s.replace(".JK", ""),
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "Verdict": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })

            if results:
                st.table(pd.DataFrame(results))
            else:
                st.info("No valid market data returned.")
