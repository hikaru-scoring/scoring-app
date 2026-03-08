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

print(df.tail())