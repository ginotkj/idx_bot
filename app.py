import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Master Trading Terminal", layout="wide")

# --- 1. THE "FORCE REFRESH" TOOL ---
if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
    st.success("Cache Cleared! Running live analysis...")

# --- 2. ROBUST DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_stock_data_pro(symbol_string):
    try:
        raw_list = [s.strip().upper() for s in symbol_string.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        
        t = Ticker(symbols, asynchronous=True)
        
        # Fetching History + Fundamental Modules
        history = t.history(period="1y")
        # Added try-except inside for module fetching to be safer
        try:
            modules = t.get_modules(['summaryDetail', 'financialData', 'summaryProfile'])
        except:
            modules = {}
        
        return history, modules
    except Exception as e:
        return str(e), {}

# 3. LANGUAGE & BENCHMARKS
lang_data = {
    "English": {
        "title": "🏛️ IDX Master Trading Terminal",
        "tech": "Technical & Foreign Flow", "fund": "Fundamental & Competitiveness",
        "wait": "Wait for Dip ⏳", "buy_col": "Buy Price (Entry)", "summary": "📋 Execution Strategy"
    },
    "Bahasa Indonesia": {
        "title": "🏛️ Terminal Trading Profesional Master BEI",
        "tech": "Teknikal & Sentimen Asing", "fund": "Fundamental & Daya Saing",
        "wait": "Tunggu Dip ⏳", "buy_col": "Harga Beli (Entry)", "summary": "📋 Strategi Eksekusi"
    }
}

INDUSTRY_AVGS = {
    "Financial": [15.8, 14.5], "Technology": [35.2, 5.0],
    "Energy": [8.5, 18.2], "Consumer Defensive": [14.2, 16.5],
    "Infrastructures": [12.5, 10.2], "Default": [12.0, 10.0]
}

selected_lang = st.sidebar.selectbox("Language / Bahasa", ["English", "Bahasa Indonesia"])
L = lang_data[selected_lang]

st.title(L["title"])
input_symbols = st.sidebar.text_input("Symbols", "BBCA, BMRI, TLKM, ASII, ADRO")
analyze_btn = st.sidebar.button("Run Deep Analysis")

if analyze_btn:
    with st.spinner('Accessing IDX Servers...'):
        history, modules = get_stock_data_pro(input_symbols)

        if isinstance(history, str):
            st.error(f"Connection Issue: {history}")
        elif history is None or history.empty:
            st.warning("No historical data found. Please check symbols or try again later.")
        else:
            summary_list = []
            
            # Use standard loop if index levels aren't as expected
            available_symbols = history.index.get_level_values(0).unique()
            
            for symbol_jk in available_symbols:
                df = history.loc[symbol_jk].copy()
                
                # --- SAFETY CHECK FOR FUNDAMENTALS ---
                # Check if modules is a dict and contains the symbol
                info = modules.get(symbol_jk, {}) if isinstance(modules, dict) else {}
                
                # --- TECHNICAL CALCULATIONS ---
                df.ta.rsi(append=True)
                df.ta.sma(length=50, append=True)
                
                rsi_cols = [c for c in df.columns if 'RSI' in str(c)]
                sma_cols = [c for c in df.columns if 'SMA_50' in str(c)]
                
                rsi_val = df.iloc[-1][rsi_cols[0]] if rsi_cols else 50
                sma_val = df.iloc[-1][sma_cols[0]] if sma_cols else df.iloc[-1]['close']
                price = df.iloc[-1]['close']
                
                # Foreign Flow Proxy
                df['Vol_Sent'] = (df['close'] - df['open']) * df['volume']
                f_flow = "Accumulation 🟢" if df['Vol_Sent'].tail(5).sum() > 0 else "Distribution 🔴"
                
                # Recommendation Logic
                if rsi_val < 35: rec = "BUY 🚀"
                elif rsi_val > 65: rec = "SELL 📉"
                else: rec = L["wait"]

                # --- FUNDAMENTAL DATA EXTRACTION (with safe defaults) ---
                summ = info.get('summaryDetail', {}) if isinstance(info, dict) else {}
                fin = info.get('financialData', {}) if isinstance(info, dict) else {}
                prof = info.get('summaryProfile', {}) if isinstance(info, dict) else {}
                
                sector = prof.get('sector', 'Default')
                pe = summ.get('trailingPE', 0) or 0
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                bench = INDUSTRY_AVGS.get(next((k for k in INDUSTRY_AVGS if k in sector), "Default"))

                # --- UI: DETAILED REPORTS ---
                st.subheader(f"🔍 {symbol_jk} ({sector})")
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(f"### 📈 {L['tech']}")
                        st.write(f"**RSI (14):** {rsi_val:.2f}")
                        st.write(f"**Trend:** {'Bullish 🔼' if price > sma_val else 'Bearish 🔽'}")
                        st.write(f"**Foreign Flow:** {f_flow}")
                        st.info(f"Verdict: **{rec}**")
                with c2:
                    with st.container(border=True):
                        st.markdown(f"### 🏢 {L['fund']}")
                        st.write(f"**P/E Ratio:** {pe:.1f}x (Avg: {bench[0]}x)")
                        st.write(f"**ROE:** {roe:.1f}% (Avg: {bench[1]}%)")
                        st.success(f"**Quality:** {'Elite 💪' if roe > bench[1] else 'Standard'}")

                summary_list.append({
                    "Stock": symbol_jk.replace(".JK", ""), "Price": f"{price:,.0f}",
                    "Recommendation": rec, "RSI": f"{rsi_val:.1f}", 
                    L["buy_col"]: f"{min(sma_val, price*0.97):,.0f}"
                })

            st.divider()
            st.subheader(L["summary"])
            st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
            st.success("Analysis complete. Data cached for 60 minutes.")
