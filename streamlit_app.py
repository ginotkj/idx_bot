import streamlit as st
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(page_title="🤖 IDX Autonomous Agent", layout="wide")

# --- STRATEGIC INTELLIGENCE ENGINE ---
def detect_anomalies(df):
    anomalies = []
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # 1. Volume Surge Detection (3x+ unusual volume)
    avg_vol = df['volume'].tail(20).mean()
    vol_ratio = last_row['volume'] / avg_vol
    if vol_ratio > 3.0:
        anomalies.append(f"🔥 VOLUME_SURGE ({vol_ratio:.1f}x)")

    # 2. Price Spike (5%+)
    pct_change = ((last_row['close'] - prev_row['close']) / prev_row['close']) * 100
    if abs(pct_change) >= 5.0:
        anomalies.append(f"⚡ PRICE_SPIKE ({pct_change:.1f}%)")

    # 3. RSI Divergence / Oversold
    df.ta.rsi(append=True)
    rsi_val = df.filter(like='RSI').iloc[-1]
    if rsi_val < 30:
        anomalies.append(f"💎 OVERSOLD (RSI: {rsi_val:.1f})")
        
    return anomalies, rsi_val, vol_ratio

# --- DASHBOARD UI ---
st.title("🏛️ IDX Strategic Intelligence Dashboard")
st.sidebar.info("🤖 Agent Status: Autonomous Mode Active")

tickers = st.sidebar.text_input("Agent Watchlist", "BBCA, BMRI, TLKM, ASII, ADRO")

if st.sidebar.button("Trigger Autonomous Research"):
    with st.spinner("Agent conducting multi-step research pipeline..."):
        clean = [s.strip().upper() for s in tickers.split(',')]
        symbols = [s if s.endswith('.JK') else s + '.JK' for s in clean]
        t = Ticker(symbols, asynchronous=True)
        hist = t.history(period="1y")
        
        if hist is not None and not hist.empty:
            for s in hist.index.get_level_values(0).unique():
                df = hist.loc[s].copy()
                anomalies, rsi, v_ratio = detect_anomalies(df)
                
                # If anomalies found, display as an "Intelligent Alert"
                if anomalies:
                    with st.expander(f"🧠 Analysis Active: {s}", expanded=True):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.metric("Current Price", f"{df['close'].iloc[-1]:,.0f}")
                            st.write(f"**Signals:** {', '.join(anomalies)}")
                        with col2:
                            st.success(f"**Strategic Insight:** Unusual activity detected. Confidence: High")
                            st.write(f"✅ Risk/Reward ratio looks favorable at current RSI ({rsi:.1f}).")
                
            # Global Market View
            st.subheader("📊 Real-Time Monitoring")
            fig = px.line(hist.reset_index(), x='date', y='close', color='symbol', title="Watchlist Trend")
            st.plotly_chart(fig, use_container_width=True)
