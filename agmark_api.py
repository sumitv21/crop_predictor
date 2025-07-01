import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_crop_prices_from_agmarknet(crop_name, api_key, state="Maharashtra"):
    url = "https://api.data.gov.in/resource/ab7c6db6-6cd8-4c6b-a2b3-9ab3c64139f1"
    today = datetime.today()
    last_month = today - timedelta(days=30)

    params = {
        "api-key": api_key,
        "format": "json",
        "filters[crop]": crop_name.title(),
        "filters[state]": state.title(),
        "limit": 1000
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        records = data.get("records", [])
        if not records:
            return None

        df = pd.DataFrame(records)
        if "arrival_date" in df.columns and "modal_price" in df.columns:
            df["arrival_date"] = pd.to_datetime(df["arrival_date"])
            df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
            df = df.dropna(subset=["modal_price"])
            df = df.sort_values("arrival_date")
            df = df[df["arrival_date"] > last_month]
            df.rename(columns={"arrival_date": "Date", "modal_price": "Price_per_kg"}, inplace=True)
            return df[["Date", "Price_per_kg"]]
        else:
            return None
    except Exception as e:
        print("Agmarknet API Error:", e)
        return None
