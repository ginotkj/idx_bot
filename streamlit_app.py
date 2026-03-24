import streamlit as st
from yahooquery import Ticker
import pandas as pd
import numpy as np

# --- MANUAL TECHNICAL INDICATORS (NO PANDAS-TA) ---
def calculate_rsi(data, period=14):
    """Calculate RSI manually"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_sma(data, period=50):
    """Calculate Simple Moving Average"""
    return data.rolling(window=period).mean()

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IDX Master Trading Terminal", layout="wide")

# --- 1. SIDEBAR TOOLS ---
if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
    st.success("Cache Cleared! Running live analysis...")

top10_btn = st.sidebar.button("🏆 Top 10 Buy Stocks")

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
    "Infrastructures": [12.5, 10.2]
}
GENERIC_BENCH = [12.0, 10.0]

# Expanded basket of ~100 highly liquid IDX stocks (Kompas100 equivalents)
LIQUID_IDX_BASKET = "BBCA, BMRI, BBRI, BBNI, TLKM, ASII, ADRO, ANTM, PTBA, UNTR, ICBP, INDF, KLBF, PGAS, SMGR, INTP, AMRT, CPIN, UNVR, MDKA, BRPT, INCO, ITMG, HRUM, MEDC, AKRA, SIDO, ESSA, MYOR, SILO, AMMN, GOTO, BREN, CUAN, TPIA, ARTO, BRIS, EXCL, ISAT, HEAL, MAPI, MAPA, ACES, CTRA, BSDE, PWON, SMRA, MTEL, TOWR, TBIG, SCMA, EMTK, MNCN, INKP, TKIM, JPFA, MAIN, TAPG, DSNG, AALI, LSIP, SIMP, SSMS, TINS, MBMA, NCKL, ADMR, PTRO, HILL, WIFI, WIKA, PTPP, ADHI, WEGE, WTON, JSMR, META, CMNP, BBTN, BDMN, BNGA, PNBN, NISP, AGRO, BRMS, BUMI, ENRG, ELSA, HMSP, GGRM, WIIM, CLEO, CMRY, ULTJ, ROTI, GOOD"

selected_lang = st.sidebar.selectbox("Language / Bahasa", ["English", "Bahasa Indonesia"])
L = lang_data[selected_lang]

st.title(L["title"])
input_symbols = st.sidebar.text_input("Symbols for Manual Scan", "BBCA, BMRI, TLKM, ASII, ADRO, ANTM")
analyze_btn = st.sidebar.button("Run Deep Analysis")

# Trigger either manual analysis OR the Top 10 Scanner
if analyze_btn or top10_btn:
    symbols_to_run = LIQUID_IDX_BASKET if top10_btn else input_symbols
    mode_title = "Scanning Top 100 Stocks for Elite Buy Opportunities..." if top10_btn else "Calculating Deep Analysis..."
    
    with st.spinner(mode_title):
        history, modules = get_stock_data_pro(symbols_to_run)

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
                
                # --- ROOT CAUSE FIX: Clean missing data (NaN) before calculating ---
                df = df.dropna(subset=['close', 'volume'])
                if df.empty:
                    continue  # Skip this stock if no valid price data exists
                # -------------------------------------------------------------------
                
                info = modules.get(symbol_jk, {}) if isinstance(modules, dict) else {}
                
                # --- FUNDAMENTALS & BENCHMARKS ---
                summ = info.get('summaryDetail', {}) if isinstance(info, dict) else {}
                fin = info.get('financialData', {}) if isinstance(info, dict) else {}
                prof = info.get('summaryProfile', {}) if isinstance(info, dict) else {}
                
                # Clean Sector Formatting (Leaves blank if no sector is found)
                sector_raw = prof.get('sector')
                sector_display = f" ({sector_raw})" if sector_raw else ""
                
                pe = summ.get('trailingPE', 0) or 0
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                bench = next((v for k, v in INDUSTRY_AVGS.items() if sector_raw and k in sector_raw), GENERIC_BENCH)
                
                is_elite = roe > bench[1]

                # --- TECHNICALS & RISK ---
                df['returns'] = df['close'].pct_change()
                volatility = df['returns'].std() * np.sqrt(252)
                risk_label = "Low 🔵" if volatility < 0.20 else "Medium 🟡" if volatility < 0.35 else "High 🔴"

                # --- MANUAL TECHNICAL INDICATORS (FIXED) ---
                df['RSI_14'] = calculate_rsi(df['close'], 14)
                df['SMA_50'] = calculate_sma(df['close'], 50)
                
                # Secondary safeguard to ensure RSI and SMA defaults if NaNs slip through indicators
                rsi_val = df.iloc[-1]['RSI_14'] if pd.notna(df.iloc[-1]['RSI_14']) else 50
                sma_val = df.iloc[-1]['SMA_50'] if pd.notna(df.iloc[-1]['SMA_50']) else df.iloc[-1]['close']
                price = df.iloc[-1]['close']
                
                df['Vol_Sent'] = (df['close'] - df['open']) * df['volume']
                f_flow = "Accumulation 🟢" if df['Vol_Sent'].tail(5).sum() > 0 else "Distribution 🔴"
                
                # --- STRICT RECOMMENDATION LOGIC ---
                if rsi_val < 35 and is_elite: 
                    rec = "BUY 🚀"
                elif rsi_val > 65: 
                    rec = "SELL 📉"
                else: 
                    rec = L["wait"]
                
                target_price = price * 1.10
                stop_loss = price * 0.95

                if top10_btn and rec != "BUY 🚀":
                    continue

                summary_list.append({
                    "Stock": symbol_jk.replace(".JK", ""), "Price": f"{price:,.0f}",
                    "Risk": risk_label, "Recommendation": rec, "RSI": rsi_val,
                    "Target (+10%)": f"{target_price:,.0f}", "Stop Loss (-5%)": f"{stop_loss:,.0f}",
                    L["buy_col"]: f"{min(sma_val, price*0.97):,.0f}"
                })
                
                detailed_reports.append({
                    "symbol": symbol_jk, "sector": sector_display, "rsi": rsi_val, "vol": volatility,
                    "price": price, "sma": sma_val, "f_flow": f_flow, "rec": rec,
                    "pe": pe, "roe": roe, "bench": bench, "is_elite": is_elite
                })

            # --- PROCESS TOP 10 LOGIC ---
            if top10_btn:
                summary_list = sorted(summary_list, key=lambda x: x["RSI"])[:10]
                detailed_reports = sorted(detailed_reports, key=lambda x: x["rsi"])[:10]
                
                if len(summary_list) == 0:
                    st.warning("⚠️ No stocks out of the Top 100 currently meet the strict criteria (Oversold RSI < 35 AND Elite ROE). The market might be overextended.")
                else:
                    st.success(f"🔥 Found {len(summary_list)} Elite Oversold Stocks from the Top 100 Scanner!")

            # Format RSI for table
            for row in summary_list:
                row["RSI"] = f"{row['RSI']:.1f}"

            # --- DISPLAY SECTION ---
            if len(summary_list) > 0:
                st.subheader("🏆 Top 10 Buy Execution Strategy" if top10_btn else L["summary"])
                st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
                st.divider()

                for r in detailed_reports:
                    st.subheader(f"🔍 {r['symbol']}{r['sector']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        with st.container(border=True):
                            st.markdown(f"### 📈 {L['tech']}")
                            st.write(f"**RSI (14):** {r['rsi']:.2f}")
                            st.write(f"**Foreign Flow:** {r['f_flow']}")
                            st.write(f"**Annual Volatility:** {r['vol']*100:.1f}%")
                            st.info(f"Verdict: **{r['rec']}**")
                    with c2:
                        with st.container(border=True):
                            st.markdown(f"### 🏢 {L['fund']}")
                            st.write(f"**P/E Ratio:** {r['pe']:.1f}x (Avg: {r['bench'][0]}x)")
                            st.write(f"**ROE:** {r['roe']:.1f}% (Avg: {r['bench'][1]}%)")
                            st.success(f"**Quality:** {'Elite 💪' if r['is_elite'] else 'Standard'}")

            with st.expander(L["method"], expanded=False):
                st.markdown("### 📊 Indicators & Strict Recommendations")
                st.write("**Strict BUY Logic:** A stock is ONLY recommended as a 'BUY' if it is both Technically Oversold (RSI < 35) AND Fundamentally Elite (ROE > Industry Average).")
                st.write(f"**{L['risk']}:** Category based on Annualized Volatility (<20%=Low, >35%=High).")
                st.write("**Foreign Flow:** Uses Volume-Price Trend logic. Positive net flow over 5 days suggests accumulation.")
                st.write("**SMA 50:** 50-day average price used to identify the 'institutional floor'.")
                st.write("**Technical Indicators:** Now using manual calculations for improved reliability and no external dependencies.")
