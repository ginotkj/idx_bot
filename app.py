import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CRITICAL IMPORT PROTECTION ---
# This prevents the "Oh no" screen if libraries are missing
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False

st.set_page_config(page_title="IDX Master Insight Pro", layout="wide")

# --- 2. THE FAIL-SAFE DATA ENGINE ---
@st.cache_data(ttl=900) # 15-minute cache to prevent Yahoo IP bans
def get_idx_data(symbol_str):
    try:
        # Format symbols for Indonesia Stock Exchange
        raw_list = [s.strip().upper() for s in symbol_str.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        
        t = Ticker(symbols, asynchronous=True)
        history = t.history(period="1y")
        
        # Check if Yahoo returned an empty response or blocked the request
        if history is None or (isinstance(history, pd.DataFrame) and history.empty):
            return None, None
            
        try:
            # Fetch fundamentals safely
            modules = t.get_modules(['summaryDetail', 'financialData', 'summaryProfile'])
        except:
            modules = {}
            
        return history, modules
    except Exception:
        return None, None

# --- 3. MAIN INTERFACE ---
st.title("🏛️ IDX Master Insight Pro")

if not IMPORT_SUCCESS:
    st.error("🚨 System Error: Required libraries (yahooquery, pandas-ta) are not installed.")
    st.info("Please update your requirements.txt and reboot the app in Streamlit Cloud.")
    st.stop()

# Sidebar Controls
st.sidebar.header("Control Panel")
if st.sidebar.button("🔄 Reset Connection"):
    st.cache_data.clear()
    st.rerun()

user_input = st.sidebar.text_input("Enter IDX Tickers (e.g. BBCA, BMRI, ASII)", "BBCA, BMRI, TLKM, ASII")
analyze_btn = st.sidebar.button("Run Deep Analysis")

if analyze_btn:
    with st.spinner("🔍 Scanning Market Data..."):
        hist, mods = get_idx_data(user_input)

        if hist is None:
            st.error("🛑 Yahoo Finance Connection Blocked.")
            st.warning("Yahoo is currently rate-limiting this server. Please wait 5-10 minutes for the block to lift.")
        else:
            summary_results = []
            symbols_present = hist.index.get_level_values(0).unique()
            
            for sym in symbols_present:
                # FIX: Remove rows with no price (prevents 'nan' in table)
                df = hist.loc[sym].copy().dropna(subset=['close'])
                
                # Skip if there isn't enough historical data
                if len(df) < 20:
                    continue

                # FIX: Safeguard against NoneType objects
                info = {}
                if isinstance(mods, dict):
                    raw_info = mods.get(sym, {})
                    info = raw_info if isinstance(raw_info, dict) else {}

                # Extraction of Fundamentals
                fin = info.get('financialData', {}) if isinstance(info.get('financialData'), dict) else {}
                prof = info.get('summaryProfile', {}) if isinstance(info.get('summaryProfile'), dict) else {}
                
                price = df.iloc[-1]['close']
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                sector = prof.get('sector', 'N/A')

                # Technical Analysis (RSI)
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col and pd.notna(df.iloc[-1][rsi_col[0]]) else 50
                
                # Logic Strategy
                if rsi_val < 35:
                    verdict = "BUY 🚀"
                elif rsi_val > 70:
                    verdict = "SELL 📉"
                else:
                    verdict = "WAIT ⏳"

                summary_results.append({
                    "Stock": sym.replace(".JK", ""),
                    "Sector": sector,
                    "Price": f"{price:,.0f}",
                    "RSI (14)": f"{rsi_val:.1f}",
                    "ROE %": f"{roe:.1f}%",
                    "Recommendation": verdict,
                    "Target (+10%)": f"{price * 1.10:,.0f}"
                })

            if summary_results:
                st.subheader("📋 Execution Strategy")
                st.dataframe(pd.DataFrame(summary_results), use_container_width=True, hide_index=True)
            else:
                st.warning("No valid data found for the selected symbols.")

# --- 4. FOOTER ---
st.divider()
st.caption("Data provided by Yahoo Finance. Technical indicators powered by Pandas-TA.")
