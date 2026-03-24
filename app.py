import streamlit as st
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta
import numpy as np

st.set_page_config(page_title="IDX Insight Engine Pro", layout="wide")

# --- 1. THE FAIL-SAFE DATA ENGINE ---
@st.cache_data(ttl=1800) # Cache for 30 mins to reduce rate-limit risk
def fetch_market_data(symbol_str):
    try:
        raw_list = [s.strip().upper() for s in symbol_str.split(',')]
        symbols = [s + ('' if s.endswith('.JK') else '.JK') for s in raw_list]
        
        t = Ticker(symbols, asynchronous=True)
        history = t.history(period="1y")
        
        # Check if Yahoo returned a block/empty response
        if history is None or (isinstance(history, dict) and not history) or history.empty:
            return None, None
            
        try:
            modules = t.get_modules(['summaryDetail', 'financialData', 'summaryProfile'])
        except:
            modules = {}
            
        return history, modules
    except Exception:
        return None, None

# --- 2. APP UI ---
st.title("🏛️ IDX Insight Engine Pro")

if st.sidebar.button("🔄 Clear Cache & Refresh"):
    st.cache_data.clear()
    st.rerun()

top10_mode = st.sidebar.button("🏆 Top 10 Buy Stocks")
manual_input = st.sidebar.text_input("Stock Symbols", "BBCA, BMRI, TLKM, ASII")
run_manual = st.sidebar.button("Run Deep Analysis")

# ~100 Stocks for the Scanner
LIQUID_BASKET = "BBCA, BMRI, BBRI, BBNI, TLKM, ASII, ADRO, ANTM, PTBA, UNTR, ICBP, INDF, KLBF, PGAS, SMGR, INTP, AMRT, CPIN, UNVR, MDKA, BRPT, INCO, ITMG, HRUM, MEDC, AKRA, SIDO, ESSA, MYOR, SILO, AMMN, GOTO, BREN, CUAN, TPIA, ARTO, BRIS, EXCL, ISAT, HEAL, MAPI, MAPA, ACES, CTRA, BSDE, PWON, SMRA, MTEL, TOWR, TBIG, SCMA, EMTK, MNCN, INKP, TKIM, JPFA, MAIN, TAPG, DSNG, AALI, LSIP, SIMP, SSMS, TINS, MBMA, NCKL, ADMR, PTRO, HILL, WIFI, WIKA, PTPP, ADHI, WEGE, WTON, JSMR, META, CMNP, BBTN, BDMN, BNGA, PNBN, NISP, AGRO, BRMS, BUMI, ENRG, ELSA, HMSP, GGRM, WIIM, CLEO, CMRY, ULTJ, ROTI, GOOD"

if run_manual or top10_mode:
    target = LIQUID_BASKET if top10_mode else manual_input
    
    with st.spinner("Connecting to IDX Data Streams..."):
        history, modules = fetch_market_data(target)

        if history is None:
            st.error("⚠️ Yahoo Finance is currently rate-limiting this connection.")
            st.info("Try clicking 'Clear Cache' or wait 5 minutes for the block to lift.")
        else:
            summary_data = []
            available_syms = history.index.get_level_values(0).unique()
            
            for sym in available_syms:
                # FIX: Remove any row with NaN to prevent 'nan' in table
                df = history.loc[sym].copy().dropna(subset=['close'])
                if len(df) < 20: continue

                # FIX: Guaranteed dictionary type to prevent AttributeError
                info = {}
                if isinstance(modules, dict):
                    raw_info = modules.get(sym)
                    if isinstance(raw_info, dict):
                        info = raw_info

                summ = info.get('summaryDetail', {}) if isinstance(info.get('summaryDetail'), dict) else {}
                fin = info.get('financialData', {}) if isinstance(info.get('financialData'), dict) else {}
                
                # Calculations with zero-division safety
                price = df.iloc[-1]['close']
                roe = (fin.get('returnOnEquity', 0) or 0) * 100
                
                df.ta.rsi(append=True)
                rsi_col = [c for c in df.columns if 'RSI' in str(c)]
                rsi_val = df.iloc[-1][rsi_col[0]] if rsi_col and pd.notna(df.iloc[-1][rsi_col[0]]) else 50
                
                # Strategy logic
                rec = "Wait for Dip ⏳"
                if rsi_val < 35 and roe > 10: rec = "BUY 🚀"
                elif rsi_val > 70: rec = "SELL 📉"

                if top10_mode and rec != "BUY 🚀": continue

                summary_data.append({
                    "Stock": sym.replace(".JK", ""),
                    "Price": f"{price:,.0f}",
                    "RSI": f"{rsi_val:.1f}",
                    "Recommendation": rec,
                    "Buy Price Target": f"{price*0.97:,.0f}" # 3% below current
                })

            if summary_data:
                st.subheader("📋 Execution Strategy")
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            else:
                st.warning("No high-confidence setups found. Market might be overextended.")
