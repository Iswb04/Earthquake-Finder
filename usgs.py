import requests


URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"


def fetch_earthquakes():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        earthquakes = []

        for event in data["features"]:

            properties = event["properties"]
            geometry = event["geometry"]

            earthquakes.append({
                "id": event["id"],
                "magnitude": properties["mag"],
                "location": properties["place"],
                "timestamp": properties["time"],
                "longitude": geometry["coordinates"][0],
                "latitude": geometry["coordinates"][1],
                "depth": geometry["coordinates"][2],
            })

        return earthquakes

    except requests.RequestException as error:
        print(f"API error: {error}")
        return []