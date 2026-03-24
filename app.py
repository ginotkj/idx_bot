import streamlit as st
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.express as px

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")
st.title("🏛️ IDX Resilience Engine")

@st.cache_data(ttl=600)
def fetch_data(tickers_str):
    try:
        clean = [s.strip().upper() for s in tickers_str.split(',')]
        syms = [s + ('' if s.endswith('.JK') else '.JK') for s in clean]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        if isinstance(hist, pd.DataFrame): 
            hist = hist.dropna(subset=['close'])
        return hist, t.get_modules(['summaryProfile'])
    except Exception as e:
        return None, str(e)

query = st.sidebar.text_input("Stocks", "BBCA, BMRI, TLKM, ASII")
if st.sidebar.button("Run Analysis"):
    with st.spinner("Fetching IDX Data..."):
        hist, mods = fetch_data(query)
        if hist is None or hist.empty:
            st.error(f"Data Fetch Failed. Error: {mods}")
        else:
            results = []
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s].copy()
                info = mods.get(s, {}) if isinstance(mods, dict) else {}
                sector = info.get('summaryProfile', {}).get('sector', 'IDX Listed')
                df.ta.rsi(append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                price = df.iloc[-1]['close']
                
                results.append({
                    "Stock": s.replace(".JK", ""), 
                    "Sector": sector, 
                    "Price": f"{price:,.0f}", 
                    "RSI": f"{rsi_val:.1f}",
                    "Action": "BUY 🚀" if rsi_val < 35 else "WAIT ⏳"
                })
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
            fig = px.line(hist.reset_index(), x='date', y='close', color='symbol')
            st.plotly_chart(fig, use_container_width=True)
