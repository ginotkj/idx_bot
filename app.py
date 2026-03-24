import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import numpy as np

st.set_page_config(page_title="IDX Master Terminal", layout="wide")

# --- 1. DATA ENGINE WITH ERROR PROTECTION ---
@st.cache_data(ttl=900) # Cache for 15 mins to avoid Yahoo bans
def get_idx_data(symbols_str):
    try:
        raw_list = [s.strip().upper() for s in symbols_str.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        
        t = Ticker(symbols, asynchronous=True)
        history = t.history(period="1y")
        
        # Check if Yahoo returned data or a "Too Many Requests" block
        if history is None or (isinstance(history, pd.DataFrame) and history.empty):
            return None, None
            
        try:
            modules = t.get_modules(['summaryDetail', 'financialData'])
        except:
            modules = {}
            
        return history, modules
    except Exception:
        return None, None

# --- 2. THE INTERFACE ---
st.title("🏛️ IDX Master Trading Terminal")

if st.sidebar.button("🔄 Reset Connection"):
    st.cache_data.clear()
    st.rerun()

user_input = st.sidebar.text_input("Stocks (e.g., BBCA, BMRI)", "BBCA, BMRI, TLKM, ASII")
analyze = st.sidebar.button("Run Analysis")

if analyze:
    with st.spinner("🔍 Fetching live IDX data..."):
        hist, mods = get_idx_data(user_input)

        if hist is None:
            st.error("🛑 Yahoo Finance Connection Failed.")
            st.warning("Yahoo is currently rate-limiting this server. Please wait 5 minutes.")
        else:
            final_table = []
            symbols_found = hist.index.get_level_values(0).unique()
            
            for s in symbols_found:
                # FIX: Drop rows with no price to prevent 'nan'
                df = hist.loc[s].copy().dropna(subset=['close'])
                if len(df) < 20: continue

                # FIX: Protection against NoneType 'info'
                info = {}
                if isinstance(mods, dict):
                    raw_info = mods.get(s, {})
                    info = raw_info if isinstance(raw_info, dict) else {}

                # Get fundamentals safely
                fin = info.get('financialData', {}) if isinstance(info.get('financialData'), dict) else {}
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                
                # Technical Analysis
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col and pd.notna(df.iloc[-1][rsi_col[0]]) else 50
                
                # Recommendation Logic
                if rsi_val < 35: rec = "BUY 🚀"
                elif rsi_val > 70: rec = "SELL 📉"
                else: rec = "Wait ⏳"

                final_table.append({
                    "Stock": s.replace(".JK", ""),
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "ROE %": f"{roe:.1f}%",
                    "Verdict": rec,
                    "Target (+10%)": f"{price * 1.10:,.0f}"
                })

            if final_table:
                st.subheader("📊 Market Analysis Result")
                st.dataframe(pd.DataFrame(final_table), use_container_width=True, hide_index=True)
            else:
                st.info("No data could be processed. Try different symbols.")
