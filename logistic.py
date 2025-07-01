import openrouteservice
from geopy.geocoders import Nominatim

# ✅ Simple in-memory cache
market_cache = {}

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="crop_app")
    location = geolocator.geocode(city_name)
    if location:
        return [location.longitude, location.latitude]
    return None

def get_nearest_market(city_name, ors_api_key):
    # ✅ Return from cache if available
    if city_name in market_cache:
        return market_cache[city_name]

    coords = get_coordinates(city_name)
    if not coords:
        return None

    client = openrouteservice.Client(key=ors_api_key)

    # Known mandi markets with coordinates [lon, lat]
    markets = [
    {"name": "Nashik Market Yard (APMC)", "coords": [73.7898, 19.9975], "district": "Nashik"},
    {"name": "Lasalgaon APMC Market", "coords": [73.8386, 20.0860], "district": "Nashik"},
    {"name": "Malegaon APMC", "coords": [74.5150, 20.5550], "district": "Nashik"},
    {"name": "Pimpalgaon Baswant APMC", "coords": [73.9000, 19.9500], "district": "Nashik"},
    {"name": "Yeola APMC", "coords": [74.1910, 20.0100], "district": "Nashik"},
    {"name": "Nashik APMC", "coords": [73.7898, 20.0058], "district": "Nashik"},

    # Pune district
    {"name": "Pune Market Yard (Shri Chhatrapati Shivaji)", "coords": [73.8612, 18.4779], "district": "Pune"},
    {"name": "Pune Market Yard", "coords": [73.8490, 18.5060], "district": "Pune"},
    {"name": "Daund APMC", "coords": [74.5850, 18.4600], "district": "Pune"},
    {"name": "Junnar APMC", "coords": [73.7800, 19.2060], "district": "Pune"},
    {"name": "Baramati APMC", "coords": [74.5761, 18.1517], "district": "Pune"},

    # Ahmednagar district
    {"name": "Ahmednagar APMC", "coords": [74.7333, 19.0833], "district": "Ahmednagar"},
    {"name": "Newasa APMC", "coords": [74.5450, 19.3000], "district": "Ahmednagar"},
    {"name": "Rahuri APMC", "coords": [74.6520, 19.3830], "district": "Ahmednagar"},
    {"name": "Shrirampur APMC", "coords": [74.6170, 19.6270], "district": "Ahmednagar"},
    {"name": "Akole APMC", "coords": [74.1500, 19.7667], "district": "Ahmednagar"},
    {"name": "Sangamner APMC", "coords": [74.4670, 19.6860], "district": "Ahmednagar"},

    # Akola district
    {"name": "Akola APMC Market Yard", "coords": [77.00296, 20.70723], "district": "Akola"},
    {"name": "Akola APMC", "coords": [77.0085, 20.7052], "district": "Akola"},
    {"name": "Murtizapur APMC", "coords": [76.4380, 20.7450], "district": "Akola"},
    {"name": "Telhara APMC", "coords": [76.9750, 20.6150], "district": "Akola"},
    {"name": "Akot APMC", "coords": [76.8820, 21.0950], "district": "Akola"},

    # Other major markets in Maharashtra
    {"name": "Vashi APMC", "coords": [72.9967, 19.0676], "district": "Thane"},
    {"name": "Pimpri Mandi", "coords": [73.8009, 18.6283], "district": "Pune"},
    {"name": "Kalamna APMC, Nagpur", "coords": [79.0833, 21.1667], "district": "Nagpur"},
    {"name": "CIDCO APMC, Aurangabad", "coords": [75.3522, 19.8762], "district": "Aurangabad"},
    {"name": "Shahupuri Market, Kolhapur", "coords": [74.2431, 16.7057], "district": "Kolhapur"},
    {"name": "Sangli APMC", "coords": [74.6000, 16.8667], "district": "Sangli"},
    {"name": "Solapur APMC", "coords": [75.9167, 17.6833], "district": "Solapur"},
    {"name": "Satara APMC", "coords": [74.0161, 17.6805], "district": "Satara"},
    {"name": "Aurangabad APMC", "coords": [75.3433, 19.8762], "district": "Aurangabad"},
    {"name": "Jalgaon APMC", "coords": [75.5626, 21.0077], "district": "Jalgaon"},
    {"name": "Dhule APMC", "coords": [74.7749, 20.9013], "district": "Dhule"},
    {"name": "Amravati APMC", "coords": [77.7588, 20.9374], "district": "Amravati"},
    {"name": "Beed APMC", "coords": [75.7445, 18.9890], "district": "Beed"},
    {"name": "Parbhani APMC", "coords": [76.7767, 19.2702], "district": "Parbhani"}
]



    nearest = None
    shortest = float('inf')

    for market in markets:
        try:
            route = client.directions(
                coordinates=[coords, market["coords"]],
                profile='driving-car',
                format='json'
            )

            distance_km = route['routes'][0]['summary']['distance'] / 1000
            duration_min = route['routes'][0]['summary']['duration'] / 60

            if distance_km < shortest:
                shortest = distance_km
                nearest = {
                    "market": market["name"],
                    "distance": f"{round(distance_km)} km",
                    "duration": f"{round(duration_min)} mins"
                }

        except Exception as e:
            print(f"Error checking market {market['name']}: {e}")

    # ✅ Save result in cache
    market_cache[city_name] = nearest
    return nearest