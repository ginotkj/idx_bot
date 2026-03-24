import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import numpy as np

st.set_page_config(page_title="IDX Insight Engine", layout="wide")

# 1. DEFENSIVE DATA FETCHING
@st.cache_data(ttl=1200) # Cache for 20 mins to stay under the radar
def get_data_safe(symbols_str):
    try:
        raw = [s.strip().upper() for s in symbols_str.split(',')]
        syms = [s + ('' if s.endswith('.JK') else '.JK') for s in raw]
        t = Ticker(syms, asynchronous=True)
        
        hist = t.history(period="1y")
        # If Yahoo returns an error message instead of a DataFrame
        if hist is None or (isinstance(hist, dict) and not hist) or (isinstance(hist, pd.DataFrame) and hist.empty):
            return None, None
            
        try:
            mods = t.get_modules(['summaryDetail', 'financialData'])
        except:
            mods = {}
            
        return hist, mods
    except Exception:
        return None, None

# 2. UI ELEMENTS
st.title("🏛️ IDX Insight Engine")

if st.sidebar.button("🔄 Force Reset Connection"):
    st.cache_data.clear()
    st.rerun()

manual_input = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
run_btn = st.sidebar.button("Run Deep Analysis")

if run_btn:
    with st.spinner("Bypassing rate limits..."):
        history, modules = get_data_safe(manual_input)

        if history is None:
            st.error("🛑 Yahoo Finance is currently blocking requests from this server.")
            st.info("Wait 5-10 minutes for the block to lift, or try the 'Force Reset' button.")
        else:
            summary_list = []
            available = history.index.get_level_values(0).unique()
            
            for s in available:
                # FIX: Immediately drop rows with no price to prevent 'nan'
                df = history.loc[s].copy().dropna(subset=['close'])
                if len(df) < 10: continue

                # FIX: Safeguard against NoneType objects
                info = modules.get(s, {}) if isinstance(modules, dict) else {}
                if not isinstance(info, dict): info = {}
                
                fin = info.get('financialData', {}) if isinstance(info.get('financialData'), dict) else {}
                
                price = df.iloc[-1]['close']
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                
                # Tech Indicators
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col and pd.notna(df.iloc[-1][rsi_col[0]]) else 50
                
                rec = "Wait for Dip ⏳"
                if rsi_val < 35: rec = "BUY 🚀"
                elif rsi_val > 70: rec = "SELL 📉"

                summary_list.append({
                    "Stock": s.replace(".JK", ""),
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "Recommendation": rec,
                    "Target (+10%)": f"{price*1.1:,.0f}"
                })

            if summary_list:
                st.subheader("📋 Execution Strategy")
                st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
            else:
                st.warning("No valid data could be parsed for these symbols.")
