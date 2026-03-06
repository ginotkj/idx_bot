import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Insight Engine Pro", layout="wide")

# --- 1. THE "FORCE REFRESH" TOOL ---
if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
    st.success("Cache Cleared! Running live analysis...")

# --- 2. CACHED DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_stock_data_pro(symbol_string):
    try:
        raw_list = [s.strip().upper() for s in symbol_string.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        
        t = Ticker(symbols, asynchronous=True)
        
        # Fetching History + Fundamentals in one go
        history = t.history(period="1y")
        modules = t.get_modules(['summaryDetail', 'financialData', 'summaryProfile'])
        
        return history, modules
    except Exception as e:
        return str(e), None

# 3. LANGUAGE & BENCHMARKS
lang_data = {
    "English": {
        "title": "🏛️ IDX Insight Engine Pro",
        "tech": "Technical & Foreign Flow", "fund": "Fundamental & Competitiveness",
        "wait": "Wait for Dip ⏳", "buy_col": "Buy Price (Entry)", "summary": "📋 Execution Strategy"
    },
    "Bahasa Indonesia": {
        "title": "🏛️ Mesin Insight IDX Pro",
        "tech": "Teknikal & Sentimen Asing", "fund": "Fundamental & Daya Saing",
        "wait": "Tunggu Dip ⏳", "buy_col": "Harga Beli (Entry)", "summary": "📋 Strategi Eksekusi"
    }
}

INDUSTRY_AVGS = {
    "Financial": [15.8, 14.5], "Technology": [35.2, 5.0],
    "Energy": [8.5, 18.2], "Consumer Defensive": [14.2, 16.5],
    "Infrastructures": [12.5, 10.2], "Default": [12.0, 10.0]
}

selected_lang = st.sidebar.selectbox("Language", ["English", "Bahasa Indonesia"])
L = lang_data[selected_lang]

st.title(L["title"])
input_symbols = st.sidebar.text_input("Stock Symbols", "BBCA, BMRI, TLKM, ASII, ADRO")
analyze_btn = st.sidebar.button("Run Deep Analysis")

if analyze_btn:
    with st.spinner('Calculating technicals & fundamental scores...'):
        history, modules = get_stock_data_pro(input_symbols)

        if isinstance(history, str):
            st.error(f"Connection Issue: {history}")
        else:
            summary_list = []
            
            # Loop through each symbol in the results
            for symbol_jk in history.index.levels[0]:
                df = history.loc[symbol_jk].copy()
                info = modules.get(symbol_jk, {})
                
                # --- TECHNICAL CALCULATIONS ---
                df.ta.rsi(append=True)
                df.ta.sma(length=50, append=True)
                rsi_val = df.iloc[-1].filter(like='RSI').iloc[0]
                sma_val = df.iloc[-1].filter(like='SMA_50').iloc[0]
                price = df.iloc[-1]['close']
                
                # Foreign Flow Proxy
                df['Vol_Sent'] = (df['close'] - df['open']) * df['volume']
                f_flow = "Accumulation 🟢" if df['Vol_Sent'].tail(5).sum() > 0 else "Distribution 🔴"
                
                # Recommendation Logic
                if rsi_val < 35: rec = "BUY 🚀"
                elif rsi_val > 65: rec = "SELL 📉"
                else: rec = L["wait"]

                # --- FUNDAMENTAL DATA ---
                summ = info.get('summaryDetail', {})
                fin = info.get('financialData', {})
                prof = info.get('summaryProfile', {})
                
                sector = prof.get('sector', 'Default')
                pe = summ.get('trailingPE', 0)
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                bench = INDUSTRY_AVGS.get(next((k for k in INDUSTRY_AVGS if k in sector), "Default"))

                # --- UI: SUMMARY TABLE ---
                summary_list.append({
                    "Stock": symbol_jk.replace(".JK", ""), "Price": f"{price:,.0f}",
                    "Recommendation": rec, "RSI": f"{rsi_val:.1f}", 
                    L["buy_col"]: f"{min(sma_val, price*0.97):,.0f}"
                })

                # --- UI: DETAILED REPORTS ---
                st.subheader(f"🔍 {symbol_jk} ({sector})")
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(f"### 📈 {L['tech']}")
                        st.write(f"**Trend:** {'Bullish 🔼' if price > sma_val else 'Bearish 🔽'}")
                        st.write(f"**Foreign Flow:** {f_flow}")
                        st.info(f"Verdict: **{rec}**")
                with c2:
                    with st.container(border=True):
                        st.markdown(f"### 🏢 {L['fund']}")
                        st.write(f"**P/E Ratio:** {pe:.1f}x (Avg: {bench[0]}x)")
                        st.write(f"**ROE:** {roe:.1f}% (Avg: {bench[1]}%)")
                        st.success(f"**Quality:** {'Elite 💪' if roe > bench[1] else 'Standard'}")

            st.divider()
            st.subheader(L["summary"])
            st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
