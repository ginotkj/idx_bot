import streamlit as st
import pandas as pd

# 1. TRAP ERRORS FOR MISSING LIBRARIES
try:
    from yahooquery import Ticker
    import pandas_ta as ta
    import plotly.express as px
    READY = True
except ImportError as e:
    READY = False
    MISSING_LIB = str(e)

st.set_page_config(page_title="IDX Resilience Engine", layout="wide")

if not READY:
    st.error(f"🚨 System is still setting up. Missing: {MISSING_LIB}")
    st.info("Please wait 1-2 minutes for the requirements to finish and refresh.")
    st.stop()

# 2. APP LOGIC
st.title("🏛️ IDX Resilience Engine")

@st.cache_data(ttl=600)
def get_data(tickers):
    try:
        syms = [s.strip().upper() + '.JK' for s in tickers.split(',')]
        t = Ticker(syms, asynchronous=True)
        hist = t.history(period="1y")
        if isinstance(hist, pd.DataFrame) and not hist.empty:
            hist = hist.dropna(subset=['close'])
            return hist, t.get_modules(['summaryProfile'])
    except:
        pass
    return None, {}

query = st.sidebar.text_input("Tickers", "BBCA, BMRI, TLKM")
if st.sidebar.button("Analyze"):
    hist, mods = get_data(query)
    if hist is not None:
        results = []
        for s in hist.index.get_level_values(0).unique():
            df = hist.loc[s].copy()
            df.ta.rsi(append=True)
            rsi_col = [c for c in df.columns if 'RSI' in c][0]
            
            results.append({
                "Ticker": s.replace(".JK",""),
                "Price": df['close'].iloc[-1],
                "RSI": round(df[rsi_col].iloc[-1], 2)
            })
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        fig = px.line(hist.reset_index(), x='date', y='close', color='symbol')
        st.plotly_chart(fig, use_container_width=True)
