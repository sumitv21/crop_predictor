from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import pandas as pd
from sklearn.linear_model import LinearRegression
import datetime
import requests
from logistic import get_nearest_market  # ✅ Import from logistic.py

app = Flask(__name__)
app.secret_key = "sumit_secret"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Load crop price data
df = pd.read_csv("sample_crop_prices.csv")
df['Date'] = pd.to_datetime(df['Date'])

# Train model per crop
crop_models = {}
for crop in df['Crop'].unique():
    crop_df = df[df['Crop'] == crop].copy()
    crop_df['Days'] = (crop_df['Date'] - crop_df['Date'].min()).dt.days
    model = LinearRegression()
    model.fit(crop_df[['Days']], crop_df['Price_per_kg'])
    crop_models[crop] = {'model': model, 'min_date': crop_df['Date'].min()}

# Weather API
def get_weather(city, api_key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        res = requests.get(url)
        data = res.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }
    except:
        return None

# Storage Suggestion
def suggest_storage(crop, weather):
    if weather["humidity"] > 70:
        return "Store in a dry, ventilated area to avoid spoilage."
    if crop.lower() == "onion":
        return "Keep onions in mesh bags in a cool, dry place."
    if crop.lower() == "tomato":
        return "Store tomatoes at room temperature, not in the fridge."
    return "Store in a cool, shaded, and dry environment."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        village = request.form['village']
        if name and village:
            session['farmer_name'] = name
            session['village'] = village
            return redirect(url_for('home'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'farmer_name' not in session:
        return redirect(url_for('login'))
    crops = list(crop_models.keys())
    return render_template("index.html", crops=crops, farmer_name=session['farmer_name'], village=session['village'])

@app.route('/result', methods=['POST'])
def result():
    if 'farmer_name' not in session:
        return redirect(url_for('login'))

    crop = request.form['crop']
    city = request.form['city']
    model_data = crop_models[crop]
    today = datetime.datetime.today()
    days = (today - model_data['min_date']).days
    predicted_price = round(model_data['model'].predict([[days]])[0], 2)

    crop_df = df[df['Crop'] == crop]
    chart_labels = crop_df['Date'].dt.strftime('%Y-%m-%d').tolist()
    chart_values = crop_df['Price_per_kg'].tolist()

    weather = get_weather(city, "091f039ffc62257274be708e3677c110")  # ✅ Replace with your key
    storage = suggest_storage(crop, weather) if weather else None

    # ✅ Get nearest market using logistic.py
    nearest_market = get_nearest_market(city, "5b3ce3597851110001cf62488a1ddd1dc965474890f7ae8e9aa25f36")  # ✅ Replace with your ORS key

    return render_template("result.html",
                           selected_crop=crop,
                           predicted_price=predicted_price,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           weather=weather,
                           storage_suggestion=storage,
                           city_name=city,
                           farmer_name=session['farmer_name'],
                           village=session['village'],
                           logistics=nearest_market)

if __name__ == "__main__":
    app.run(debug=True)
