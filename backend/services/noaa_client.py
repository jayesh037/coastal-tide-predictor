import logging
from datetime import datetime
from typing import List, Optional

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

STATIONS_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=waterlevels"
DATA_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

async def get_all_stations() -> List[dict]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(STATIONS_URL)
            response.raise_for_status()
            data = response.json()
            
            result = []
            for station in data.get("stations", []):
                state = station.get("state")
                if state is not None and state != "":
                    try:
                        result.append({
                            "station_id": station.get("id"),
                            "name": station.get("name"),
                            "lat": float(station.get("lat", 0.0)),
                            "lon": float(station.get("lng", 0.0)),
                            "state": state
                        })
                    except (ValueError, TypeError):
                        continue
                        
            return result
    except Exception as e:
        logger.warning(f"Error fetching all stations: {e}")
        return []

async def get_station_observations(station_id: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    try:
        params = {
            "product": "water_level",
            "datum": "MLLW",
            "station": station_id,
            "begin_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "units": "metric",
            "time_zone": "GMT",
            "application": "coastal_tide_predictor",
            "format": "json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(DATA_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            records = data.get("data", [])
            if not records:
                return pd.DataFrame(columns=["datetime", "water_level", "quality"])
                
            df = pd.DataFrame(records)
            
            # Map columns and ensure they exist
            if "t" in df.columns:
                df = df.rename(columns={"t": "datetime"})
            if "v" in df.columns:
                df = df.rename(columns={"v": "water_level"})
            if "q" in df.columns:
                df = df.rename(columns={"q": "quality"})
                
            # Ensure required columns are present
            for col in ["datetime", "water_level", "quality"]:
                if col not in df.columns:
                    df[col] = None

            # Convert datetime and localize to UTC
            df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce').dt.tz_localize('UTC')
            
            # Convert water_level to float
            df["water_level"] = pd.to_numeric(df["water_level"], errors='coerce')
            
            # Drop NaN water levels
            df = df.dropna(subset=["water_level"])
            
            # Drop quality == "M"
            df = df[df["quality"] != "M"]
            
            return df[["datetime", "water_level", "quality"]].copy()
            
    except Exception as e:
        logger.warning(f"Error fetching observations for station {station_id}: {e}")
        return pd.DataFrame(columns=["datetime", "water_level", "quality"])

async def get_station_metadata(station_id: str) -> Optional[dict]:
    try:
        url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            stations = data.get("stations", [])
            if not stations:
                return None
                
            station = stations[0]
            
            # Extract timezone offset cautiously
            timezone = station.get("timezone", {})
            # Handle case where timezone might be a string depending on API version
            if isinstance(timezone, str):
                tz_offset = timezone
            else:
                tz_offset = timezone.get("offset") if isinstance(timezone, dict) else None
                
            return {
                "station_id": station.get("id"),
                "name": station.get("name"),
                "lat": float(station.get("lat", 0.0)),
                "lon": float(station.get("lng", 0.0)),
                "state": station.get("state"),
                "timezone_offset": tz_offset
            }
    except Exception as e:
        logger.warning(f"Error fetching metadata for station {station_id}: {e}")
        return None
