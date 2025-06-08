import requests
import time
import os
import json
import dotenv
import math
import threading

dotenv.load_dotenv()

latitude = 49.25
longitude = 1.21667
radius = 5000

def get_places_nearby(lat, lng, radius, place_type=None):
    print(f"Recherche de lieux à proximité de {lat}, {lng} dans un rayon de {radius} mètres.")
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": os.getenv("API_KEY"),
    }
    if place_type:
        params["type"] = place_type

    results = []
    seen_place_ids = set()
    fetched_locations = set()

    def grid_points(center_lat, center_lng, radius, step=2000):
        points = []
        r_earth = 6378137
        for dx in range(-radius, radius + 1, step):
            for dy in range(-radius, radius + 1, step):
                dist = math.sqrt(dx**2 + dy**2)
                if dist > radius:
                    continue
                dlat = (dy / r_earth) * (180 / math.pi)
                dlng = (dx / (r_earth * math.cos(math.pi * center_lat / 180))) * (180 / math.pi)
                points.append((center_lat + dlat, center_lng + dlng))
        return points
    
    grid = grid_points(lat, lng, radius)
    def fetch_grid_point(lat_grid, lng_grid, params, url, details_url, seen_place_ids, results, fetched_locations, grid_lock):
        print(f"Recherche dans la grille : {lat_grid}, {lng_grid}")
        grid_key = f"{round(lat_grid, 5)},{round(lng_grid, 5)}"
        with grid_lock:
            if grid_key in fetched_locations:
                return
            fetched_locations.add(grid_key)
        local_params = params.copy()
        local_params["location"] = f"{lat_grid},{lng_grid}"
        while True:
            response = requests.get(url, params=local_params)
            data = response.json()
            for place in data.get("results", []):
                place_id = place.get("place_id")
                with grid_lock:
                    if place_id in seen_place_ids:
                        continue
                    seen_place_ids.add(place_id)
                details_params = {
                    "place_id": place_id,
                    "fields": "name,rating,user_ratings_total,website,vicinity,types",
                    "key": os.getenv("API_KEY"),
                }
                details_resp = requests.get(details_url, params=details_params)
                details_data = details_resp.json().get("result", {})
                with grid_lock:
                    results.append({
                        "name": details_data.get("name"),
                        "address": details_data.get("vicinity"),
                        "rating": details_data.get("rating"),
                        "user_ratings_total": details_data.get("user_ratings_total"),
                        "website": details_data.get("website"),
                        "types": details_data.get("types"),
                        "place_id": place_id
                    })
                time.sleep(0.1)
            next_page_token = data.get("next_page_token")
            if next_page_token:
                time.sleep(2)
                local_params = {
                    "pagetoken": next_page_token,
                    "key": os.getenv("API_KEY"),
                }
            else:
                break

    threads = []
    grid_lock = threading.Lock()
    for idx, (lat_grid, lng_grid) in enumerate(grid):
        t = threading.Thread(
            target=fetch_grid_point,
            args=(lat_grid, lng_grid, params, url, details_url, seen_place_ids, results, fetched_locations, grid_lock)
        )
        threads.append(t)
        t.start()
        # Limiter le nombre de threads simultanés pour éviter les problèmes de quota API
        if (idx + 1) % 10 == 0:
            for th in threads:
                th.join()
            threads = []

    # Attendre la fin de tous les threads restants
    for th in threads:
        th.join()
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
        

