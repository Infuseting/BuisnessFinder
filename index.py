import requests
import time
import os
import json
import dotenv

dotenv.load_dotenv()

latitude = 49.25
longitude = 1.21667
radius = 5000

def get_places_nearby(lat, lng, radius):
    print(f"Recherche de lieux à proximité de {lat}, {lng} dans un rayon de {radius} mètres.")
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": os.getenv("API_KEY"),
    }
    results = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        for place in data.get("results", []):
            place_id = place.get("place_id")
            details_params = {
                "place_id": place_id,
                "fields": "name,rating,user_ratings_total,website,vicinity,types",
                "key": os.getenv("API_KEY"),
            }
            details_resp = requests.get(details_url, params=details_params)
            details_data = details_resp.json().get("result", {})
            results.append({
                "name": details_data.get("name"),
                "address": details_data.get("vicinity"),
                "rating": details_data.get("rating"),
                "user_ratings_total": details_data.get("user_ratings_total"),
                "website": details_data.get("website"),
                "types": details_data.get("types"),
                "place_id": place_id
            })
            time.sleep(0.1)  # Pour éviter de dépasser la limite de requêtes
        next_page_token = data.get("next_page_token")
        if next_page_token:
            time.sleep(2)
            params = {
                "pagetoken": next_page_token,
                "key": os.getenv("API_KEY"),
            }
        else:
            break
    return results
def file_numero():
    existing_files = [f for f in os.listdir("assets") if f.endswith(".json")]
    if not existing_files:
        return "1.json"
    last_file = max(existing_files, key=lambda x: int(x.split('.')[0]))
    next_file_num = int(last_file.split('.')[0]) + 1
    return f"{next_file_num}.json"

if __name__ == "__main__":
    
    last_file = file_numero()
        

