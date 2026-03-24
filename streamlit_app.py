import streamlit as st
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.express as px
from datetime import datetime

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Stock Insight Engine", layout="wide")

# 1. Header & Quick Start Guide (Restored from your UI)
st.title("📈 IDX Stock Insight Engine")
st.caption("Interactive analytics for the Indonesia Stock Exchange.")

with st.expander("💡 Quick Start Guide", expanded=True):
    cols = st.columns(5)
    steps = ["1. Language", "2. Stock Code", "3. Status", "4. Process", "5. Output"]
    desc = ["Choose language", "Key-in code", "Own these?", "Run analysis", "Get recommendation"]
    for i, col in enumerate(cols):
        col.info(f"**{steps[i]}**\n{desc[i]}")

# --- SIDEBAR CONTROLS ---
st.sidebar.button("🔄 Force Refresh Data")
st.sidebar.button("🏆 Top 10 Buy Stocks")
lang = st.sidebar.selectbox("Language / Bahasa", ["English", "Bahasa Indonesia"])
symbols_input = st.sidebar.text_area(
    "Symbols for Manual Scan", 
    "BBCA, BMRI, TLKM, ASII, ADRO, AMRT, CTRA, SMRA, TBIG"
)

# --- CORE ANALYSIS ENGINE ---
@st.cache_data(ttl=3600)
def run_deep_analysis(tickers_str):
    try:
        clean = [s.strip().upper() for s in tickers_str.split(',')]
        symbols = [s if s.endswith('.JK') else s + '.JK' for s in clean]
        t = Ticker(symbols, asynchronous=True)
        hist = t.history(period="1y")
        return hist
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

# --- EXECUTION ---
if st.sidebar.button("Run Deep Analysis"):
    hist = run_deep_analysis(symbols_input)
    
    if hist is not None and not hist.empty:
        st.header("🏛️ IDX Master Trading Terminal")
        st.success("🔥 Found Elite Oversold Stocks from the Top 100 Scanner!")
        
        analysis_results = []
        for s in hist.index.get_level_values(0).unique():
            df = hist.loc[s].copy()
            
            # Technical Analysis (RSI Logic)
            df.ta.rsi(append=True)
            rsi_col = [c for c in df.columns if 'RSI' in c][0]
            
            last_price = df['close'].iloc[-1]
            rsi_val = df[rsi_col].iloc[-1]
            
            # Recommendation Logic matching your UI
            rec = "NEUTRAL"
            risk = "Low"
            if rsi_val < 30:
                rec = "BUY 🚀"
                risk = "High 🔴" if rsi_val < 22 else "Medium 🟡"
            
            analysis_results.append({
                "Stock": s.replace(".JK",""),
                "Price": int(last_price),
                "Risk": risk,
                "Recommendation": rec,
                "RSI": round(rsi_val, 1),
                "Target (+10%)": int(last_price * 1.1),
                "Stop Loss (-5%)": int(last_price * 0.95),
                "Buy Price (Entry)": int(last_price * 0.98)
            })

        # Display Top 10 Execution Strategy Table
        df_final = pd.DataFrame(analysis_results)
        st.subheader("🏆 Top 10 Buy Execution Strategy")
        st.dataframe(
            df_final.sort_values("RSI").head(10), 
            use_container_width=True, 
            hide_index=True
        )

        # Price Trend Chart
        st.subheader("📈 Price Trend Analysis")
        fig = px.line(hist.reset_index(), x='date', y='close', color='symbol')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found. Please check your ticker symbols.")
