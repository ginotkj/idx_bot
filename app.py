import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from curl_cffi import requests

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Insight Engine 2026", layout="wide")

# --- BROWSER IMPERSONATION ENGINE ---
# This creates a persistent "Chrome" identity to bypass Yahoo's blocks
if 'session' not in st.session_state:
    st.session_state.session = requests.Session(impersonate="chrome")

# 1. LANGUAGE DATA
lang_data = {
    "English": {
        "title": "🏛️ IDX Insight Engine",
        "symbol_label": "Stock Symbols",
        "tech_header": "Technical & Foreign Sentiment",
        "fund_header": "Fundamental & Competitiveness",
        "summary": "📋 Execution Strategy (Summary Snapshot)",
        "wait_msg": "Wait for Dip ⏳",
        "buy_col": "Buy Price (Entry)",
        "logic_header": "🧠 Analysis Methodology"
    },
    "Bahasa Indonesia": {
        "title": "🏛️ Mesin Insight IDX",
        "symbol_label": "Simbol Saham",
        "tech_header": "Teknikal & Sentimen Asing",
        "fund_header": "Fundamental & Daya Saing",
        "summary": "📋 Strategi Eksekusi (Ringkasan Snapshot)",
        "wait_msg": "Tunggu Dip ⏳",
        "buy_col": "Harga Beli (Entry)",
        "logic_header": "Metodologi Analisis"
    }
}

selected_lang = st.sidebar.selectbox("Language / Bahasa", ["English", "Bahasa Indonesia"])
L = lang_data[selected_lang]

# 2026 Industry Benchmarks
INDUSTRY_AVGS = {
    "Financial": [15.8, 14.5, 0.95], "Technology": [35.2, 5.0, 0.40],
    "Energy": [8.5, 18.2, 0.70], "Consumer Defensive": [14.2, 16.5, 0.82],
    "Infrastructures": [12.5, 10.2, 1.20], "Default": [12.0, 10.0, 0.80]
}

def get_pro_data(symbol):
    try:
        # Pass the impersonated session into yfinance
        ticker = yf.Ticker(symbol, session=st.session_state.session)
        df = ticker.history(period="1y")
        
        if df.empty:
            return "NO_DATA", None, None, None, None
            
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # Calculate Technicals
        df.ta.rsi(append=True)
        df.ta.sma(length=50, append=True)
        rsi_c = [c for c in df.columns if 'RSI' in str(c)][0]
        sma_c = [c for c in df.columns if 'SMA_50' in str(c)][0]
        
        # Foreign Flow Proxy
        df['Vol_Sentiment'] = (df['Close'] - df['Open']) * df['Volume']
        f_flow = "Accumulation 🟢" if df['Vol_Sentiment'].tail(5).sum() > 0 else "Distribution 🔴"
        
        return df, ticker.info, rsi_c, sma_c, f_flow
    except Exception as e:
        return str(e), None, None, None, None

st.title(L["title"])
input_symbols = st.sidebar.text_input(L["symbol_label"], "BBCA, BMRI, TLKM, ASII, ADRO")
has_position = st.sidebar.toggle("I already own these stocks", value=False)
analyze_btn = st.sidebar.button("Run Deep Analysis")

if analyze_btn:
    raw_list = input_symbols.split(',')
    symbols = [s.strip().upper() + ('' if s.strip().upper().endswith('.JK') else '.JK') for s in raw_list]

    summary_list, full_reports = [], []

    for symbol in symbols:
        result, info, rsi_c, sma_c, f_flow = get_pro_data(symbol)
        
        if isinstance(result, str):
            st.warning(f"⚠️ {symbol}: {result if result != 'NO_DATA' else 'No data found'}")
            continue
            
        df = result
        price, rsi_val, sma_val = df.iloc[-1]['Close'], df.iloc[-1][rsi_c], df.iloc[-1][sma_c]
        
        # Logic for Recommendations
        if rsi_val < 35: rec = "BUY 🚀"
        elif rsi_val > 65: rec = "SELL 📉"
        else: rec = "HOLD ✅" if has_position else L["wait_msg"]

        sector = info.get('sector', 'Default')
        sector_key = next((k for k in INDUSTRY_AVGS if k in sector), "Default")
        
        # Table Row
        row = {
            "Stock": symbol.replace(".JK", ""), 
            "Price": f"{price:,.0f}", 
            "Recommendation": rec,
            "Target (+10%)": f"{price * 1.10:,.0f}",
            "Stop Loss (-5%)": f"{price * 0.95:,.0f}"
        }
        if not has_position: row[L["buy_col"]] = f"{min(sma_val, price*0.97):,.0f}"
        summary_list.append(row)
        full_reports.append({"symbol": symbol, "info": info, "rsi": rsi_val, "price": price, "sma": sma_val, "rec": rec, "sector": sector, "bench": INDUSTRY_AVGS[sector_key], "f_flow": f_flow})

    if summary_list:
        st.subheader(L["summary"])
        st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
        st.divider()

        for r in full_reports:
            st.subheader(f"🔍 {r['symbol']} ({r['sector']})")
            cols = st.columns(2) 
            with cols[0]:
                with st.container(border=True):
                    st.markdown(f"### 📈 {L['tech_header']}")
                    st.write(f"**RSI (14):** {r['rsi']:.2f}")
                    st.write(f"**Trend:** {'Bullish 🔼' if r['price'] > r['sma'] else 'Bearish 🔽'}")
                    st.write(f"**Foreign Flow:** {r['f_flow']}")
                    st.info(f"Verdict: **{r['rec']}**")
            with cols[1]:
                with st.container(border=True):
                    st.markdown(f"### 🏢 {L['fund_header']}")
                    pe = r['info'].get('trailingPE', 0)
                    roe = (r['info'].get('returnOnEquity', 0) or 0) * 100
                    st.write(f"**P/E Ratio:** {pe:.1f}x (Avg: {r['bench'][0]}x)")
                    st.write(f"**ROE:** {roe:.1f}% (Avg: {r['bench'][1]}%)")
                    st.success(f"**Quality:** {'Elite 💪' if roe > r['bench'][1] else 'Standard'}")

    with st.expander(L["logic_header"], expanded=True):
        st.markdown("### 📊 Methodology")
        st.write("Calculations use TLS Fingerprinting to ensure reliable data access from Yahoo Finance.")
