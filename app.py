import streamlit as st
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.express as px
import os
import requests
from curl_cffi import requests as cffi_requests

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")
st.title("🏛️ IDX Resilience Engine")

# --- 1. YOUR TELEGRAM REBALANCING LOGIC ---
def check_for_rebalancing():
    TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN")
    CHAT_ID = st.secrets.get("CHAT_ID")
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        st.sidebar.error("Telegram credentials missing in Secrets!")
        return

    session = cffi_requests.Session(impersonate="chrome")
    url = "https://www.idx.co.id/en/news/announcement"
    
    try:
        msg = (
            "🔍 <b>IDX Rebalancing Reminder</b>\n\n"
            "The IDX updates indices in late Jan, Apr, July, and Oct.\n"
            "Check <a href='https://www.idx.co.id/en/news/announcement'>IDX</a> "
            "to see if your ticker list needs an update."
        )
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
        st.sidebar.success("Telegram Alert Sent!")
    except Exception as e:
        st.sidebar.error(f"Telegram Failed: {e}")

# --- 2. DATA FETCHING ENGINE ---
@st.cache_data(ttl=3600)
def get_idx_data(tickers_str):
    try:
        clean = [s.strip().upper() for s in tickers_str.split(',')]
        symbols = [s if s.endswith('.JK') else s + '.JK' for s in clean]
        t = Ticker(symbols, asynchronous=True)
        df = t.history(period="1y")
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df, t.get_modules(['summaryProfile'])
    except:
        return None, None

# --- 3. INTERFACE ---
st.sidebar.header("Controls")
user_input = st.sidebar.text_input("IDX Tickers", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Run Market Analysis"):
    hist, mods = get_idx_data(user_input)
    if hist is not None:
        results = []
        for s in hist.index.get_level_values(0).unique():
            df = hist.loc[s].copy()
            df.ta.rsi(append=True)
            rsi_col = [c for c in df.columns if 'RSI' in c][0]
            
            # Extract sector from the modules we fetched
            info = mods.get(s, {}) if isinstance(mods, dict) else {}
            sector = info.get('summaryProfile', {}).get('sector', 'IDX Listed')

            results.append({
                "Ticker": s.replace(".JK",""),
                "Sector": sector,
                "Price": f"{df['close'].iloc[-1]:,.0f}",
                "RSI": round(df[rsi_col].iloc[-1], 1)
            })
        
        st.subheader("Advanced Market Snapshot")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        
        fig = px.line(hist.reset_index(), x='date', y='close', color='symbol', title="1-Year Trend")
        st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
if st.sidebar.button("Send Telegram Rebalance Alert"):
    check_for_rebalancing()
