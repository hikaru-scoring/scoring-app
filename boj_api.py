#boj_api.py
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

        # 日銀APIの実際の構造に合わせて抽出
        data_list = data.get('data', [])
        if not data_list:
            return pd.DataFrame()

        # 最初のデータ系列から日付(period)と数値(value)を取得
        values = data_list[0].get('values', [])
        df = pd.DataFrame(values)

        if df.empty:
            return pd.DataFrame()

        # カラム名を統一（日銀のキーは 'period' と 'value' です）
        df = df.rename(columns={'period': 'date'})

        df = pd.DataFrame({
            "date": dates,
            "value": obs
        })

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