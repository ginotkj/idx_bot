import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import numpy as np
import time

st.set_page_config(page_title="IDX Insight Engine Pro", layout="wide")

# --- 1. ROBUST DATA FETCHING (With Anti-Block Delay) ---
@st.cache_data(ttl=3600)
def get_clean_data(symbol_string):
    try:
        raw_list = [s.strip().upper() for s in symbol_string.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        
        # We fetch in one go but with a backup check
        t = Ticker(symbols, asynchronous=True)
        history = t.history(period="1y")
        
        if history is None or (isinstance(history, dict) and not history):
            return "Yahoo is blocking requests. Please wait 5 mins.", {}
            
        try:
            modules = t.get_modules(['summaryDetail', 'financialData', 'summaryProfile'])
        except:
            modules = {}
            
        return history, modules
    except Exception as e:
        return str(e), {}

# --- 2. CONFIG & UI ---
L_IDX = "BBCA, BMRI, BBRI, BBNI, TLKM, ASII, ADRO, ANTM, PTBA, UNTR, ICBP, INDF, KLBF, PGAS, SMGR, INTP, AMRT, CPIN, UNVR, MDKA, BRPT, INCO, ITMG, HRUM, MEDC, AKRA, SIDO, ESSA, MYOR, SILO, AMMN, GOTO, BREN, CUAN, TPIA, ARTO, BRIS, EXCL, ISAT, HEAL, MAPI, MAPA, ACES, CTRA, BSDE, PWON, SMRA, MTEL, TOWR, TBIG, SCMA, EMTK, MNCN, INKP, TKIM, JPFA, MAIN, TAPG, DSNG, AALI, LSIP, SIMP, SSMS, TINS, MBMA, NCKL, ADMR, PTRO, HILL, WIFI, WIKA, PTPP, ADHI, WEGE, WTON, JSMR, META, CMNP, BBTN, BDMN, BNGA, PNBN, NISP, AGRO, BRMS, BUMI, ENRG, ELSA, HMSP, GGRM, WIIM, CLEO, CMRY, ULTJ, ROTI, GOOD"

st.title("🏛️ IDX Insight Engine Pro")
top10_btn = st.sidebar.button("🏆 Top 10 Buy Stocks")
manual_input = st.sidebar.text_input("Manual Symbols", "BBCA, BMRI, TLKM")
run_manual = st.sidebar.button("Run Manual Scan")

if run_manual or top10_btn:
    target = L_IDX if top10_btn else manual_input
    with st.spinner("Analyzing Market Data..."):
        history, modules = get_clean_data(target)

        if isinstance(history, str):
            st.error(f"⚠️ {history}")
        else:
            summary = []
            detailed = []
            # Get unique symbols that actually returned data
            available = history.index.get_level_values(0).unique() if hasattr(history, 'index') else []
            
            for sym in available:
                # FIX: Drop rows with NaN close prices immediately to fix 'nan' in table
                df = history.loc[sym].copy().dropna(subset=['close'])
                if len(df) < 30: continue 

                # FIX: Extreme NoneType protection for fundamentals
                info = {}
                if isinstance(modules, dict):
                    raw_info = modules.get(sym)
                    if isinstance(raw_info, dict):
                        info = raw_info

                summ_mod = info.get('summaryDetail', {}) if isinstance(info.get('summaryDetail'), dict) else {}
                fin_mod = info.get('financialData', {}) if isinstance(info.get('financialData'), dict) else {}
                prof_mod = info.get('summaryProfile', {}) if isinstance(info.get('summaryProfile'), dict) else {}

                # Sector Logic (Requested: Blank if unknown)
                sec = prof_mod.get('sector')
                sec_text = f" ({sec})" if sec else ""

                # Technicals
                price = df.iloc[-1]['close']
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col and not np.isnan(df.iloc[-1][rsi_col[0]]) else 50
                
                # Fundamentals
                roe = (fin_mod.get('returnOnEquity', 0) or 0) * 100
                pe = summ_mod.get('trailingPE', 0) or 0
                
                # Recommendation Logic
                if rsi_val < 35 and roe > 12: rec = "BUY 🚀"
                elif rsi_val > 70: rec = "SELL 📉"
                else: rec = "Wait for Dip ⏳"

                if top10_btn and rec != "BUY 🚀": continue

                summary.append({
                    "Stock": sym.replace(".JK", ""), "Price": f"{price:,.0f}",
                    "RSI": rsi_val, "Recommendation": rec,
                    "Target (+10%)": f"{price*1.1:,.0f}", "Stop Loss (-5%)": f"{price*0.95:,.0f}"
                })
                detailed.append({"sym": sym, "sec": sec_text, "rsi": rsi_val, "roe": roe, "pe": pe, "rec": rec})

            if summary:
                st.subheader("📋 Execution Strategy")
                res_df = pd.DataFrame(summary).sort_values("RSI")
                st.dataframe(res_df.head(10), use_container_width=True, hide_index=True)
                
                for r in detailed[:10]:
                    with st.expander(f"🔍 {r['sym']}{r['sec']}"):
                        c1, c2 = st.columns(2)
                        c1.metric("RSI", f"{r['rsi']:.2f}")
                        c2.metric("ROE", f"{r['roe']:.1f}%")
                        st.info(f"Verdict: {r['rec']}")
            else:
                st.warning("No high-probability setups found right now.")
