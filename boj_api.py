#boj_api.py
import requests
import pandas as pd
import streamlit as st

def fetch_boj_data(db_name, series_code, start_date="202401"):
    """
    日本銀行APIから直接データを取得し、日付と数値のDataFrameを返す関数。
    """
    base_url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    params = {
        "appId": st.secrets["ESTAT_APP_ID"],
        "statsDataId": "00200573",
        "cdCat01": "1000000000"
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

        # --- 修正箇所：日銀データの安全な処理 ---
        # まず period を date に変える
        df = df.rename(columns={'period': 'date'})
        
        # 'value' 列がない、またはデータが空の場合のガード
        if 'value' not in df.columns or df['value'].empty:
            return pd.DataFrame(columns=['date', 'value'])
            
        # 数値型に変換
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        return df[['date', 'value']]
        # --- 修正ここまで ---
    
        return df

    except Exception as e:
        print(f"日銀API取得エラー ({series_code}): {e}")
        return pd.DataFrame()