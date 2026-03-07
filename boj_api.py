import requests
import pandas as pd

def fetch_cpi(api_key):

    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

    params = {
        "appId": api_key,
        "statsDataId": "0003427113"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]

        df = pd.DataFrame(values)

        df = df.rename(columns={
            "@time": "date",
            "$": "value"
        })

        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        return df[["date", "value"]].dropna()

    except Exception as e:
        print(f"CPI取得エラー: {e}")
        return pd.DataFrame(columns=["date", "value"])