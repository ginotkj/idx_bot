import streamlit as st
import pandas as pd
from yahooquery import Ticker
import plotly.express as px

st.set_page_config(page_title="IDX Stock Engine", layout="wide")
st.title("🏛️ IDX Stock Engine")

# DATA FETCHING ENGINE
@st.cache_data(ttl=3600)
def get_idx_data(tickers_str):
    try:
        # Clean input and add .JK suffix if missing
        clean = [s.strip().upper() for s in tickers_str.split(',')]
        symbols = [s if s.endswith('.JK') else s + '.JK' for s in clean]
        
        t = Ticker(symbols, asynchronous=True)
        df = t.history(period="1y")
        
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df.reset_index()
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# INTERFACE
user_input = st.sidebar.text_input("Enter IDX Tickers (comma separated)", "BBCA, BMRI, TLKM")

if st.sidebar.button("Fetch Data"):
    data = get_idx_data(user_input)
    
    if data is not None:
        st.success("Data loaded successfully!")
        
        # Latest Prices Table
        latest = data.sort_values('date').groupby('symbol').tail(1)
        st.subheader("Latest Market Snapshot")
        st.dataframe(latest[['symbol', 'date', 'close', 'volume']], use_container_width=True)
        
        # Price Chart
        st.subheader("Price Trend (1 Year)")
        fig = px.line(data, x='date', y='close', color='symbol')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found. Please check ticker symbols.")
