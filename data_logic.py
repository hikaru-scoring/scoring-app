#data_logic.py
import pandas as pd
import streamlit as st
from fredapi import Fred
from boj_api import fetch_boj_data
import requests

# --- e-Stat API取得用の関数を新規追加 ---
def fetch_estat_data(stats_data_id, cd_cat01=None):
    app_id = st.secrets["ESTAT_APP_ID"]
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    params = {"appId": app_id, "statsDataId": stats_data_id, "metaGetFlg": "Y", "cntGetFlg": "N"}
    if cd_cat01:
        params["cdCat01"] = cd_cat01

    try:
        response = requests.get(url, params=params)
        data = response.json()
        # --- 修正箇所：e-Statのデータ抽出 ---
        # 階層を一つずつ安全に掘り進めます
        stats_list = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {})
        data_inf = stats_list.get("DATA_INF", {})
        values = data_inf.get("VALUE", [])

        if not values:
            st.error(f"データが見つかりません: {stats_data_id}")
            return pd.Series(dtype='float64')
        # --- 修正ここまで ---
        df = pd.DataFrame(values)
        df = df.rename(columns={"@time": "date", "$": "value"})
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        # e-Statの月次(YYYYMM)を日付型に変換
        series = pd.Series(df["value"].values, index=pd.to_datetime(df["date"], format="%Y%m", errors='coerce'))
        return series.sort_index()
    except Exception as e:
        st.error(f"e-Stat Error ({stats_data_id}): {e}")
        return pd.Series(dtype='float64')

# この下に既存の @st.cache_data が続く...

@st.cache_data(ttl=86400)
def fetch_central_bank_data(symbol, name):
    try:
        fred_key = st.secrets["FRED_API_KEY"]
        fred = Fred(api_key=fred_key)

        # --- 日本（JPN）の場合：日銀 & e-Stat ハイブリッド ---
        if symbol == "JPN":
            # 日銀APIから金融・市場指標を取得
            df_rate = fetch_boj_data("FM01", "STRDCLUCON")
            df_10y = fetch_boj_data("IR01", "IR01_JGB10Y@D")
            df_2y = fetch_boj_data("IR01", "IR01_JGB2Y@D")
            df_m2 = fetch_boj_data("MA01", "MA01_M2AGY00")

            # ★ 物価(CPI)と雇用(失業率)は総務省(e-Stat)から直接取得
            # 0003423127: 消費者物価指数 / 0003007513: 労働力調査
            raw_cpi = fetch_estat_data("0003427113", cd_cat01="1000000000")
            raw_unrate = fetch_estat_data("00200524")

            # 日銀データの変換（Series化）
            raw_rate = pd.Series(df_rate['value'].values, index=pd.to_datetime(df_rate['date']))
            raw_10y = pd.Series(df_10y['value'].values, index=pd.to_datetime(df_10y['date']))
            raw_2y = pd.Series(df_2y['value'].values, index=pd.to_datetime(df_2y['date']))
            raw_m2 = pd.Series(df_m2['value'].values, index=pd.to_datetime(df_m2['date']))

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
