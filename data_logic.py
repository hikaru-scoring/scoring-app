# data_logic.py
import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=43200)
def fetch_data(symbol, name):
    import requests
    import pandas as pd
    # 光さんの2つの武器（キー）
    eod_key = st.secrets["EODHD_API_KEY"]
    
    symbol_tw = f"{symbol}" 

    try:
        # 1. 【株価】Twelve Dataから取得（これは確実に取れます）
        h_url = f"https://eodhistoricaldata.com/api/eod/{symbol}.SI?api_token={eod_key}&fmt=json"
        h_res = requests.get(h_url, timeout=15).json()
        st.write("DEBUG h_res:", h_res)
        if not isinstance(h_res, list) or len(h_res) == 0:
            eturn None
        
        # 2. 【財務データ】FMPの無料枠で限界まで挑戦！
        # 比較的ロックがゆるい 'key-metrics-ttm' を狙います
        m_data = {}

        # 3. データの成形（Twelve Data用）
        df = pd.DataFrame(h_res)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        hist_series = df.dropna(subset=["date","close"]).set_index("date")["close"].sort_index()

        # 各種数値の抽出（データがなければ0や1.0を代入して計算停止を防ぐ）
        last_price = float(hist_series.iloc[-1])
        avg_price = hist_series.mean()
        max_price = hist_series.max()
        volatility = hist_series.pct_change().std() * 100
        
        # --- ここがチャレンジ箇所！本物のデータを狙う ---
        per = m_data.get("peRatioTTM")
        roe = m_data.get("roeTTM")
        debt = m_data.get("debtEquityRatioTTM")
        fcf_yield = m_data.get("freeCashFlowYieldTTM")

        # --- 4. スコア計算（データがある時だけ反映、なければ安全な値で計算） ---
        valid_scores = {}
        # 将来性 (PERがあれば反映)
        valid_scores["Future Focus"] = min(int((last_price / avg_price) * 100 * (max(0.5, 1.5 - (per / 40)) if per else 1.0)), 200)
        # 市場性
        valid_scores["Market Position"] = min(int(100 + (volatility * 10)), 200)
        # 財務健全性 (負債比率があれば反映)
        valid_scores["Financial Strength"] = min(int((last_price / max_price) * 150 * (max(0.5, 1.5 - (debt / 2)) if debt else 1.0)), 200)
        # キャッシュフロー (FCF利回りがあれば反映)
        valid_scores["Cashflow Quality"] = int(min(max(fcf_yield * 1000, 0), 200)) if fcf_yield else 120
        # 人材・経営 (ROEがあれば反映)
        valid_scores["People"] = int(min(roe * 500, 200)) if roe else 100

        AXES_LIST = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
        company_axes = {k: int(min(valid_scores.get(k, 100) * 0.85, 195)) for k in AXES_LIST}
        
        return {
            "axes": company_axes,
            "total": int(sum(company_axes.values())),
            "name": name,
            "price_hist": hist_series,
            "current_price": last_price,
            "pe": per if per else "N/A",
            "market_cap": 0
        }
    except Exception:
        return None
# data_logic.py の末尾に追記

@st.cache_data(ttl=3600)
def fetch_oil_data():
    """WTI原油先物データを取得し、動的なマーケットスコアに変換する"""
    import time   # ← この1行を必ずここに追加してください！
    time.sleep(1) 
    ticker = yf.Ticker("CL=F")
    try:
        # この下の行の左側に、必ず半角スペースが「8個」入っている必要があります
        hist = ticker.history(period="1y")
        if hist.empty:
            return None
        
        # --- 本物志向の計算ロジック ---
        last_price = hist['Close'].iloc[-1]
        avg_price = hist['Close'].mean()
        max_price = hist['Close'].max()
        volatility = hist['Close'].pct_change().std() * 100 
        
        # 概念ペア・ロジック
        demand_score = (last_price / avg_price) * 100
        geo_risk_score = 100 + (volatility * 15)
        price_level_score = (last_price / max_price) * 150
        # 1. まず「recent_volatility」を計算して定義する（これが抜けていました）
        recent_volatility = hist['Close'].pct_change().rolling(window=20).std().iloc[-1] * 100

        # 2. 定義した後に、それを使ってスコアを出す
        supply_stability = max(50, 180 - (recent_volatility * 40))
        market_heat_score = (last_price / hist['Close'].iloc[0]) * 120

        oil_axes = {
            "Future Focus": min(demand_score, 200),
            "Market Position": min(geo_risk_score, 200),
            "Financial Strength": min(price_level_score, 200),
            "Cashflow Quality": supply_stability,
            "People": min(market_heat_score, 200)
        }

        # 5つの指標の合計を計算
        
        total_score = int(sum(oil_axes.values()))

        return {
            "axes": oil_axes,
            "total": total_score,
            "name": "WTI CRUDE OIL", # 直接名前を書く
            "price_hist": hist['Close'],
            "current_price": last_price,
            "pe": 0,
            "market_cap": 0
        }
    except Exception:
        return None