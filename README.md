# PinkMap

PinkMap is a route app for Houston that helps drivers pick the **calmer** way to get somewhere. It compares how long a trip takes *right now* (with traffic) to how long it *normally* takes, and flags routes that are running slower or faster than usual.

This is a group project for our AI/ML course at Houston Community College (Fall 2026).

**Team:** Phu, Jose, Mary, Christian

## Try the app

Live demo: https://phunguyenm.github.io/PinkMap/PinkMap_App.html

Pick a start and a destination, click **Show routes**, and the app draws the route options on a map. Each option shows its travel time with traffic, its usual travel time, and a tag like "slower than usual". The calmest option is marked **Least congested**.

The first time you open it, it asks for a free Mapbox public token (make one at mapbox.com). The token is not stored in this repo.

## What is in this repo

| File | What it is |
|---|---|
| `PinkMap_App.html` | The demo app (map, route options, traffic vs. usual time) |
| `PinkMap_1_Collect_Data.ipynb` | Notebook that collects traffic data from Mapbox and saves it to a csv |
| `PinkMap_2_Clean_Explore_Baseline.ipynb` | Notebook that cleans the data, adds features, splits it, makes charts, and runs baseline models |
| `data/` | The csv files of collected data |

## How it works

1. **Places** come from OpenStreetMap (parks, campuses, libraries, and so on).
2. **Routes and travel times** come from the Mapbox Directions API (`driving-traffic` profile), which gives both the live travel time and the typical travel time.
3. **Our data:** every run of the collection notebook adds one row per trip (time, distance, traffic time, typical time).
4. **Features** we build from that: traffic delay, slower/faster label, hour, day of week, rush hour, and average speed.
5. **Model:** we compare simple baselines now, and will train a better model to predict traffic delay.

## Help us collect data

The more runs we have at different times and days, the better our model gets. Rush hour (7-9 AM and 4-6 PM) is the most useful.

1. Get a free token: create an account at mapbox.com and copy your **Default public token** (starts with `pk.`).
2. Open https://colab.research.google.com, choose **File -> Upload notebook**, and pick `PinkMap_1_Collect_Data.ipynb`.
3. Paste your token in the first code cell, between the quote marks. **Do not upload a notebook with your token in it.**
4. Click **Runtime -> Run all**. Allow Google Drive if it asks. If Drive will not connect, the notebook downloads the csv for you instead.
5. You should see "Saved 15 new rows".
6. Rename the csv like `yourname_2026-10-08_evening.csv` and put it in the `data/` folder (**Add file -> Upload files**), or send it to Phu.

## Current status (honest version)

- Working: data collection, the demo app, and the cleaning/baseline notebook.
- Still small: the dataset is only as big as the runs we have collected so far, so early numbers are a proof of concept, not a final result.
- Next: collect more rush-hour data across several days, train and compare real models, and show the model's prediction inside the app.

## Data and privacy

We only use public places (parks, campuses, libraries, community centers). No home addresses and no personal travel history are collected.
