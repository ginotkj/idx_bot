import streamlit as st
import pandas as pd
from yahooquery import Ticker
import pandas_ta as ta
import plotly.express as px
import requests

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")
st.title("🏛️ IDX Resilience Engine")

# --- 1. TELEGRAM NOTIFICATION SYSTEM ---
def send_telegram_alert(message):
    # Using st.secrets for security as seen in your configuration
    token = st.secrets.get("TELEGRAM_TOKEN")
    chat_id = st.secrets.get("CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
        except Exception as e:
            st.error(f"Telegram failed: {e}")

# --- 2. ADVANCED ANALYSIS ENGINE ---
@st.cache_data(ttl=600)
def analyze_stocks(tickers_str):
    try:
        clean = [s.strip().upper() for s in tickers_str.split(',')]
        symbols = [s if s.endswith('.JK') else s + '.JK' for s in clean]
        t = Ticker(symbols, asynchronous=True)
        hist = t.history(period="1y")
        
        # Fetching news for the "News Update" trigger
        news = t.news(5) 
        return hist, news
    except:
        return None, None

# --- 3. DASHBOARD INTERFACE ---
user_input = st.sidebar.text_input("Stocks to Monitor", "BBCA, BMRI, TLKM, ASII")
alert_threshold = st.sidebar.slider("Price Alert Threshold (%)", 1.0, 5.0, 2.0)

if st.sidebar.button("Run Market Engine"):
    hist, news_data = analyze_stocks(user_input)
    
    if hist is not None and not hist.empty:
        results = []
        alert_log = []
        
        for s in hist.index.get_level_values(0).unique():
            df = hist.loc[s].copy()
            df.ta.rsi(append=True)
            
            # PRICE CHANGE LOGIC
            last_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            pct_change = ((last_price - prev_price) / prev_price) * 100
            
            # Trigger Alert if change exceeds threshold
            if abs(pct_change) >= alert_threshold:
                alert_log.append(f"⚠️ <b>{s}</b> Price Shift: {pct_change:.2f}%")

            results.append({
                "Ticker": s.replace(".JK",""),
                "Price": f"{last_price:,.0f}",
                "Change %": f"{pct_change:.2f}%",
                "RSI": round(df.filter(like='RSI').iloc[-1], 1)
            })
            
        # Display Results
        st.subheader("Market Intelligence")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        
        # Send Telegram if alerts triggered
        if alert_log:
            summary = "🚀 <b>IDX Movement Detected</b>\n\n" + "\n".join(alert_log)
            send_telegram_alert(summary)
            st.info("Telegram price alert sent!")

        # News Section
        if news_data:
            st.subheader("Recent Market News")
            for item in news_data[:3]: # Show top 3
                st.write(f"📰 **{item.get('title')}**")
                st.caption(f"Source: {item.get('publisher')} | [Read More]({item.get('link')})")

        fig = px.line(hist.reset_index(), x='date', y='close', color='symbol')
        st.plotly_chart(fig, use_container_width=True)
