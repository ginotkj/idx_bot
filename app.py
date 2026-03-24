import streamlit as st
import pandas as pd

# Protection against missing libraries
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    READY = True
except ImportError:
    READY = False

st.set_page_config(page_title="IDX Resilience Pro", layout="wide")

if not READY:
    st.error("🚨 System Error: Libraries missing. Check requirements.txt.")
    st.stop()

@st.cache_data(ttl=600)
def fetch_idx(stocks_str):
    try:
        syms = [s.strip().upper() + '.JK' for s in stocks_str.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        # Fix for 'nan': drop rows with no close price
        if isinstance(hist, pd.DataFrame): hist = hist.dropna(subset=['close'])
        return hist, t.get_modules(['summaryProfile'])
    except:
        return None, {}

st.title("🏛️ IDX Resilience Pro")
query = st.sidebar.text_input("Tickers", "BBCA, BMRI, TLKM, ASII")

if st.sidebar.button("Analyze"):
    hist, mods = fetch_idx(query)
    if hist is None or hist.empty:
        st.warning("Yahoo Finance blocked the request. Try again in 5 mins.")
    else:
        results = []
        for s in hist.index.get_level_values(0).unique():
            df = hist.loc[s]
            # Fix for 'Unknown Sector'
            sector = mods.get(s, {}).get('summaryProfile', {}).get('sector', 'IDX Stock')
            price = df.iloc[-1]['close']
            df.ta.rsi(append=True)
            rsi = df.iloc[-1].filter(like='RSI').iloc[0]
            
            results.append({"Stock": s, "Sector": sector, "Price": f"{price:,.0f}", "RSI": f"{rsi:.1f}"})
        st.table(pd.DataFrame(results))
