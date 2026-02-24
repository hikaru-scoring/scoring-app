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
    import pandas as pd
    api_key = "7kX25WsxViDvI1nTaGHUx9NV1hIBRRQR"
    
    # 1. ティッカー成形
    symbol_si = f"{symbol}.SI" if not symbol.endswith(".SI") else symbol

    # 2. APIからデータを取得（yfinanceの代わりにrequestsを使用）
    base_url = "https://financialmodelingprep.com/api/v3"
    try:
        # Quote（株価・時価総額）
        q_data = requests.get(f"{base_url}/quote/{symbol_si}?apikey={api_key}").json()[0]
        # Metrics（PER, ROE, Debt/Equity）
        m_data = requests.get(f"{base_url}/key-metrics/{symbol_si}?period=annual&limit=1&apikey={api_key}").json()[0]
        # CashFlow（FCF）
        c_data = requests.get(f"{base_url}/cash-flow-statement/{symbol_si}?period=annual&limit=1&apikey={api_key}").json()[0]
        # History（1年分の株価履歴）
        h_res = requests.get(f"{base_url}/historical-price-full/{symbol_si}?timeseries=260&apikey={api_key}").json()
        
        # 履歴データの成形
        df = pd.DataFrame(h_res['historical'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        hist_series = df['close'].sort_index()

        # 変数の抽出
        last_price = q_data.get("price", 0)
        avg_price = hist_series.mean()
        max_price = hist_series.max()
        volatility = hist_series.pct_change().std() * 100
        m_cap = q_data.get("marketCap", 0)
        per = m_data.get("peRatio")
        debt = m_data.get("debtToEquity")
        roe = m_data.get("roe", 0)
        eps_growth = m_data.get("earningsYield", 0)
        fcf = c_data.get("freeCashFlow", 0)

        # 3. 元のロジックにデータを流し込む
        valid_scores = {}
        
        # Future Focus
        if per:
            per_factor = max(0.5, 1.5 - (per / 40))
            valid_scores["Future Focus"] = min(int((last_price / avg_price) * 100 * per_factor), 200)
        
        # Market Position
        if m_cap > 0:
            cap_factor = (m_cap / 1e11) + 0.5
            valid_scores["Market Position"] = min(int((100 + (volatility * 10)) * cap_factor), 200)
        
        # Financial Strength
        if debt:
            debt_factor = max(0.5, 1.5 - (debt / 200))
            valid_scores["Financial Strength"] = min(int((last_price / max_price) * 150 * debt_factor), 200)
        
        # Cashflow Quality
        fcf_margin = fcf / (m_cap if m_cap > 0 else 1)
        valid_scores["Cashflow Quality"] = int(min(max(fcf_margin * 2000, 0), 200))
        
        # People
        roe_score = min(max(roe * 100 * 10, 0), 200)
        eps_score = min(max(eps_growth * 100 * 20, 0), 200)
        valid_scores["People"] = int(min((roe_score * 0.7) + (eps_score * 0.3), 200))

        # スケーリング調整
        AXES_LIST = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
        company_axes = {k: int(min(valid_scores.get(k, 100) * 0.85, 195)) for k in AXES_LIST}
        
        return {
            "axes": company_axes,
            "total": int(sum(company_axes.values())),
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