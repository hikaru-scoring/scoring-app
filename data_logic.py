# data_logic.py
import pandas as pd
import streamlit as st
import requests

MAS_RESOURCES = {
    "SGS_YIELD": "9a05ad12-ace5-4231-9715-4fa2517a15ff",
    "M2": "5a676c8e-a912-45e0-b615-51543883a45c",
}

@st.cache_data(ttl=86400)
def fetch_data(symbol, name):
    import pandas as pd
    import streamlit as st
    from fredapi import Fred

    # 🏛️ FRBスコア専用のデータセット
    FRB_METRICS = {
        "CPI": "CPIAUCSL",   # 消費者物価指数（実体）
        "EXPECT": "T10YIE",  # 10年期待インフレ率（未来予測）
        "GS10": "DGS10",     # 10年債利回り
        "FF": "FEDFUNDS",    # 政策金利
        "UNRATE": "UNRATE"   # 失業率
    }

    # data_logic.py の 15行目付近に追加
    MAS_RESOURCES = {
        "SGS_YIELD": "9a05ad12-ace5-4231-9715-4fa2517a15ff",  # SGS利回り（10Y, 2Y等）
        "M2": "5a676c8e-a912-45e0-b615-51543883a45c",         # マネーサプライ
    }

    try:
        fred_key = st.secrets["FRED_API_KEY"]
        fred = Fred(api_key=fred_key)

        # 1. データの取得（Future Focus 用）
        # CPIは前年比を出すために2年分（730日強）取得
        raw_cpi = fred.get_series(FRB_METRICS["CPI"], observation_start='2024-01-01')
        raw_expect = fred.get_series(FRB_METRICS["EXPECT"])
        # --- [追加] Market Position 用のデータ取得 ---
        raw_10y = fred.get_series(FRB_METRICS["GS10"])
        raw_2y = fred.get_series("DGS2")
        raw_m2 = fred.get_series("M2SL", observation_start='2023-01-01')
        raw_ff = fred.get_series(FRB_METRICS["FF"])
        # --- [追加] People 用の失業率 ---
        raw_unrate = fred.get_series(FRB_METRICS["UNRATE"])

        # --- Future Focus ロジック計算 ---
        # ① 実体インフレ YoY の計算
        cpi_yoy = raw_cpi.pct_change(12).iloc[-1] * 100 # 12ヶ月前との比較(%)
        
        # ② 期待インフレの最新値
        expect_val = raw_expect.iloc[-1]
        
        # ③ スコア化（目標 2.0% からの乖離を 50倍で減点）
        cpi_score = max(0, 200 - abs(cpi_yoy - 2.0) * 50)
        expect_score = max(0, 200 - abs(expect_val - 2.0) * 50)
        
        # 合算して Future Focus (200点満点)
        future_focus_score = int((cpi_score + expect_score) / 2)

        # --- [Market Position] 2要素ロジック ---
        # ① Stability (100点満点): 10年債の直近20日のボラが低いほど良い
        yield_vol = raw_10y.diff().tail(20).std()
        stability_score = max(0, 100 - (yield_vol * 500))
        
        # ② Curve (100点満点): 10Y - 2Y が正常（プラス）なら満点、逆イールドなら減点
        curve_gap = raw_10y.iloc[-1] - raw_2y.iloc[-1]
        curve_score = max(0, min(100, 100 + (curve_gap * 100)))
        
        market_pos_score = int(stability_score + curve_score)

        # --- [Cashflow Quality] 通貨供給の均衡度 ---
        m2_yoy = raw_m2.pct_change(12).iloc[-1] * 100
        # 4.0%を理想とし、ズレるほど減点（4%ズレで100点減点）
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 30))

        # --- [追加] Financial Strength 実質利下げ余力 ---
        last_ff = raw_ff.iloc[-1]
        real_rate = last_ff - cpi_yoy
        # 実質金利が 4.0% で 200点満点、0%以下で 0点になる計算
        fin_strength_score = int(max(0, min(200, real_rate * 50)))

        # --- [People] 雇用の均衡度 ---
        last_unrate = raw_unrate.iloc[-1]
        # 4.0% を理想とし、そこからズレるほど減点（係数40で現実的な変動に対応）
        people_score = int(max(0, 200 - abs(last_unrate - 4.0) * 40))

        # --------------------------------------------------
        # スコア反映（ついに全5軸が完成！）
        # --------------------------------------------------
        company_axes = {
            "Future Focus": future_focus_score,
            "Market Position": market_pos_score,
            "Financial Strength": fin_strength_score,
            "Cashflow Quality": cashflow_score,
            "People": people_score 
        }
# --------------------------------------------------
        
        return {
            "axes": company_axes,
            "total": int(sum(company_axes.values())),
            "name": "FRB Composite",
            "price_hist": raw_expect.tail(1825), # 代表として期待インフレのチャートを表示
            "current_price": expect_val,
            "pe": "Macro",
            "market_cap": 0
        }

    except Exception as e:
        st.error(f"FRB Logic Error: {e}")
        return None

# data_logic.py の一番最後に貼り付け
@st.cache_data(ttl=86400)
def fetch_mas_logic():
    import requests
    import pandas as pd
    import streamlit as st

    # 🎯 2026年現在の SGS Yield Curve の Dataset ID
    SGS_ID = "d_91724f72836261541f5343f8e5b4e073" 
    
    # 🎯 v2 API の正規エンドポイント
    url = f"https://api.data.gov.sg/v2/public/api/datasets/{SGS_ID}/data?limit=5"

    try:
        # --- 🔍 診断フェーズ ---
        res = requests.get(url, timeout=10)
        
        st.write("--- 🛠 MAS API DIAGNOSIS ---")
        st.write(f"📡 Status Code: {res.status_code}")
        
        if res.status_code != 200:
            st.error(f"Failed to connect. Error: {res.text[:200]}")
            return None

        # --- 📊 データ解析フェーズ ---
        raw_json = res.json()
        
        # JSONの中身を画面に出して、正しいキー名を特定する
        st.success("Connection Success! Reviewing JSON structure...")
        st.json(raw_json) 

        # records を取り出す
        records = raw_json.get("data", {}).get("records", [])
        
        if not records:
            st.warning("No records found in this dataset.")
            return None

        # 🚀 ここで「10_year_bond_yield」という名前が正しいか自動チェック
        first_row = records[0]
        st.write("Current Keys found in data:", list(first_row.keys()))

        # --- 📈 均衡ロジック計算 (暫定) ---
        # 正しいキーが見つかれば計算、なければ仮の数値で描画を止めない
        y_10y = float(first_row.get("10_year_bond_yield", 2.8)) # 見つからなければ 2.8
        
        mas_axes = {
            "Future Focus": 175, 
            "Market Position": 160,
            "Financial Strength": 165,
            "Cashflow Quality": 150,
            "People": 180
        }

        return {
            "axes": mas_axes,
            "total": int(sum(mas_axes.values())),
            "name": "MAS Composite (Singapore)",
            "price_hist": pd.Series([r.get("10_year_bond_yield", 2.8) for r in records][::-1]),
            "current_price": y_10y,
            "pe": "SG-SGS",
            "market_cap": 0
        }

    except Exception as e:
        st.error(f"Critical Logic Error: {e}")
        return None