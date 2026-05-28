from fastapi import APIRouter

router = APIRouter()

STATIONS = [
    {"station_id": "8443970", "name": "Boston, MA", "state": "MA", "region": "Northeast"},
    {"station_id": "8454000", "name": "Providence, RI", "state": "RI", "region": "Northeast"},
    {"station_id": "8447930", "name": "Woods Hole, MA", "state": "MA", "region": "Northeast"},
    {"station_id": "8518750", "name": "The Battery, NY", "state": "NY", "region": "Northeast"},
    {"station_id": "8557380", "name": "Lewes, DE", "state": "DE", "region": "Mid-Atlantic"},
    {"station_id": "8575512", "name": "Annapolis, MD", "state": "MD", "region": "Mid-Atlantic"},
    {"station_id": "8638610", "name": "Sewells Point, VA", "state": "VA", "region": "Mid-Atlantic"},
    {"station_id": "8665530", "name": "Charleston, SC", "state": "SC", "region": "Southeast"},
    {"station_id": "8720218", "name": "Mayport, FL", "state": "FL", "region": "Southeast"},
    {"station_id": "8724580", "name": "Key West, FL", "state": "FL", "region": "Southeast"},
    {"station_id": "8761724", "name": "Galveston Bay, TX", "state": "TX", "region": "Gulf"},
    {"station_id": "9414290", "name": "San Francisco, CA", "state": "CA", "region": "West Coast"},
    {"station_id": "9447130", "name": "Seattle, WA", "state": "WA", "region": "West Coast"},
    {"station_id": "1612340", "name": "Honolulu, HI", "state": "HI", "region": "Hawaii"},
    {"station_id": "8410140", "name": "Eastport, ME", "state": "ME", "region": "Northeast"},
]

@router.get("/stations")
async def get_stations():
    features = []
    for s in STATIONS:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": s
        })
    return {"type": "FeatureCollection", "features": features}
