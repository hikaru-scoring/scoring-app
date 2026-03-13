# data_logic.py
import pandas as pd
import yfinance as yf
import streamlit as st
from fredapi import Fred

@st.cache_data(ttl=86400, persist="disk")
def fetch_data(symbol, name):
    """
    株価データと分析スコアを取得する関数。
    app.pyから呼び出される心臓部。
    """
    # 修正：ランダムな1.0〜3.0秒の待機を入れてブロック回避
    import time
    import random
    time.sleep(random.uniform(1.0, 3.0)) 
    
    ticker = yf.Ticker(f"{symbol}.SI")
    try:

        hist = ticker.history(period="5y")
        
        if hist.empty: return None
        
        # --- ここから追記 ---
        last_price = hist['Close'].iloc[-1]
        avg_price = hist['Close'].mean()
        max_price = hist['Close'].max()
        volatility = hist['Close'].pct_change().std() * 100 
        # --- ここまで ---

        # --- ハイブリッド計算ロジック（株価 × 財務） ---
        # 修正：高速なfast_infoを優先し、重いinfoは失敗しても無視して続行する
        try:
            f_info = ticker.fast_info
            m_cap = f_info.get('marketCap') or 0
        except:
            m_cap = 0

        try:
            info = ticker.info
            if not isinstance(info, dict):
                info = {}
        except:
            info = {}
        
        # --- 🚀 鉄壁プロトタイプ・ロジック（欠損カバー版） ---
        valid_scores = {}

        # 1. Future Focus
        per = info.get('forwardPE') or info.get('trailingPE')
        if per:
            per_factor = max(0.5, 1.5 - (per / 40))
            valid_scores["Future Focus"] = min(int((last_price / avg_price) * 100 * per_factor), 200)

        # 2. Market Position
        m_cap = info.get('marketCap')
        if m_cap:
            cap_factor = (m_cap / 1e11) + 0.5
            valid_scores["Market Position"] = min(int((100 + (volatility * 10)) * cap_factor), 200)

        # 3. Financial Strength
        debt = info.get('debtToEquity')
        if debt:
            debt_factor = max(0.5, 1.5 - (debt / 200))
            valid_scores["Financial Strength"] = min(int((last_price / max_price) * 150 * debt_factor), 200)

        # --- 4. Cashflow Quality (FCF Margin ベース) ---
        fcf = info.get('freeCashflow', 0) or 0
        revenue = info.get('totalRevenue', 1)  # 0除算防止

        fcf_margin = fcf / revenue  # 例：0.12（12%）
        c_score = fcf_margin * 2000  # 10% → 200点

        valid_scores["Cashflow Quality"] = int(min(max(c_score, 0), 200))

        # 5. People (経営の質：ROE 70% × EPS成長 30% の比重へ)
        # ROEは「経営の効率」、EPS成長は「経営の結果」を意味します
        roe = info.get('returnOnEquity', 0) or 0
        eps_growth = info.get('earningsGrowth', 0) or 0

        # ROE 10%で100点、EPS成長5%で100点を目指すスケーリング
        roe_score = min(max(roe * 100 * 10, 0), 200)
        eps_score = min(max(eps_growth * 100 * 20, 0), 200)

        # 【経営の質重視】比率を 0.7 : 0.3 に設定
        people_raw = (roe_score * 0.7) + (eps_score * 0.3)
        valid_scores["People"] = int(min(people_raw, 200))

        # --- 🚀 200点張り付きを解消し、銘柄の「差」を出す代入ロジック ---
        AXES_LIST = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
        company_axes = {}
        
        for k in AXES_LIST:
            val = valid_scores.get(k)
            if val is not None and val != 0:
                # 0.85倍のスケーリングで185点固定を破壊し、バラツキを作ります
                company_axes[k] = int(min(val * 0.85, 195)) 
            else:
                # データがない、あるいは0の場合は「100（標準）」
                company_axes[k] = 100
        
        # 合計スコアの算出
        total_score = int(sum(company_axes.values()))
        return {
            "axes": company_axes,
            "total": total_score,
            "name": name,
            "price_hist": hist['Close'],
            "current_price": last_price,
            "pe": per if per else "N/A",
            "market_cap": m_cap if m_cap else 0
        }
    except Exception:
        return None

# data_logic.py の末尾に追記

@st.cache_data(ttl=86400, persist="disk")
def fetch_oil_data():
    """WTI原油先物データを取得し、動的なマーケットスコアに変換する"""
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
    except Exception as e:
        st.error(f"Oil Data Error: {e}")
        return None

def _worldbank_fetch(indicator, country="SGP"):
    """World Bank APIから最新値を取得して返す（float）"""
    import requests
    try:
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv=5&per_page=5"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2 or not data[1]:
            return None
        for entry in data[1]:
            if entry.get("value") is not None:
                return float(entry["value"])
        return None
    except Exception:
        return None


def _fetch_mas_data():
    """MAS用データをWorld Bank + FREDから取得する"""
    # --- World Bank: CPI年次変化率(%) ---
    cpi_yoy = _worldbank_fetch("FP.CPI.TOTL.ZG")
    # --- World Bank: 失業率(%) ---
    latest_unemployment = _worldbank_fetch("SL.UEM.TOTL.ZS")

    if cpi_yoy is None or latest_unemployment is None:
        st.error("MAS Data Error: World Bank fetch failed")
        return None

    # --- FRED: 10年債・短期金利（取れなければNone） ---
    fred_key = st.secrets["FRED_API_KEY"]
    fred = Fred(api_key=fred_key)
    y10, y2 = None, None
    try:
        s = fred.get_series("IRLTLT01SGM156N").dropna()
        if not s.empty:
            y10 = s
    except Exception:
        pass
    try:
        s = fred.get_series("IR3TIB01SGM156N").dropna()
        if not s.empty:
            y2 = s
    except Exception:
        pass

    try:
        latest_y10 = float(y10.iloc[-1]) if y10 is not None else None
        latest_y2  = float(y2.iloc[-1])  if y2  is not None else None
        y10_vol    = float(y10.tail(20).std()) if y10 is not None and len(y10) >= 20 else None

        price_stability = float(max(0, min(200, 200 - abs(cpi_yoy - 2) * 20)))
        employment      = float(max(0, min(200, 200 - latest_unemployment * 15)))
        liquidity       = 100.0  # M2データ取得不可のため中立値
        monetary_policy = float(max(0, min(200, 100 + (latest_y10 - latest_y2) * 30))) \
                          if latest_y10 is not None and latest_y2 is not None else 100.0
        market_stability= float(max(0, min(200, 200 - y10_vol * 100))) \
                          if y10_vol is not None else 100.0

        cb_axes = {
            "Price Stability": price_stability,
            "Employment":      employment,
            "Monetary Policy": monetary_policy,
            "Liquidity":       liquidity,
            "Market Stability":market_stability,
        }
        return {
            "name":         "MAS",
            "axes":         cb_axes,
            "total":        int(sum(cb_axes.values())),
            "y10":          latest_y10,
            "y2":           latest_y2,
            "cpi_yoy":      cpi_yoy,
            "unemployment": latest_unemployment,
            "m2_yoy":       None,
            "y10_vol":      y10_vol,
            "curve":        float(latest_y10 - latest_y2) if latest_y10 is not None and latest_y2 is not None else None,
            "y10_hist":     y10,
        }
    except Exception as e:
        st.error(f"MAS Data Error: {e}")
        return None


@st.cache_data(ttl=86400)
def fetch_central_bank_data(bank):
    """
    FREDから中央銀行スコア用の主要マクロ指標を取得する。
    返り値は app.py でそのまま使える辞書。
    """
    if bank == "MAS":
        return _fetch_mas_data()

    fred_key = st.secrets["FRED_API_KEY"]
    fred = Fred(api_key=fred_key)

    # 中央銀行ごとのFRED series
    series_map = {
        "Federal Reserve": {
            "y10": "DGS10",
            "y2": "DGS2",
            "cpi": "CPIAUCSL",
            "unemployment": "UNRATE",
            "m2": "M2SL",
        },
        "European Central Bank": {
            "y10": "IRLTLT01EZM156N",
            "y2": "IR3TIB01EZM156N",
            "cpi": "CP0000EZ19M086NEST",
            "unemployment": "LRHUTTTTEZM156S",
            "m2": "MYAGM2EZM196N",
        },
        "Bank of Japan": {
            "y10": "IRLTLT01JPM156N",
            "y2": "IR3TIB01JPM156N",
            "cpi": "JPNCPIALLMINMEI",
            "unemployment": "LRHUTTTTJPM156S",
            "m2": "MYAGM2JPM189N",
        },
        "Bank of England": {
            "y10": "IRLTLT01GBM156N",
            "y2": "IR3TIB01GBM156N",
            "cpi": "GBRCPIALLMINMEI",
            "unemployment": "LRHUTTTTGBM156S",
            "m2": "MABMM301GBM189S",
        },
        "MAS": {
            "y10": "IRLTLT01SGM156N",
            "y2": "IR3TIB01SGM156N",
            "cpi": "SGPCPIALLMINMEI",
            "unemployment": "LRHUTTTTSGM156S",
            "m2": "MYAGM2SGM189N",
        },
    }

    try:
        ids = series_map[bank]

        y10 = fred.get_series(ids["y10"]).dropna()
        y2 = fred.get_series(ids["y2"]).dropna()
        cpi = fred.get_series(ids["cpi"]).dropna()
        unemployment = fred.get_series(ids["unemployment"]).dropna()
        m2 = fred.get_series(ids["m2"]).dropna()

        if y10.empty or y2.empty or cpi.empty or unemployment.empty or m2.empty:
            return None

        # --- 最新値 ---
        latest_y10 = float(y10.iloc[-1])
        latest_y2 = float(y2.iloc[-1])
        latest_unemployment = float(unemployment.iloc[-1])

        # --- CPI YoY ---
        if len(cpi) < 13:
            return None
        cpi_yoy = ((cpi.iloc[-1] / cpi.iloc[-13]) - 1) * 100

        # --- M2 YoY ---
        if len(m2) < 13:
            return None
        m2_yoy = ((m2.iloc[-1] / m2.iloc[-13]) - 1) * 100

        # --- 10Y volatility ---
        y10_vol = y10.tail(20).std() if len(y10) >= 20 else y10.std()

        # --- Axes スコア計算 ---
        price_stability = float(max(0, min(200, 200 - abs(float(cpi_yoy) - 2) * 20)))
        employment      = float(max(0, min(200, 200 - latest_unemployment * 15)))
        monetary_policy = float(max(0, min(200, 100 + (latest_y10 - latest_y2) * 30)))
        liquidity       = float(max(0, min(200, 200 - abs(float(m2_yoy) - 5) * 10)))
        market_stability= float(max(0, min(200, 200 - float(y10_vol) * 100)))

        cb_axes = {
            "Price Stability": price_stability,
            "Employment":      employment,
            "Monetary Policy": monetary_policy,
            "Liquidity":       liquidity,
            "Market Stability":market_stability,
        }

        return {
            "name": bank,
            "axes": cb_axes,
            "total": int(sum(cb_axes.values())),
            "y10": latest_y10,
            "y2": latest_y2,
            "cpi_yoy": float(cpi_yoy),
            "unemployment": latest_unemployment,
            "m2_yoy": float(m2_yoy),
            "y10_vol": float(y10_vol),
            "curve": float(latest_y10 - latest_y2),
            "y10_hist": y10,
        }

    except Exception as e:
        st.error(f"Central Bank Data Error: {e}")
        return None        