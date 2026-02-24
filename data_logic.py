# data_logic.py
import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=43200)
def fetch_data(symbol, name):
    """
    Financial Modeling Prep (FMP) APIを使用してシンガポール株のデータを取得し、
    5つの独自指標で分析スコアを算出する。
    """
    import requests
    api_key = "7kX25WsxViDvI1nTaGHUx9NV1hIBRRQR"
    
    # ティッカーの整形
    ticker_symbol = f"{symbol}.SI" if not symbol.endswith(".SI") else symbol

    # APIエンドポイントの設定
    quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker_symbol}?apikey={api_key}"
    metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker_symbol}?period=annual&limit=1&apikey={api_key}"
    cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker_symbol}?period=annual&limit=1&apikey={api_key}"
    enterprise_url = f"https://financialmodelingprep.com/api/v3/enterprise-values/{ticker_symbol}?period=annual&limit=1&apikey={api_key}"
    history_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker_symbol}?timeseries=260&apikey={api_key}"

    try:
        # 各データの取得
        quote_res = requests.get(quote_url).json()
        metrics_res = requests.get(metrics_url).json()
        cashflow_res = requests.get(cashflow_url).json()
        history_res = requests.get(history_url).json()

        if not quote_res or not metrics_res or not cashflow_res or not history_res:
            return None

        # データの展開
        quote = quote_res[0]
        metrics = metrics_res[0]
        cashflow = cashflow_res[0]
        
        # 株価履歴をpandas Seriesに変換（yfinance互換）
        hist_df = pd.DataFrame(history_res['historical'])
        hist_df['date'] = pd.to_datetime(hist_df['date'])
        hist_df.set_index('date', inplace=True)
        hist_series = hist_df['close'].sort_index()

        # 基本数値の抽出
        last_price = quote.get("price")
        avg_price = hist_series.mean()
        max_price = hist_series.max()
        volatility = hist_series.pct_change().std() * 100
        m_cap = quote.get("marketCap") or 0
        
        # 指標の抽出
        per = metrics.get("peRatio")
        debt = metrics.get("debtToEquity")
        fcf = cashflow.get("freeCashFlow") or 0
        revenue = quote.get("revenue") or 1 # 万が一のために1を代入
        roe = metrics.get("roe") or 0
        eps_growth = metrics.get("earningsYield") or 0 # EPS成長の代わりに収益率を参考

        # --- 🚀 鉄壁プロトタイプ・ロジック（FMPデータ適用版） ---
        valid_scores = {}

        # 1. Future Focus
        if per:
            per_factor = max(0.5, 1.5 - (per / 40))
            valid_scores["Future Focus"] = min(int((last_price / avg_price) * 100 * per_factor), 200)

        # 2. Market Position
        if m_cap:
            cap_factor = (m_cap / 1e11) + 0.5
            valid_scores["Market Position"] = min(int((100 + (volatility * 10)) * cap_factor), 200)

        # 3. Financial Strength
        if debt:
            debt_factor = max(0.5, 1.5 - (debt / 200))
            valid_scores["Financial Strength"] = min(int((last_price / max_price) * 150 * debt_factor), 200)

        # 4. Cashflow Quality
        fcf_margin = fcf / (m_cap if m_cap > 0 else 1) # 時価総額比で代替
        c_score = fcf_margin * 2000
        valid_scores["Cashflow Quality"] = int(min(max(c_score, 0), 200))

        # 5. People
        roe_score = min(max(roe * 100 * 10, 0), 200)
        eps_score = min(max(eps_growth * 100 * 20, 0), 200)
        people_raw = (roe_score * 0.7) + (eps_score * 0.3)
        valid_scores["People"] = int(min(people_raw, 200))

        # --- 🚀 200点張り付き解消ロジック ---
        AXES_LIST = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
        company_axes = {}
        for k in AXES_LIST:
            val = valid_scores.get(k)
            if val is not None and val != 0:
                company_axes[k] = int(min(val * 0.85, 195)) 
            else:
                company_axes[k] = 100
        
        total_score = int(sum(company_axes.values()))

        return {
            "axes": company_axes,
            "total": total_score,
            "name": name,
            "price_hist": hist_series,
            "current_price": last_price,
            "pe": per if per else "N/A",
            "market_cap": m_cap
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