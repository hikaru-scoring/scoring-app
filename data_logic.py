import pandas as pd
import streamlit as st
from fredapi import Fred
import io
import requests

# --------------------------------------------------
# 🏛️ 1. FRBスコア専用ロジック（聖域：一切変えない）
# --------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_frb_logic(name):
    try:
        fred_key = st.secrets["FRED_API_KEY"]
        fred = Fred(api_key=fred_key)

        # データの取得
        raw_cpi = fred.get_series("CPIAUCSL", observation_start='2024-01-01')
        raw_expect = fred.get_series("T10YIE")
        raw_10y = fred.get_series("DGS10")
        raw_2y = fred.get_series("DGS2")
        raw_m2 = fred.get_series("M2SL", observation_start='2023-01-01')
        raw_ff = fred.get_series("FEDFUNDS")
        raw_unrate = fred.get_series("UNRATE")

        # 計算
        cpi_yoy = raw_cpi.pct_change(12).iloc[-1] * 100
        expect_val = raw_expect.iloc[-1]
        cpi_score = max(0, 200 - abs(cpi_yoy - 2.0) * 50)
        expect_score = max(0, 200 - abs(expect_val - 2.0) * 50)
        future_focus_score = int((cpi_score + expect_score) / 2)
        
        yield_vol = raw_10y.diff().tail(20).std()
        stability_score = max(0, 100 - (yield_vol * 500))
        curve_gap = raw_10y.iloc[-1] - raw_2y.iloc[-1]
        curve_score = max(0, min(100, 100 + (curve_gap * 100)))
        market_pos_score = int(stability_score + curve_score)

        m2_yoy = raw_m2.pct_change(12).iloc[-1] * 100
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 30))
        real_rate = raw_ff.iloc[-1] - cpi_yoy
        fin_strength_score = int(max(0, min(200, real_rate * 50)))
        people_score = int(max(0, 200 - abs(raw_unrate.iloc[-1] - 4.0) * 40))

        axes = {
            "Future Focus": future_focus_score,
            "Market Position": market_pos_score,
            "Financial Strength": fin_strength_score,
            "Cashflow Quality": cashflow_score,
            "People": people_score 
        }
        return {
            "axes": axes, "total": int(sum(axes.values())), "name": name,
            "price_hist": raw_expect.tail(252), "current_price": raw_10y.iloc[-1],
            "pe": "Macro", "market_cap": 0
        }
    except Exception as e:
        st.error(f"FRB Logic Error: {e}")
        return None

# --------------------------------------------------
# 🛢️ 2. コモディティ専用ロジック（Stooqからデータを取る）
# --------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_commodity_logic(symbol, name):
    
    try:
        # symbolをStooqが受け付けやすい形式（末尾 _f）に変換
        mapping = {"cl.f": "cl.w", "ng.f": "ng.w", "gc.f": "gc.w", "si.f": "si.w", "hg.f": "hg.w"}
        stooq_symbol = symbol.lower().replace(".f", "_f")
        url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()

        if not res.text or "Date" not in res.text: return None
        df = pd.read_csv(io.StringIO(res.text))

        df = pd.read_csv(io.StringIO(res.text))
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date").sort_index()
        if df.empty: return None
        df = df.sort_index().tail(252)
        
        price_hist = df['Close']
        high_hist = df['High']
        low_hist = df['Low']
        vol_hist = df['Volume']
        
        current_price = price_hist.iloc[-1]
        price_1y_ago = price_hist.iloc[0]
        price_25d_avg = price_hist.tail(25).mean()

        # FRS-1000 スコア計算
        score_1 = max(0, min(200, (current_price / price_1y_ago - 1) * 500 + 100))
        score_2 = max(0, min(200, (current_price / price_25d_avg - 1) * 1000 + 100))
        
        daily_range = high_hist - low_hist
        score_3 = max(0, min(200, (daily_range.mean() / daily_range.tail(5).mean() * 100))) if daily_range.tail(5).mean() > 0 else 100
        
        avg_vol = vol_hist.tail(20).mean()
        score_4 = max(0, min(200, (vol_hist.iloc[-1] / avg_vol * 100))) if avg_vol > 0 else 100
        
        p_range = price_hist.max() - price_hist.min()
        score_5 = max(0, min(200, (current_price - price_hist.min()) / p_range * 200)) if p_range > 0 else 100

        axes = {
            "Annual Trajectory": score_1, "Relative Momentum": score_2,
            "Structural Stress": score_3, "Liquidity Energy": score_4, "Cycle Equilibrium": score_5
        }
        return {
            "axes": axes, "total": sum(axes.values()), "name": name, "symbol": symbol,
            "price_hist": price_hist, "current_price": current_price,
            "pe": "N/A", "market_cap": 0
        }
    except Exception as e:
        st.error(f"Commodity Error: {e}")
        return None

# --------------------------------------------------
# 📡 3. ルーター（受付窓口：app.pyからはここだけを呼ぶ）
# --------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_data(symbol, name):
    if symbol == "^TNX":
        return fetch_frb_logic(name)
    else:
        return fetch_commodity_logic(symbol, name)

def fetch_oil_data():
    return fetch_data("CL.F", "WTI CRUDE OIL")