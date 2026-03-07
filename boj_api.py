import requests
import pandas as pd

def fetch_boj_data(db_name, series_code, start_date="202301"):
    base_url = "https://www.stat-search.boj.or.jp/api/v1/getDataCode"
    
    params = {
        "format": "json",
        "lang": "jp",
        "db": db_name,
        "code": series_code,
        "startDate": start_date
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        data_list = data.get('data', [])
        if not data_list:
            return pd.DataFrame(columns=['date', 'value'])

        values = data_list[0].get('values', [])
        df = pd.DataFrame(values)

        if df.empty:
            return pd.DataFrame(columns=['date', 'value'])

        df = df.rename(columns={'period': 'date'})
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        return df[['date', 'value']].dropna()

    except Exception as e:
        print(f"日銀API取得エラー ({series_code}): {e}")
        return pd.DataFrame(columns=['date', 'value'])