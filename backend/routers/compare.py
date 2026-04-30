# backend/routers/compare.py
import asyncio
import logging
from fastapi import APIRouter, Query
from services.noaa_client import get_station_metadata

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/compare")
async def compare_stations(ids: str = Query(...)):
    station_ids = [s.strip() for s in ids.split(",") if s.strip()][:5]
    
    tasks = [get_station_metadata(station_id) for station_id in station_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_results = []
    for res in results:
        if isinstance(res, dict):
            valid_results.append(res)
            
    return valid_results