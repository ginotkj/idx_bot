import streamlit as st
import pandas as pd
import numpy as np

# Try to import yahooquery; if it fails, show a clear error instead of crashing
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    YQ_AVAILABLE = True
except ImportError:
    YQ_AVAILABLE = False

st.set_page_config(page_title="IDX Insight Engine", layout="wide")

if not YQ_AVAILABLE:
    st.error("🚨 System Error: Libraries not installed. Please check your requirements.txt and reboot the app.")
    st.stop()

@st.cache_data(ttl=600)
def get_data(symbols_str):
    try:
        raw = [s.strip().upper() for s in symbols_str.split(',')]
        syms = [s + ('' if s.endswith('.JK') else '.JK') for s in raw]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        
        if hist is None or (isinstance(hist, pd.DataFrame) and hist.empty):
            return None
        return hist
    except Exception:
        return None

st.title("🏛️ IDX Insight Engine")
input_stocks = st.sidebar.text_input("Symbols", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Deep Analysis"):
    with st.spinner("Bypassing Yahoo Rate Limits..."):
        history = get_data(input_stocks)

        if history is None:
            st.error("🛑 Yahoo Finance is currently blocking requests. Please try again in 5 minutes.")
        else:
            summary = []
            for s in history.index.get_level_values(0).unique():
                # FIX: Remove empty rows to prevent 'nan'
                df = history.loc[s].copy().dropna(subset=['close'])
                if len(df) < 20: continue

                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col else 50
                
                summary.append({
                    "Stock": s.replace(".JK", ""),
                    "Price": f"{price:,.0f}" if pd.notna(price) else "N/A",
                    "RSI": round(rsi_val, 1),
                    "Verdict": "BUY 🚀" if rsi_val < 35 else "Wait ⏳"
                })

            if summary:
                st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
            else:
                st.warning("No data found for these symbols.")
