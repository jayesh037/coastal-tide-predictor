# backend/routers/history.py
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from services.noaa_client import get_station_observations

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/history/{station_id}")
async def get_station_history(station_id: str, days: int = Query(30)):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    end_date = now
    
    df = await get_station_observations(station_id, start_date, end_date)
    
    observations = []
    if not df.empty:
        for _, row in df.iterrows():
            observations.append({
                "timestamp": row["datetime"].isoformat() if hasattr(row["datetime"], "isoformat") else str(row["datetime"]),
                "water_level": float(row["water_level"])
            })
            
    return {
        "station_id": station_id,
        "days": days,
        "observations": observations
    }