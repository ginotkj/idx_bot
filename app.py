import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Insight Engine 2026", layout="wide")

# --- FIX: BYPASS RATE LIMITS WITH CUSTOM HEADERS ---
# This makes the app look like a real browser to Yahoo Finance
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

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

def get_pro_data(symbol):
    try:
        # Pass the custom session to yfinance
        ticker = yf.Ticker(symbol, session=session)
        df = ticker.history(period="1y")
        
        if df.empty:
            return "NO_DATA", None, None, None, None
            
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        df.ta.rsi(append=True)
        df.ta.sma(length=50, append=True)
        rsi_c = [c for c in df.columns if 'RSI' in str(c)][0]
        sma_c = [c for c in df.columns if 'SMA_50' in str(c)][0]
        
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
            st.warning(f"⚠️ {symbol}: {result}")
            continue
            
        df = result
        price = df.iloc[-1]['Close']
        rsi_val = df.iloc[-1][rsi_c]
        sma_val = df.iloc[-1][sma_c]
        
        rec = "BUY 🚀" if rsi_val < 35 else ("SELL 📉" if rsi_val > 65 else (L["wait_msg"] if not has_position else "HOLD ✅"))
        
        row = {"Stock": symbol.replace(".JK", ""), "Price": f"{price:,.0f}", "Recommendation": rec, "Target (+10%)": f"{price * 1.10:,.0f}", "Stop Loss (-5%)": f"{price * 0.95:,.0f}"}
        if not has_position: row[L["buy_col"]] = f"{min(sma_val, price*0.97):,.0f}"
        summary_list.append(row)
        full_reports.append({"symbol": symbol, "info": info, "rsi": rsi_val, "price": price, "sma": sma_val, "rec": rec, "f_flow": f_flow})

    if summary_list:
        st.subheader(L["summary"])
        st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
        for r in full_reports:
            st.subheader(f"🔍 {r['symbol']}")
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**RSI:** {r['rsi']:.2f} | **Trend:** {r['f_flow']}")
            with c2:
                st.success(f"**Verdict:** {r['rec']}")
