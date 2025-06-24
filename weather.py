import requests

def get_weather(city_name, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ API Error:", response.status_code, response.text)
        return None

    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }

def suggest_storage(crop, temp, humidity):
    crop = crop.lower()
    if temp > 30 or humidity > 70:
        return "Use Cold Storage"
    elif "grain" in crop or crop in ["wheat", "rice"]:
        return "Use Dry Storage"
    else:
        return "Sell Immediately"
