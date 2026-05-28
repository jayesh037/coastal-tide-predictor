# backend/routers/forecast.py
import os
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query
from services.noaa_client import get_station_observations
from services.tft_inference import get_forecast

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/forecast/{station_id}")
async def get_station_forecast(station_id: str, days_history: int = Query(14)):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days_history)
    end_date = now
    
    df = await get_station_observations(station_id, start_date, end_date)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for this station")
        
    df["station_id"] = station_id
    checkpoint_path = os.getenv("MODEL_CHECKPOINT_PATH", "/app/ml/checkpoints/full_checkpoint2.pth")
    
    result = get_forecast(station_id, df, checkpoint_path)
    if result is None:
        raise HTTPException(status_code=500, detail="Inference failed")
        
    return {
        "station_id": station_id,
        "generated_at": now.isoformat(),
        "horizon_hours": 168,
        "timestamps": result.get("timestamps", []),
        "q10": result.get("q10", []),
        "q25": result.get("q25", []),
        "q50": result.get("q50", []),
        "q75": result.get("q75", []),
        "q90": result.get("q90", []),
        "actuals": result.get("actuals", [])
    }
