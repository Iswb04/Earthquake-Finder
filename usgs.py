import requests

# USGS 30 DAYS
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

def fetch_earthquakes():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        earthquakes = []

        for event in data["features"]:
            properties = event["properties"]
            geometry = event["geometry"]
            coordinates = geometry["coordinates"]

            earthquakes.append({
                "id": event["id"],
                "magnitude": properties["mag"],
                "location": properties["place"],
                "timestamp": properties["time"],
                "longitude": coordinates[0],
                "latitude": coordinates[1],
                "depth": coordinates[2],
            })

        return earthquakes
        
    except requests.RequestException as error:
        print(f"API error: {error}")
        return []