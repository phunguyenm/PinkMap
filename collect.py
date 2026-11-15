"""PinkMap automatic data collector (runs on GitHub Actions hourly (scheduled)).

Reads the Mapbox token from the environment variable MAPBOX_TOKEN (a GitHub Secret),
asks Mapbox about 50 Houston trips, and adds one row per trip to data/auto_collected.csv.
The columns are the same as the Colab collection notebook, so Notebook 2 can combine both.
"""
import csv
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

TOKEN = os.environ.get("MAPBOX_TOKEN", "")
OUT_FILE = "data/auto_collected.csv"
COLUMNS = ["collected_at", "route_id", "origin", "destination", "distance_miles",
           "traffic_seconds", "typical_seconds", "day_of_week", "hour"]

# 50 trips between real Houston places (names and coordinates come from your team's OpenStreetMap list)
ROUTES = [
    {"route_id": 1, "origin": 'Houston City College', "o_lat": 29.74228, "o_lon": -95.3772125, "dest": 'Houston City College West Loop Campus', "d_lat": 29.7213883, "d_lon": -95.4573693},
    {"route_id": 2, "origin": 'Houston City College', "o_lat": 29.74228, "o_lon": -95.3772125, "dest": 'Houston City College Northeast - Northline Campus', "d_lat": 29.8328069, "d_lon": -95.3771485},
    {"route_id": 3, "origin": 'Houston City College', "o_lat": 29.74228, "o_lon": -95.3772125, "dest": 'Rice University', "d_lat": 29.7165599, "d_lon": -95.4029398},
    {"route_id": 4, "origin": 'Discovery Green', "o_lat": 29.7529825, "o_lon": -95.3595375, "dest": 'Hermann Park', "d_lat": 29.7148648, "d_lon": -95.3888866},
    {"route_id": 5, "origin": 'Discovery Green', "o_lat": 29.7529825, "o_lon": -95.3595375, "dest": 'University of Houston', "d_lat": 29.7207023, "d_lon": -95.3434964},
    {"route_id": 6, "origin": 'Houston City College West Loop Campus', "o_lat": 29.7213883, "o_lon": -95.4573693, "dest": 'Levy Park', "d_lat": 29.7326662, "d_lon": -95.4233311},
    {"route_id": 7, "origin": 'Houston City College West Loop Campus', "o_lat": 29.7213883, "o_lon": -95.4573693, "dest": 'Hermann Park', "d_lat": 29.7148648, "d_lon": -95.3888866},
    {"route_id": 8, "origin": 'Houston City College Northeast - Northline Campus', "o_lat": 29.8328069, "o_lon": -95.3771485, "dest": 'Discovery Green', "d_lat": 29.7529825, "d_lon": -95.3595375},
    {"route_id": 9, "origin": 'Memorial Park', "o_lat": 29.7661061, "o_lon": -95.4436138, "dest": 'Discovery Green', "d_lat": 29.7529825, "d_lon": -95.3595375},
    {"route_id": 10, "origin": 'Rice University', "o_lat": 29.7165599, "o_lon": -95.4029398, "dest": 'Space Center Houston', "d_lat": 29.5511263, "d_lon": -95.0973288},
    {"route_id": 11, "origin": 'Central Library', "o_lat": 29.7594337, "o_lon": -95.3699788, "dest": 'Houston Museum of Natural Science', "d_lat": 29.7221086, "d_lon": -95.3897295},
    {"route_id": 12, "origin": 'University of Houston', "o_lat": 29.7207023, "o_lon": -95.3434964, "dest": 'NRG Arena', "d_lat": 29.6811892, "d_lon": -95.4057955},
    {"route_id": 13, "origin": 'Houston City College Northwest - Spring Branch Campus', "o_lat": 29.7879064, "o_lon": -95.5606959, "dest": 'Houston City College', "d_lat": 29.74228, "d_lon": -95.3772125},
    {"route_id": 14, "origin": 'Houston City College West Loop Campus', "o_lat": 29.7213883, "o_lon": -95.4573693, "dest": 'Houston City College Northwest - Spring Branch Campus', "d_lat": 29.7879064, "d_lon": -95.5606959},
    {"route_id": 15, "origin": 'Houston Sports Park', "o_lat": 29.637277, "o_lon": -95.3950164, "dest": 'Discovery Green', "d_lat": 29.7529825, "d_lon": -95.3595375},

    # Additional fixed routes (16–30); original 15 are unchanged.
    {'route_id': 16, 'origin': 'Emancipation Park', 'o_lat': 29.73588, 'o_lon': -95.36514, 'dest': 'Memorial Park', 'd_lat': 29.76611, 'd_lon': -95.44361},
    {'route_id': 17, 'origin': 'POST Houston', 'o_lat': 29.76614, 'o_lon': -95.36454, 'dest': 'Rice University', 'd_lat': 29.71656, 'd_lon': -95.40294},
    {'route_id': 18, 'origin': 'Menil Collection', 'o_lat': 29.73728, 'o_lon': -95.39847, 'dest': 'University of Houston', 'd_lat': 29.7207, 'd_lon': -95.3435},
    {'route_id': 19, 'origin': "Children's Museum of Houston", 'o_lat': 29.72251, 'o_lon': -95.38525, 'dest': 'Discovery Green', 'd_lat': 29.75298, 'd_lon': -95.35954},
    {'route_id': 20, 'origin': 'Holocaust Museum Houston', 'o_lat': 29.72512, 'o_lon': -95.38564, 'dest': 'Houston City College West Loop Campus', 'd_lat': 29.72139, 'd_lon': -95.45737},
    {'route_id': 21, 'origin': 'The University of Texas Health Science Center', 'o_lat': 29.70299, 'o_lon': -95.40315, 'dest': 'NRG Arena', 'd_lat': 29.68119, 'd_lon': -95.4058},
    {'route_id': 22, 'origin': 'University of Houston - Clear Lake', 'o_lat': 29.57892, 'o_lon': -95.09731, 'dest': 'Space Center Houston', 'd_lat': 29.55113, 'd_lon': -95.09733},
    {'route_id': 23, 'origin': 'San Jacinto College South Campus', 'o_lat': 29.58026, 'o_lon': -95.20157, 'dest': 'University of Houston - Clear Lake', 'd_lat': 29.57892, 'd_lon': -95.09731},
    {'route_id': 24, 'origin': 'Eleanor Tinsley Park', 'o_lat': 29.76125, 'o_lon': -95.37803, 'dest': 'Houston Sports Park', 'd_lat': 29.63728, 'd_lon': -95.39502},
    {'route_id': 25, 'origin': 'Spotts Park', 'o_lat': 29.76496, 'o_lon': -95.39509, 'dest': 'Houston City College', 'd_lat': 29.74228, 'd_lon': -95.37721},
    {'route_id': 26, 'origin': 'Lamar Park', 'o_lat': 29.74673, 'o_lon': -95.39554, 'dest': 'Houston Museum of Natural Science', 'd_lat': 29.72211, 'd_lon': -95.38973},
    {'route_id': 27, 'origin': 'MacGregor Park', 'o_lat': 29.71016, 'o_lon': -95.3401, 'dest': 'Central Library', 'd_lat': 29.75943, 'd_lon': -95.36998},
    {'route_id': 28, 'origin': 'Herman Brown Park', 'o_lat': 29.78507, 'o_lon': -95.24673, 'dest': 'Discovery Green', 'd_lat': 29.75298, 'd_lon': -95.35954},
    {'route_id': 29, 'origin': 'Buffalo Bayou Park', 'o_lat': 29.761951, 'o_lon': -95.390954, 'dest': 'Houston City College Northwest - Spring Branch Campus', 'd_lat': 29.78791, 'd_lon': -95.5607},
    {'route_id': 30, 'origin': 'Houston City Hall', 'o_lat': 29.760185, 'o_lon': -95.369383, 'dest': 'Hermann Park', 'd_lat': 29.71486, 'd_lon': -95.38889},

    # Additional monitored routes (31-50)
    {"route_id": 31, "origin": 'Houston Farmers Market', "o_lat": 29.810226, "o_lon": -95.381617, "dest": 'Discovery Green', "d_lat": 29.75298, "d_lon": -95.35954},
    {"route_id": 32, "origin": 'Heights Neighborhood Library', "o_lat": 29.794729, "o_lon": -95.397209, "dest": 'Rice University', "d_lat": 29.71656, "d_lon": -95.40294},
    {"route_id": 33, "origin": 'Bayou Bend Collection and Gardens', "o_lat": 29.757615, "o_lon": -95.420467, "dest": 'Hermann Park', "d_lat": 29.71486, "d_lon": -95.38889},
    {"route_id": 34, "origin": 'Houston Arboretum Park', "o_lat": 29.763583, "o_lon": -95.451701, "dest": 'Houston City College West Loop Campus', "d_lat": 29.72139, "d_lon": -95.45737},
    {"route_id": 35, "origin": 'Gerald D. Hines Waterwall Park', "o_lat": 29.736221, "o_lon": -95.461288, "dest": 'Memorial Park', "d_lat": 29.76611, "d_lon": -95.44361},
    {"route_id": 36, "origin": 'McGovern Centennial Gardens', "o_lat": 29.7211, "o_lon": -95.387431, "dest": 'University of Houston', "d_lat": 29.7207, "d_lon": -95.3435},
    {"route_id": 37, "origin": 'Hermann Square', "o_lat": 29.759738, "o_lon": -95.368612, "dest": 'Rice University', "d_lat": 29.71656, "d_lon": -95.40294},
    {"route_id": 38, "origin": 'Market Square Park', "o_lat": 29.762664, "o_lon": -95.362356, "dest": 'NRG Arena', "d_lat": 29.68119, "d_lon": -95.4058},
    {"route_id": 39, "origin": 'Midtown Park', "o_lat": 29.743588, "o_lon": -95.376147, "dest": 'Levy Park', "d_lat": 29.73267, "d_lon": -95.42333},
    {"route_id": 40, "origin": 'Eastwood Park', "o_lat": 29.742002, "o_lon": -95.326131, "dest": 'Space Center Houston', "d_lat": 29.55113, "d_lon": -95.09733},
    {"route_id": 41, "origin": 'Mason Park', "o_lat": 29.725606, "o_lon": -95.29341, "dest": 'Discovery Green', "d_lat": 29.75298, "d_lon": -95.35954},
    {"route_id": 42, "origin": 'George Bush Park', "o_lat": 29.74311, "o_lon": -95.68446, "dest": 'Rice University', "d_lat": 29.71656, "d_lon": -95.40294},
    {"route_id": 43, "origin": 'Cullen Park', "o_lat": 29.798678, "o_lon": -95.693237, "dest": 'Houston City College West Loop Campus', "d_lat": 29.72139, "d_lon": -95.45737},
    {"route_id": 44, "origin": 'Bear Creek Pioneers Park', "o_lat": 29.825157, "o_lon": -95.626859, "dest": 'Discovery Green', "d_lat": 29.75298, "d_lon": -95.35954},
    {"route_id": 45, "origin": 'Kingwood Branch Library', "o_lat": 30.041932, "o_lon": -95.181584, "dest": 'Houston City Hall', "d_lat": 29.760185, "d_lon": -95.369383},
    {"route_id": 46, "origin": 'Jesse Jones Park', "o_lat": 30.026179, "o_lon": -95.294373, "dest": 'Memorial Park', "d_lat": 29.76611, "d_lon": -95.44361},
    {"route_id": 47, "origin": 'Fonde Park', "o_lat": 29.714403, "o_lon": -95.324935, "dest": 'Houston Sports Park', "d_lat": 29.63728, "d_lon": -95.39502},
    {"route_id": 48, "origin": 'Buffalo Bayou Park', "o_lat": 29.761951, "o_lon": -95.390954, "dest": 'Houston Farmers Market', "d_lat": 29.810226, "d_lon": -95.381617},
    {"route_id": 49, "origin": 'Houston City College West Loop Campus', "o_lat": 29.72139, "o_lon": -95.45737, "dest": 'Alief Community Park', "d_lat": 29.701762, "d_lon": -95.590012},
    {"route_id": 50, "origin": 'Houston Museum of Natural Science', "o_lat": 29.72211, "o_lon": -95.38973, "dest": 'Houston City Hall', "d_lat": 29.760185, "d_lon": -95.369383},
]


def get_route_row(trip):
    coords = f"{trip['o_lon']},{trip['o_lat']};{trip['d_lon']},{trip['d_lat']}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coords}"
    params = {"access_token": TOKEN, "overview": "false", "alternatives": "false"}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    route = response.json()["routes"][0]
    now = datetime.now(ZoneInfo("America/Chicago"))  # Houston time
    return {
        "collected_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "route_id": trip["route_id"],
        "origin": trip["origin"],
        "destination": trip["dest"],
        "distance_miles": round(route["distance"] / 1609.344, 3),
        "traffic_seconds": round(route["duration"], 1),
        "typical_seconds": route.get("duration_typical"),
        "day_of_week": now.strftime("%A"),
        "hour": now.hour,
    }


def main():
    if not TOKEN:
        print("MAPBOX_TOKEN is missing. Add it as a GitHub Secret.")
        sys.exit(1)

    rows = []
    for trip in ROUTES:
        try:
            rows.append(get_route_row(trip))
            print("OK   trip", trip["route_id"])
        except Exception as error:
            print("FAIL trip", trip["route_id"], "-", error)

    if not rows:
        print("No rows collected.")
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    new_file = not os.path.exists(OUT_FILE)
    with open(OUT_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {OUT_FILE}")


if __name__ == "__main__":
    main()
