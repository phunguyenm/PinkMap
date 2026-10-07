"""PinkMap automatic data collector (runs on GitHub Actions every 2 hours).

Reads the Mapbox token from the environment variable MAPBOX_TOKEN (a GitHub Secret),
asks Mapbox about 15 Houston trips, and adds one row per trip to data/auto_collected.csv.
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

# 15 trips between real Houston places (names and coordinates come from your team's OpenStreetMap list)
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
