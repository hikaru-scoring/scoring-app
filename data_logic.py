# data_logic.py
import pandas as pd
import yfinance as yf
import streamlit as st

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
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 25))
        # --- [Cashflow Quality] 通貨供給の均衡度 ---
        m2_yoy = raw_m2.pct_change(12).iloc[-1] * 100
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 25))

        # --- [追加] Financial Strength 実質利下げ余力 ---
        last_ff = raw_ff.iloc[-1]
        real_rate = last_ff - cpi_yoy
        # 実質金利が 4.0% で 200点満点、0%以下で 0点になる計算
        fin_strength_score = int(max(0, min(200, real_rate * 50)))
        # --------------------------------------------------
        # スコア反映（最新版）
        # --------------------------------------------------
        company_axes = {
            "Future Focus": future_focus_score,
            "Market Position": market_pos_score,
            "Financial Strength": fin_strength_score,
            "Cashflow Quality": cashflow_score, # 🚀 通貨均衡スコアを反映！
            "People": 125 
        }

        # --------------------------------------------------
        # ※現時点では他の軸は仮置き、もしくは既存の DGS10 等を使用
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