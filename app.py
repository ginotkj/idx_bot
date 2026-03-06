import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import time

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Insight Engine 2026", layout="wide")

# --- 1. CACHED DATA FETCHING (Prevents Rate Limits) ---
@st.cache_data(ttl=3600) # Only fetches new data once per hour
def get_stock_data(symbols):
    try:
        # yahooquery handles IDX suffixes automatically
        formatted_symbols = [s.strip().upper() + ('' if s.strip().upper().endswith('.JK') else '.JK') for s in symbols]
        t = Ticker(formatted_symbols, asynchronous=True)
        
        # Get History & Info
        history = t.history(period="1y")
        info = t.summary_detail
        
        return history, info
    except Exception as e:
        return str(e), None

# 2. LANGUAGE DATA
lang_data = {
    "English": {
        "title": "🏛️ IDX Insight Engine (v3)",
        "symbol_label": "Stock Symbols",
        "summary": "📋 Execution Strategy",
        "wait_msg": "Wait for Dip ⏳",
        "buy_col": "Buy Price",
        "analysis_btn": "Run Deep Analysis"
    },
    "Bahasa Indonesia": {
        "title": "🏛️ Mesin Insight IDX (v3)",
        "symbol_label": "Simbol Saham",
        "summary": "📋 Strategi Eksekusi",
        "wait_msg": "Tunggu Dip ⏳",
        "buy_col": "Harga Beli",
        "analysis_btn": "Jalankan Analisis"
    }
}

selected_lang = st.sidebar.selectbox("Language / Bahasa", ["English", "Bahasa Indonesia"])
L = lang_data[selected_lang]

st.title(L["title"])
input_symbols = st.sidebar.text_input(L["symbol_label"], "BBCA, BMRI, TLKM, ASII")
analyze_btn = st.sidebar.button(L["analysis_btn"])

if analyze_btn:
    with st.spinner('Accessing IDX Servers...'):
        symbol_list = input_symbols.split(',')
        history, info = get_stock_data(symbol_list)

        if isinstance(history, str):
            st.error(f"⚠️ Connection Error: {history}. Please wait 15 mins.")
        else:
            summary_table = []
            
            for symbol_jk in history.index.levels[0]:
                df = history.loc[symbol_jk].copy()
                
                # Technicals
                df.ta.rsi(append=True)
                df.ta.sma(length=50, append=True)
                
                price = df.iloc[-1]['close']
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                sma_val = df.iloc[-1].filter(like='SMA').iloc[0]

                # Simple Logic
                if rsi_val < 35: rec = "BUY 🚀"
                elif rsi_val > 65: rec = "SELL 📉"
                else: rec = L["wait_msg"]

                summary_table.append({
                    "Stock": symbol_jk.replace(".JK", ""),
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "Recommendation": rec,
                    "Buy Price Target": f"{sma_val:,.0f}"
                })

            st.subheader(L["summary"])
            st.dataframe(pd.DataFrame(summary_table), use_container_width=True, hide_index=True)
            st.success("Analysis complete. Data cached for 60 minutes to prevent blocks.")
