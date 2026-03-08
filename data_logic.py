#data_logic.py
import pandas as pd
import streamlit as st
from fredapi import Fred
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
        print("=== e-Stat raw response ===")
        print(data)

        # --- 修正箇所：e-Statのデータ抽出 ---
        # 1. ルートを取得
        root = data.get("GET_STATS_DATA", {})
        
        # 2. そもそも成功したか確認（RESULT を見るのが仕様書流）
        if root.get("RESULT", {}).get("STATUS") != 0:
            return pd.Series(dtype='float64')

        # 3. データを掘る
        stat_data = root.get("STATISTICAL_DATA", {})
        values = stat_data.get("DATA_INF", {}).get("VALUE", [])

        # 4. 1件（辞書）でも複数（リスト）でも DataFrame にできるようにする
        if isinstance(values, dict):
            values = [values]

        if not values:
            st.error(f"データが見つかりません: {stats_data_id}")
            return pd.Series(dtype='float64')
        # --- 修正ここまで ---
        df = pd.DataFrame(values)
        
        if "@time" not in df.columns or "$" not in df.columns:
            raise KeyError(f"VALUEに @time または $ がありません。statsDataId={stats_data_id} は時系列表ですか？")

        df = df.rename(columns={"@time": "date", "$": "value"})
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        # e-Statの月次(YYYYMM)を日付型に変換
        series = pd.Series(
            df["value"].values,
            index=pd.to_datetime(df["date"].astype(str).str.replace("M",""), format="%Y%m", errors="coerce")
        )
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

        # --- 1. データ取得フェーズ ---
        if symbol == "JPN":
            # 日本：CPIと失業率は e-Stat から取得
            raw_cpi = fetch_estat_data("0003427113", cd_cat01="0001")
            raw_unrate = fetch_estat_data("0003007513", cd_cat01="01")
            
            # 金利・マネーは取得が容易な FRED から取得
            raw_10y = fred.get_series("IRLTLT01JPM156N")
            raw_2y  = fred.get_series("IR3TIB01JPM156N")
            raw_rate = fred.get_series("IRSTCI01JPM156N")
            raw_m2  = fred.get_series("MYAGM2JPM189S")

        elif symbol == "^TNX": # USA
            # アメリカ：全て FRED から取得
            raw_cpi = fred.get_series("CPIAUCSL", observation_start='2018-01-01')
            raw_10y = fred.get_series("DGS10")
            raw_2y = fred.get_series("DGS2")
            raw_m2 = fred.get_series("M2SL", observation_start='2018-01-01')
            raw_rate = fred.get_series("FEDFUNDS")
            raw_unrate = fred.get_series("UNRATE")
        
        else:
            return None

        # --- 2. スコア計算フェーズ (共通) ---
        cpi_yoy_series = raw_cpi.pct_change(12).dropna()
        if cpi_yoy_series.empty:
            st.error(f"CPI YoY cannot be calculated for {name}")
            return None

        cpi_yoy = cpi_yoy_series.iloc[-1] * 100
        cpi_score = max(0, 200 - abs(cpi_yoy - 2.0) * 50)
        
        yield_vol = raw_10y.diff().tail(20).std()
        stability_score = max(0, 100 - (yield_vol * 500))
        
        # 直近のイールドカーブ・ギャップ
        curve_gap = raw_10y.iloc[-1] - raw_2y.iloc[-1]
        curve_score = max(0, min(100, 100 + (curve_gap * 100)))

        m2_yoy = raw_m2.pct_change(12).dropna().iloc[-1] * 100
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 30))
        
        # 実質金利スコア
        real_rate = raw_rate.iloc[-1] - cpi_yoy
        fin_strength_score = int(max(0, min(200, real_rate * 50)))
        
        # 雇用スコア
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
        st.error(f"Data Processing Error ({name}): {e}")
        return None
