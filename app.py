import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import numpy as np

st.set_page_config(page_title="IDX Insight Engine Pro", layout="wide")

# --- SIDEBAR ---
if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
    st.success("Cache Cleared!")

top10_btn = st.sidebar.button("🏆 Top 10 Buy Stocks")

# --- DATA ENGINE ---
@st.cache_data(ttl=3600)
def get_data(symbol_string):
    try:
        raw_list = [s.strip().upper() for s in symbol_string.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        t = Ticker(symbols, asynchronous=True)
        history = t.history(period="1y")
        try:
            modules = t.get_modules(['summaryDetail', 'financialData', 'summaryProfile'])
        except:
            modules = {} # Fallback if modules fail
        return history, modules
    except Exception as e:
        return str(e), {}

# --- SETTINGS ---
LIQUID_IDX = "BBCA, BMRI, BBRI, BBNI, TLKM, ASII, ADRO, ANTM, PTBA, UNTR, ICBP, INDF, KLBF, PGAS, SMGR, INTP, AMRT, CPIN, UNVR, MDKA, BRPT, INCO, ITMG, HRUM, MEDC, AKRA, SIDO, ESSA, MYOR, SILO, AMMN, GOTO, BREN, CUAN, TPIA, ARTO, BRIS, EXCL, ISAT, HEAL, MAPI, MAPA, ACES, CTRA, BSDE, PWON, SMRA, MTEL, TOWR, TBIG, SCMA, EMTK, MNCN, INKP, TKIM, JPFA, MAIN, TAPG, DSNG, AALI, LSIP, SIMP, SSMS, TINS, MBMA, NCKL, ADMR, PTRO, HILL, WIFI, WIKA, PTPP, ADHI, WEGE, WTON, JSMR, META, CMNP, BBTN, BDMN, BNGA, PNBN, NISP, AGRO, BRMS, BUMI, ENRG, ELSA, HMSP, GGRM, WIIM, CLEO, CMRY, ULTJ, ROTI, GOOD"

st.title("🏛️ IDX Insight Engine Pro")
input_symbols = st.sidebar.text_input("Manual Scan", "BBCA, BMRI, BBRI, TLKM")
run = st.sidebar.button("Run Deep Analysis")

if run or top10_btn:
    target_symbols = LIQUID_IDX if top10_btn else input_symbols
    with st.spinner("Fetching Live Data..."):
        history, modules = get_data(target_symbols)

        if isinstance(history, str) or history is None or history.empty:
            st.error("⚠️ Yahoo Finance is currently rate-limiting this server. Please wait 5-10 minutes.")
        else:
            summary_list = []
            detailed_reports = []
            available = history.index.get_level_values(0).unique()
            
            for sym in available:
                df = history.loc[sym].copy().dropna(subset=['close'])
                if len(df) < 20: continue # Skip if not enough history
                
                # CRITICAL FIX: Safe dictionary access to prevent NoneType crash
                info = {}
                if modules and isinstance(modules, dict):
                    info = modules.get(sym, {})
                    if not isinstance(info, dict): info = {}

                summ = info.get('summaryDetail', {})
                fin = info.get('financialData', {})
                prof = info.get('summaryProfile', {})
                
                # Sector clean-up
                sec = prof.get('sector')
                sec_display = f" ({sec})" if sec else ""
                
                # Stats with NaN safety
                price = df.iloc[-1]['close']
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                is_elite = roe > 10.0 # Standard IDX benchmark
                
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col and pd.notna(df.iloc[-1][rsi_col[0]]) else 50
                
                # Logic: BUY if RSI < 35 AND ROE is Elite
                rec = "BUY 🚀" if (rsi_val < 35 and is_elite) else "Wait for Dip ⏳"
                if rsi_val > 70: rec = "SELL 📉"

                if top10_btn and rec != "BUY 🚀": continue

                summary_list.append({
                    "Stock": sym.replace(".JK", ""), "Price": f"{price:,.0f}",
                    "Recommendation": rec, "RSI": rsi_val,
                    "Target (+10%)": f"{price*1.1:,.0f}", "Stop Loss (-5%)": f"{price*0.95:,.0f}"
                })
                
                detailed_reports.append({"sym": sym, "sec": sec_display, "rsi": rsi_val, "roe": roe, "rec": rec})

            if summary_list:
                st.subheader("📋 Execution Strategy")
                # Sort by RSI to find best deals
                df_final = pd.DataFrame(summary_list).sort_values("RSI")
                st.dataframe(df_final.head(10), use_container_width=True, hide_index=True)
                
                for r in detailed_reports[:10]:
                    with st.expander(f"Analysis: {r['sym']}{r['sec']}"):
                        c1, c2 = st.columns(2)
                        c1.metric("RSI (Technicals)", f"{r['rsi']:.1f}", delta="Oversold" if r['rsi'] < 35 else None)
                        c2.metric("ROE (Fundamentals)", f"{r['roe']:.1f}%", delta="Elite" if r['roe'] > 10 else None)
                        st.info(f"Final Verdict: {r['rec']}")
            else:
                st.warning("No stocks currently meet the strict BUY criteria. Market may be overbought.")
