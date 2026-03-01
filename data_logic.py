# data_logic.py
import pandas as pd
import yfinance as yf
import streamlit as st

def fetch_data(symbol, name):
    import pandas as pd
    import yfinance as yf
    import streamlit as st
    
    try:
        # 1. データ取得ルートの分岐（FRED vs yfinance）
        if symbol == "SG10Y":
            from fredapi import Fred
            # 🚀 StreamlitのSecretsに保存したFREDのキーを呼び出す
            fred_key = st.secrets["bd0ca525203b9393ffdaba745ee4dff9"]
            fred = Fred(api_key=fred_key)
            
            # シンガポール長期金利の取得（FREDのID: IRLTLT01SGM156N）
            raw_series = fred.get_series('IRLTLT01SGM156N')
            raw_series.index = pd.to_datetime(raw_series.index)
            # 月次データを日次に引き伸ばし、直近260日分（約1年分）を抽出してチャートを滑らかにする
            hist_series = raw_series.resample('D').ffill().tail(260)
            
        else:
            # その他マクロ資産（金、銅、米10年債など）は yfinance で取得
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if hist.empty:
                return None
            hist_series = hist['Close']

        # 2. 共通の計算準備
        last_price = float(hist_series.iloc[-1])
        avg_price = hist_series.mean()
        max_price = hist_series.max()
        volatility = hist_series.pct_change().std() * 100

        # 3. マクロスコアリング計算（UIを崩さないため、キー名は株用を維持）
        valid_scores = {}
        
        # 将来性 (マクロのMomentumとして計算)
        valid_scores["Future Focus"] = min(int((last_price / avg_price) * 100), 200)
        
        # 市場性 (マクロのStabilityとして計算：ボラティリティが低いほど高得点)
        valid_scores["Market Position"] = min(int(150 - (volatility * 10)), 200)
        
        # 財務健全性 (マクロのPotentialとして計算)
        valid_scores["Financial Strength"] = min(int((last_price / max_price) * 150), 200)
        
        # キャッシュフロー & 人材 (マクロ向けの固定ベーススコア + 変動)
        valid_scores["Cashflow Quality"] = 140
        valid_scores["People"] = 125

        AXES_LIST = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
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
        st.write("🔥 ERROR INSIDE FETCH:", e)
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