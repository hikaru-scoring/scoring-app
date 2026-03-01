# data_logic.py
import pandas as pd
import yfinance as yf
import streamlit as st

def fetch_data(symbol, name):
    import pandas as pd
    import yfinance as yf
    import streamlit as st
    
    # 🏛️ 中央銀行・金利指標の管理（FREDを使用）
    # シンボルが ^TNX (米国10年債利回り) の場合はFREDから取得する設定
    CENTRAL_BANK_SERIES = {
        "^TNX": "DGS10"
    }

    try:
        # 1. データ取得ルートの分岐
        if symbol in CENTRAL_BANK_SERIES:
            from fredapi import Fred
            # StreamlitのSecretsからAPIキーを取得
            fred_key = st.secrets["FRED_API_KEY"]
            fred = Fred(api_key=fred_key)
            
            series_id = CENTRAL_BANK_SERIES[symbol]
            # FREDから米国10年債データを取得
            raw_series = fred.get_series(series_id)
            
            if raw_series.empty:
                return None
                
            raw_series.index = pd.to_datetime(raw_series.index)
            # データを日次に引き伸ばし、直近365日分を抽出
            hist_series = raw_series.resample('D').ffill().tail(365)
            
        else:
            # コモディティ（金・銅・原油）やビットコインは yfinance で取得
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if hist.empty:
                return None
            hist_series = hist['Close']

        # 2. 共通の計算準備
        last_price = float(hist_series.iloc[-1])
        avg_price = hist_series.mean()
        max_price = hist_series.max()
        # ボラティリティ（価格変動の激しさ）を計算
        volatility = hist_series.pct_change().std() * 100

        # 3. マクロスコアリングロジック（思想の部分）
        valid_scores = {
            "Future Focus": min(int((last_price / avg_price) * 100), 200),
            "Market Position": min(int(150 - (volatility * 10)), 200),
            "Financial Strength": min(int((last_price / max_price) * 150), 200),
            "Cashflow Quality": 140, # 流動性指標として固定
            "People": 125           # 市場信頼度として固定
        }

        AXES_LIST = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
        # 全体のバランスを調整して195点満点に収める
        company_axes = {k: int(min(valid_scores.get(k, 100) * 0.85, 195)) for k in AXES_LIST}
        
        return {
            "axes": company_axes,
            "total": int(sum(company_axes.values())),
            "name": name,
            "price_hist": hist_series,
            "current_price": last_price,
            "pe": "Macro",
            "market_cap": 0
        }
    except Exception as e:
        # 予期せぬエラーが起きた場合は画面に表示してNoneを返す
        st.error(f"Logic Error for {name}: {e}")
        return None
# data_logic.py の末尾に追記

def fetch_oil_data():
    """WTI原油先物データを取得し、動的なマーケットスコアに変換する"""
    import time   # ← この1行を必ずここに追加してください！
    time.sleep(1) 
    ticker = yf.Ticker("CL=F")
    try:
        # この下の行の左側に、必ず半角スペースが「8個」入っている必要があります
        hist = ticker.history(period="1y")
        st.write("DEBUG OIL EMPTY:", hist.empty)
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
    except Exception as e:
        st.write("🔥 ERROR INSIDE FETCH:", e)
        return None