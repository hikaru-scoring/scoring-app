import pandas as pd
import streamlit as st
from fredapi import Fred
import io
import requests

# --------------------------------------------------
# 🏛️ 1. FRBスコア専用ロジック（聖域：一切変えない）
# --------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_frb_logic(name):
    try:
        fred_key = st.secrets["FRED_API_KEY"]
        fred = Fred(api_key=fred_key)

        # データの取得
        raw_cpi = fred.get_series("CPIAUCSL", observation_start='2024-01-01')
        raw_expect = fred.get_series("T10YIE")
        raw_10y = fred.get_series("DGS10")
        raw_2y = fred.get_series("DGS2")
        raw_m2 = fred.get_series("M2SL", observation_start='2023-01-01')
        raw_ff = fred.get_series("FEDFUNDS")
        raw_unrate = fred.get_series("UNRATE")

        # 計算
        cpi_yoy = raw_cpi.pct_change(12).iloc[-1] * 100
        expect_val = raw_expect.iloc[-1]
        cpi_score = max(0, 200 - abs(cpi_yoy - 2.0) * 50)
        expect_score = max(0, 200 - abs(expect_val - 2.0) * 50)
        future_focus_score = int((cpi_score + expect_score) / 2)
        
        yield_vol = raw_10y.diff().tail(20).std()
        stability_score = max(0, 100 - (yield_vol * 500))
        curve_gap = raw_10y.iloc[-1] - raw_2y.iloc[-1]
        curve_score = max(0, min(100, 100 + (curve_gap * 100)))
        market_pos_score = int(stability_score + curve_score)

        m2_yoy = raw_m2.pct_change(12).iloc[-1] * 100
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 30))
        real_rate = raw_ff.iloc[-1] - cpi_yoy
        fin_strength_score = int(max(0, min(200, real_rate * 50)))
        people_score = int(max(0, 200 - abs(raw_unrate.iloc[-1] - 4.0) * 40))

        axes = {
            "Future Focus": future_focus_score,
            "Market Position": market_pos_score,
            "Financial Strength": fin_strength_score,
            "Cashflow Quality": cashflow_score,
            "People": people_score 
        }
        return {
            "axes": axes, "total": int(sum(axes.values())), "name": name,
            "price_hist": raw_expect.tail(252), "current_price": raw_10y.iloc[-1],
            "pe": "Macro", "market_cap": 0
        }
    except Exception as e:
        st.error(f"FRB Logic Error: {e}")
        return None

def fetch_oil_data():
    return fetch_data("CL.F", "WTI CRUDE OIL")