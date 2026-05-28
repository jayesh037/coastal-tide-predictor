from fastapi import APIRouter

router = APIRouter()

STATIONS = [
    {
        "id": "8443970",
        "name": "Boston, MA",
        "state": "MA",
        "lat": 42.3539,
        "lon": -71.0503,
        "timezone": "America/New_York",
        "region": "Northeast"
    },
    {
        "id": "8454000",
        "name": "Providence, RI",
        "state": "RI",
        "lat": 41.8071,
        "lon": -71.4012,
        "timezone": "America/New_York",
        "region": "Northeast"
    },
    {
        "id": "8447930",
        "name": "Woods Hole, MA",
        "state": "MA",
        "lat": 41.5236,
        "lon": -70.6711,
        "timezone": "America/New_York",
        "region": "Northeast"
    },
    {
        "id": "8518750",
        "name": "The Battery, NY",
        "state": "NY",
        "lat": 40.7006,
        "lon": -74.0142,
        "timezone": "America/New_York",
        "region": "Northeast"
    },
    {
        "id": "8557380",
        "name": "Lewes, DE",
        "state": "DE",
        "lat": 38.7828,
        "lon": -75.1192,
        "timezone": "America/New_York",
        "region": "Northeast"
    },
    {
        "id": "8575512",
        "name": "Annapolis, MD",
        "state": "MD",
        "lat": 38.9833,
        "lon": -76.4814,
        "timezone": "America/New_York",
        "region": "Northeast"
    },
    {
        "id": "8638610",
        "name": "Sewells Point, VA",
        "state": "VA",
        "lat": 36.9467,
        "lon": -76.3300,
        "timezone": "America/New_York",
        "region": "Southeast"
    },
    {
        "id": "8665530",
        "name": "Charleston, SC",
        "state": "SC",
        "lat": 32.7811,
        "lon": -79.9250,
        "timezone": "America/New_York",
        "region": "Southeast"
    },
    {
        "id": "8720218",
        "name": "Mayport, FL",
        "state": "FL",
        "lat": 30.3967,
        "lon": -81.4283,
        "timezone": "America/New_York",
        "region": "Southeast"
    },
    {
        "id": "8724580",
        "name": "Key West, FL",
        "state": "FL",
        "lat": 24.5550,
        "lon": -81.8081,
        "timezone": "America/New_York",
        "region": "Southeast"
    },
    {
        "id": "8761724",
        "name": "Galveston Bay, TX",
        "state": "TX",
        "lat": 29.3100,
        "lon": -94.7933,
        "timezone": "America/Chicago",
        "region": "Gulf"
    },
    {
        "id": "9414290",
        "name": "San Francisco, CA",
        "state": "CA",
        "lat": 37.8067,
        "lon": -122.4650,
        "timezone": "America/Los_Angeles",
        "region": "West Coast"
    },
    {
        "id": "9447130",
        "name": "Seattle, WA",
        "state": "WA",
        "lat": 47.6022,
        "lon": -122.3394,
        "timezone": "America/Los_Angeles",
        "region": "West Coast"
    },
    {
        "id": "1612340",
        "name": "Honolulu, HI",
        "state": "HI",
        "lat": 21.3069,
        "lon": -157.8661,
        "timezone": "Pacific/Honolulu",
        "region": "Hawaii"
    },
    {
        "id": "8410140",
        "name": "Eastport, ME",
        "state": "ME",
        "lat": 44.9033,
        "lon": -66.9822,
        "timezone": "America/New_York",
        "region": "Northeast"
    }
]

@router.get("/stations")
async def get_stations():
    features = []
    for station in STATIONS:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [station["lon"], station["lat"]]
            },
            "properties": station
        }
        features.append(feature)
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
