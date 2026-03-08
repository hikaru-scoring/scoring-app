import pandas as pd
import streamlit as st
from fredapi import Fred
import requests

@st.cache_data(ttl=86400)
def fetch_central_bank_data(symbol, name):
    try:
        fred_key = st.secrets["FRED_API_KEY"]
        fred = Fred(api_key=fred_key)

        # --- データ取得 ---
        if symbol == "^TNX":
            # アメリカ：全て FRED
            raw_cpi = fred.get_series("CPIAUCSL", observation_start='2018-01-01')
            raw_10y = fred.get_series("DGS10")
            raw_2y = fred.get_series("DGS2")
            raw_m2 = fred.get_series("M2SL", observation_start='2018-01-01')
            raw_rate = fred.get_series("FEDFUNDS")
            raw_unrate = fred.get_series("UNRATE")
        else:
            return None

        # --- スコア計算 ---
        cpi_yoy_series = raw_cpi.pct_change(4).dropna()
        if cpi_yoy_series.empty:
            return None

        cpi_yoy = cpi_yoy_series.iloc[-1] * 100
        cpi_score = max(0, 200 - abs(cpi_yoy - 2.0) * 50)
        
        yield_vol = raw_10y.diff().tail(20).std()
        stability_score = max(0, 100 - (yield_vol * 500))
        curve_gap = raw_10y.iloc[-1] - raw_2y.iloc[-1]
        curve_score = max(0, min(100, 100 + (curve_gap * 100)))

        m2_yoy = raw_m2.pct_change(12).dropna().iloc[-1] * 100
        cashflow_score = int(max(0, 200 - abs(m2_yoy - 4.0) * 30))
        real_rate = raw_rate.iloc[-1] - cpi_yoy
        fin_strength_score = int(max(0, min(200, real_rate * 50)))
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
        st.error(f"Error: {e}")
        return None

def fetch_sg_cpi():

    import requests
    import pandas as pd

    url = "https://tablebuilder.singstat.gov.sg/api/table/tabledata/M212261"

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = response.json()

    rows = data["Data"]["row"]

    records = []

    for r in rows:
        for c in r["columns"]:
            records.append({
                "date": c["key"],
                "value": float(c["value"])
            })

    df = pd.DataFrame(records)

    df["date"] = pd.to_datetime(df["date"].str.replace(" ", "-"))

    series = pd.Series(df["value"].values, index=df["date"])

    return series        

def fetch_data(symbol, name):
    return fetch_central_bank_data(symbol, name)
