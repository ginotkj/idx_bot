import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import numpy as np

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
        history = t.history(period="1y")
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
        "wait": "Wait for Dip ⏳", "buy_col": "Buy Price (Entry)", "summary": "📋 Execution Strategy",
        "method": "🧠 Analysis Methodology", "risk": "Risk"
    },
    "Bahasa Indonesia": {
        "title": "🏛️ Terminal Trading Profesional Master BEI",
        "tech": "Teknikal & Sentimen Asing", "fund": "Fundamental & Daya Saing",
        "wait": "Tunggu Dip ⏳", "buy_col": "Harga Beli (Entry)", "summary": "📋 Strategi Eksekusi",
        "method": "🧠 Metodologi Analisis", "risk": "Risiko"
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
    with st.spinner('Calculating Execution Strategy...'):
        history, modules = get_stock_data_pro(input_symbols)

        if isinstance(history, str):
            st.error(f"Connection Issue: {history}")
        elif history is None or history.empty:
            st.warning("No data found.")
        else:
            summary_list = []
            detailed_reports = []
            available_symbols = history.index.get_level_values(0).unique()
            
            for symbol_jk in available_symbols:
                df = history.loc[symbol_jk].copy()
                info = modules.get(symbol_jk, {}) if isinstance(modules, dict) else {}
                
                # --- RISK & VOLATILITY ---
                df['returns'] = df['close'].pct_change()
                volatility = df['returns'].std() * np.sqrt(252)
                risk_label = "Low 🔵" if volatility < 0.20 else "Medium 🟡" if volatility < 0.35 else "High 🔴"

                # --- TECHNICALS ---
                df.ta.rsi(append=True)
                df.ta.sma(length=50, append=True)
                rsi_cols = [c for c in df.columns if 'RSI' in str(c)]
                sma_cols = [c for c in df.columns if 'SMA_50' in str(c)]
                
                rsi_val = df.iloc[-1][rsi_cols[0]] if rsi_cols else 50
                sma_val = df.iloc[-1][sma_cols[0]] if sma_cols else df.iloc[-1]['close']
                price = df.iloc[-1]['close']
                
                # Recommendation logic
                if rsi_val < 35: rec = "BUY 🚀"
                elif rsi_val > 65: rec = "SELL 📉"
                else: rec = L["wait"]

                # --- EXECUTION CALCULATION ---
                target_price = price * 1.10
                stop_loss = price * 0.95

                # --- FUNDAMENTALS ---
                summ = info.get('summaryDetail', {}) if isinstance(info, dict) else {}
                fin = info.get('financialData', {}) if isinstance(info, dict) else {}
                prof = info.get('summaryProfile', {}) if isinstance(info, dict) else {}
                sector = prof.get('sector', 'Default')
                pe = summ.get('trailingPE', 0) or 0
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                bench = INDUSTRY_AVGS.get(next((k for k in INDUSTRY_AVGS if k in sector), "Default"))

                # Store for Table
                summary_list.append({
                    "Stock": symbol_jk.replace(".JK", ""), 
                    "Price": f"{price:,.0f}",
                    "Risk": risk_label,
                    "Recommendation": rec,
                    "Target (+10%)": f"{target_price:,.0f}",
                    "Stop Loss (-5%)": f"{stop_loss:,.0f}",
                    L["buy_col"]: f"{min(sma_val, price*0.97):,.0f}"
                })
                
                # Store for Details
                detailed_reports.append({
                    "symbol": symbol_jk, "sector": sector, "rsi": rsi_val, "vol": volatility,
                    "price": price, "sma": sma_val, "rec": rec, "pe": pe, "roe": roe, "bench": bench
                })

            # --- DISPLAY 1: EXECUTION STRATEGY (TOP) ---
            st.subheader(L["summary"])
            st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
            st.divider()

            # --- DISPLAY 2: DETAILED ANALYSIS ---
            for r in detailed_reports:
                st.subheader(f"🔍 {r['symbol']} ({r['sector']})")
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(f"### 📈 {L['tech']}")
                        st.write(f"**RSI (14):** {r['rsi']:.2f}")
                        st.write(f"**Annual Volatility:** {r['vol']*100:.1f}%")
                        st.info(f"Verdict: **{r['rec']}**")
                with c2:
                    with st.container(border=True):
                        st.markdown(f"### 🏢 {L['fund']}")
                        st.write(f"**P/E Ratio:** {r['pe']:.1f}x (Avg: {r['bench'][0]}x)")
                        st.write(f"**ROE:** {r['roe']:.1f}% (Avg: {r['bench'][1]}%)")
                        st.success(f"**Quality:** {'Elite 💪' if r['roe'] > r['bench'][1] else 'Standard'}")

            # --- DISPLAY 3: METHODOLOGY ---
            with st.expander(L["method"], expanded=False):
                st.markdown("### 📊 Indicators & Calculations")
                st.write(f"**{L['risk']}:** Category based on Annualized Volatility (<20%=Low, >35%=High).")
                st.write("**Target Price:** Calculated as a +10% profit objective from current price.")
                st.write("**Stop Loss:** Set at -5% to protect capital from significant drawdowns.")
                st.write("**RSI (14):** Momentum indicator for identifying Oversold (<35) and Overbought (>65) levels.")
                st.write("**SMA 50:** Average closing price over 50 days; used as a technical floor for 'Buy Price' targets.")
