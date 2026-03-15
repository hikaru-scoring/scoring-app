"""
Daily score recorder — runs via GitHub Actions.
Fetches current scores for all assets and appends to scores_history.json.
"""
import json
import os
from datetime import datetime, timezone

import yfinance as yf
import pandas as pd

HISTORY_FILE = "scores_history.json"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

COMMODITY_TICKERS = {"WTI Crude Oil": "CL=F", "Gold": "GC=F", "Copper": "HG=F"}
SGX_STOCKS = {"D05": "DBS Group", "O39": "OCBC", "U11": "UOB", "Z74": "Singtel", "9CI": "CapitaLand Investment"}


def score_commodity(commodity, ticker_sym):
    ticker = yf.Ticker(ticker_sym)
    hist = ticker.history(period="1y")
    if hist.empty or len(hist) < 63:
        return None
    close = hist["Close"]
    last        = float(close.iloc[-1])
    avg_1y      = float(close.mean())
    high_52w    = float(close.max())
    prev_1y     = float(close.iloc[0])
    prev_3m     = float(close.iloc[-63])
    vol         = float(close.pct_change().tail(20).std() * 100)
    yoy         = ((last / prev_1y) - 1) * 100
    mom         = ((last / prev_3m) - 1) * 100
    return int(sum([
        min(max(100 + mom * 2,              0), 200),
        min(max(200 - vol * 8,              0), 200),
        min(max((last / avg_1y) * 100,      0), 200),
        min(max((last / high_52w) * 200,    0), 200),
        min(max(100 + yoy * 1.5,            0), 200),
    ]))


def score_sgx(symbol):
    ticker = yf.Ticker(f"{symbol}.SI")
    hist = ticker.history(period="1y")
    if hist.empty or len(hist) < 252:
        return None
    close     = hist["Close"]
    last      = float(close.iloc[-1])
    avg_12m   = float(close.mean())
    high_52w  = float(close.max())
    vol       = float(close.pct_change().std() * 100)
    ff = min(max((last / avg_12m) * 100,  0), 200)
    fs = min(max((last / high_52w) * 200, 0), 200)
    mp = min(max(200 - vol * 20,          0), 200)
    return int(ff + fs + mp + 100 + 100)


def score_central_bank(bank):
    """中央銀行スコアをFREDから取得（FRED_API_KEY環境変数が必要）"""
    fred_key = os.environ.get("FRED_API_KEY")
    if not fred_key:
        return None
    try:
        from fredapi import Fred
        fred = Fred(api_key=fred_key)
        series_map = {
            "Federal Reserve":       {"y10": "DGS10",           "y2": "DGS2",           "cpi": "CPIAUCSL", "unemployment": "UNRATE",          "m2": "M2SL"},
            "Bank of England":       {"y10": "IRLTLT01GBM156N", "y2": "IR3TIB01GBM156N","cpi": "GBRCPIALLMINMEI","unemployment":"LRHUTTTTGBM156S","m2": "MABMM301GBM189S"},
            "Bank of Japan":         {"y10": "IRLTLT01JPM156N", "y2": "IR3TIB01JPM156N", "cpi": None,       "unemployment": "LRHUTTTTJPM156S", "m2": None},
        }
        if bank not in series_map:
            return None
        ids = series_map[bank]
        y10 = fred.get_series(ids["y10"]).dropna()
        y2  = fred.get_series(ids["y2"]).dropna()
        if y10.empty or y2.empty:
            return None
        latest_y10 = float(y10.iloc[-1])
        latest_y2  = float(y2.iloc[-1])
        unemp = fred.get_series(ids["unemployment"]).dropna() if ids["unemployment"] else None
        latest_unemp = float(unemp.iloc[-1]) if unemp is not None and not unemp.empty else 5.0
        cpi_yoy = 2.0
        if ids["cpi"]:
            cpi = fred.get_series(ids["cpi"]).dropna()
            if len(cpi) >= 13:
                cpi_yoy = float(((cpi.iloc[-1] / cpi.iloc[-13]) - 1) * 100)
        m2_yoy = 5.0
        if ids["m2"]:
            m2 = fred.get_series(ids["m2"]).dropna()
            if len(m2) >= 13:
                m2_yoy = float(((m2.iloc[-1] / m2.iloc[-13]) - 1) * 100)
        y10_vol = float(y10.tail(20).std()) if len(y10) >= 20 else float(y10.std())
        return int(sum([
            max(0, min(200, 200 - abs(cpi_yoy - 2) * 20)),
            max(0, min(200, 200 - latest_unemp * 15)),
            max(0, min(200, 100 + (latest_y10 - latest_y2) * 30)),
            max(0, min(200, 200 - abs(m2_yoy - 5) * 10)),
            max(0, min(200, 200 - y10_vol * 100)),
        ]))
    except Exception as e:
        print(f"  CB error ({bank}): {e}")
        return None


def main():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}

    if TODAY not in history:
        history[TODAY] = {}

    for commodity, ticker_sym in COMMODITY_TICKERS.items():
        try:
            score = score_commodity(commodity, ticker_sym)
            if score is not None:
                history[TODAY][commodity] = score
                print(f"  {commodity}: {score}")
        except Exception as e:
            print(f"  Error ({commodity}): {e}")

    for symbol, name in SGX_STOCKS.items():
        try:
            score = score_sgx(symbol)
            if score is not None:
                history[TODAY][name] = score
                print(f"  {name}: {score}")
        except Exception as e:
            print(f"  Error ({name}): {e}")

    for bank in ["Federal Reserve", "Bank of England", "Bank of Japan"]:
        try:
            score = score_central_bank(bank)
            if score is not None:
                history[TODAY][bank] = score
                print(f"  {bank}: {score}")
        except Exception as e:
            print(f"  Error ({bank}): {e}")

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"Done. Scores recorded for {TODAY}")


if __name__ == "__main__":
    main()
