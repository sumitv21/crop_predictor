import openrouteservice
from geopy.geocoders import Nominatim

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="crop_app")
    location = geolocator.geocode(city_name)
    if location:
        return [location.longitude, location.latitude]
    return None

def get_nearest_market(city_name, ors_api_key):
    coords = get_coordinates(city_name)
    if not coords:
        return None

    client = openrouteservice.Client(key=ors_api_key)

    # Known mandi markets with coordinates [lon, lat]
    markets = [
    {"name": "Lasalgaon APMC", "coords": [74.22953, 20.15775]},   # ✅ Verified
    {"name": "Vashi APMC", "coords": [72.9967, 19.0676]},
    {"name": "Pimpri Mandi", "coords": [73.8009, 18.6283]},
    {"name": "Kalamna Market", "coords": [79.0833, 21.1667]},
    {"name": "CIDCO Mandi", "coords": [75.3522, 19.8762]},
    {"name": "Shahupuri Market", "coords": [74.2431, 16.7057]}
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

    return nearest
