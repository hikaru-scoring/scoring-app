import requests
import pandas as pd

def fetch_boj_data(db_name, series_code, start_date="202301"):
    # URLを日銀の「時系列統計データ検索サイト」専用に固定
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

        # 日銀特有の JSON 構造（data -> values）から抜き出す
        data_list = data.get('data', [])
        if not data_list:
            return pd.DataFrame(columns=['date', 'value'])

        values = data_list[0].get('values', [])
        df = pd.DataFrame(values)

        if df.empty:
            return pd.DataFrame(columns=['date', 'value'])

        # period を date に、数値を value に整理
        df = df.rename(columns={'period': 'date'})
        
        # 数値変換（日銀のデータは文字列なので必須）
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # 最後に、Scoringに必要な「日付」と「数値」の列だけを返す
        return df[['date', 'value']].dropna()

    except Exception as e:
        print(f"日銀API取得エラー ({series_code}): {e}")
        return pd.DataFrame(columns=['date', 'value'])