import requests
import pandas as pd

def fetch_boj_data(db_name, series_code, start_date="202401"):
    """
    日本銀行APIから直接データを取得し、日付と数値のDataFrameを返す関数。
    """
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

        # 日銀JSONの階層を掘り進んでデータ部分を抽出
        # data -> data (list) -> [0] -> values (list)
        data_list = data.get('data', [])
        if not data_list:
            return pd.DataFrame()

        values = data_list[0].get('values', [])
        df = pd.DataFrame(values)

        if df.empty:
            return pd.DataFrame()

        # Scoringで使いやすいようにカラム名を統一
        # 日銀のレスポンスは 'period' (日付) と 'value' (数値)
        df = df.rename(columns={'period': 'date', 'value': 'value'})
        
        # 数値型に変換（日銀のデータは文字列で来るため）
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        return df

    except Exception as e:
        print(f"日銀API取得エラー ({series_code}): {e}")
        return pd.DataFrame()