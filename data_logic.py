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

        elif symbol == "SGP":
            # Singapore
            raw_cpi = fetch_sg_cpi()
            raw_10y = raw_cpi
            raw_2y = raw_cpi
            raw_m2 = raw_cpi
            raw_rate = raw_cpi
            raw_unrate = raw_cpi    
        else:
            return None

        axes = {
            "Future Focus": 200 if raw_cpi is not None else 0,
            "Market Position": 200 if raw_10y is not None else 0,
            "Financial Strength": 200 if raw_rate is not None else 0,
            "Cashflow Quality": 200 if raw_m2 is not None else 0,
            "People": 200 if raw_unrate is not None else 0
        }

        return {
            "axes": axes, 
            "total": int(sum(axes.values())), 
            "name": name,
            "price_hist": raw_10y.tail(20) if hasattr(raw_10y, "tail") else raw_cpi.tail(20) 
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
