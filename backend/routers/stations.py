# backend/routers/stations.py
import time
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.noaa_client import get_all_stations, get_station_metadata

router = APIRouter()

_stations_cache: Dict[str, Any] = {"timestamp": 0, "data": None}
CACHE_TTL = 3600

@router.get("/stations")
async def get_stations():
    global _stations_cache
    now = time.time()
    
    if _stations_cache["data"] is not None and (now - _stations_cache["timestamp"]) < CACHE_TTL:
        return _stations_cache["data"]
        
    stations = await get_all_stations()
    
    features = []
    for st in stations:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [st["lon"], st["lat"]]},
            "properties": {
                "station_id": st["station_id"],
                "name": st["name"],
                "state": st["state"]
            }
        })
        
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    _stations_cache["timestamp"] = now
    _stations_cache["data"] = feature_collection
    
    return feature_collection

@router.get("/stations/{station_id}")
async def get_station(station_id: str):
    metadata = await get_station_metadata(station_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Station not found")
    return metadata