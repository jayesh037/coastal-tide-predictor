# backend/models/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class StationSchema(BaseModel):
    station_id: str
    name: str
    state: Optional[str]
    lat: float
    lon: float
    is_active: bool = True

class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONPoint
    properties: StationSchema

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

class ObservationSchema(BaseModel):
    timestamp: datetime
    water_level: float

class HistoryResponse(BaseModel):
    station_id: str
    days: int
    observations: List[ObservationSchema]

class ForecastResponse(BaseModel):
    station_id: str
    generated_at: datetime
    horizon_hours: int
    timestamps: List[str]
    q10: List[float]
    q25: List[float]
    q50: List[float]
    q75: List[float]
    q90: List[float]
    actuals: List[float]

class LiveReading(BaseModel):
    station_id: str
    timestamp: datetime
    water_level: float