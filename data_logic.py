#data_logic.py
import pandas as pd
import streamlit as st
from fredapi import Fred
from boj_api import fetch_boj_data

@st.cache_data(ttl=86400)
def fetch_central_bank_data(symbol, name):
    try:
        fred_key = st.secrets["FRED_API_KEY"]
        fred = Fred(api_key=fred_key)

        # --- 日本（JPN）の場合：日銀API直結 ---
        if symbol == "JPN":
            # 日銀APIから5つの指標を直接取得
            df_rate = fetch_boj_data("FM01", "STRDCLUCON")
            df_cpi = fetch_boj_data("PR01", "PR01_CPI2020GY00") # CPI
            df_10y = fetch_boj_data("IR01", "IR01_JGB10Y@D")    # 10年債
            df_2y = fetch_boj_data("IR01", "IR01_JGB2Y@D")      # 2年債
            df_m2 = fetch_boj_data("MA01", "MA01_M2AGY00")      # M2

            # 既存の計算ロジック（Series型）に合わせるための変換
            raw_rate = pd.Series(df_rate['value'].values, index=pd.to_datetime(df_rate['date']))
            raw_cpi = pd.Series(df_cpi['value'].values, index=pd.to_datetime(df_cpi['date']))
            raw_10y = pd.Series(df_10y['value'].values, index=pd.to_datetime(df_10y['date']))
            raw_2y = pd.Series(df_2y['value'].values, index=pd.to_datetime(df_2y['date']))
            raw_m2 = pd.Series(df_m2['value'].values, index=pd.to_datetime(df_m2['date']))
            
            # 失業率(unrate)だけは日銀APIにないので、FREDから取得
            raw_unrate = fred.get_series("CPALTT01JPM657N")
        else:
            if symbol == "^TNX":  # USA
                ids = {"cpi": "CPIAUCSL", "10y": "DGS10", "2y": "DGS2", "m2": "M2SL", "rate": "FEDFUNDS", "unrate": "UNRATE"}    
            elif symbol == "EZ":   # Eurozone
                ids = {"cpi": "CP0000EZ19M086NEST", "10y": "IRLTLT01EZM156N", "2y": "IR3TIB01EZM156N", "m2": "MABMM301EZM189S", "rate": "ECBDFR", "unrate": "LRHUTTTTEZM156S"}
            elif symbol == "UK":   # UK
                ids = {"cpi": "GBRCPIALLMINMEI", "10y": "IRLTLT01GBM156N", "2y": "IR3TIB01GBM156N", "m2": "MABMM301GBM189S", "rate": "IR3TIB01GBM156N", "unrate": "LRHUTTTTGBM156S"}
            elif symbol == "CAN":  # Canada
                ids = {"cpi": "CPALTT01CAM657N", "10y": "IRLTLT01CAM156N", "2y": "IR3TIB01CAM156N", "m2": "MABMM301CAM189S", "rate": "IRSTCB01CAM156N", "unrate": "LRUNTTTTCAM156S"}
            elif symbol == "AUS":  # Australia
                ids = {"cpi": "AUSCPIALLQINMEI", "10y": "IRLTLT01AUM156N", "2y": "IR3TIB01AUM156N", "m2": "MABMM301AUM189S", "rate": "IR3TIB01AUM156N", "unrate": "LRUNTTTTAUM156S"}
            else:
                return None

            # --- データの取得 ---
            # 共通して取得する（CPIとM2は少し長めに取る）
            raw_cpi = fred.get_series(ids["cpi"], observation_start='2018-01-01')
            raw_10y = fred.get_series(ids["10y"])
            raw_2y = fred.get_series(ids["2y"])
            raw_m2 = fred.get_series(ids["m2"], observation_start='2018-01-01')
            raw_rate = fred.get_series(ids["rate"])
            raw_unrate = fred.get_series(ids["unrate"])

        # 計算
        cpi_yoy = raw_cpi.pct_change(12).dropna().iloc[-1] * 100
        cpi_score = max(0, 200 - abs(cpi_yoy - 2.0) * 50)
        future_focus_score = int(cpi_score) # CPIスコアをそのまま使用
        
        yield_vol = raw_10y.diff().tail(20).std()
        stability_score = max(0, 100 - (yield_vol * 500))
        curve_gap = raw_10y.iloc[-1] - raw_2y.iloc[-1]
        curve_score = max(0, min(100, 100 + (curve_gap * 100)))
        market_pos_score = int(stability_score + curve_score)

        m2_yoy = raw_m2.pct_change(12).dropna().iloc[-1] * 100
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 30))
        real_rate = raw_rate.iloc[-1] - cpi_yoy
        fin_strength_score = int(max(0, min(200, real_rate * 50)))
        people_score = int(max(0, 200 - abs(raw_unrate.iloc[-1] - 4.0) * 40))

        axes = {
            "Future Focus": int(cpi_score),
            "Market Position": int(stability_score + curve_score),
            "Financial Strength": fin_strength_score,
            "Cashflow Quality": cashflow_score,
            "People": people_score 
        }

        return {
            "axes": axes, 
            "total": int(sum(axes.values())), 
            "name": name,
            "price_hist": raw_10y.tail(252), 
            "current_price": raw_10y.iloc[-1],
            "pe": "Central Bank", 
            "market_cap": 0
        }
    except Exception as e:
        st.error(f"FRED Error ({name}): {e}")
        return None

# ルーターを更新
def fetch_data(symbol, name):
    return fetch_central_bank_data(symbol, name)

# 比較用（日本銀行をデフォルトに）
def fetch_jpn_data():
    return fetch_central_bank_data("JPN", "Bank of Japan")
