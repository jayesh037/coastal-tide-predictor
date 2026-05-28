import asyncio
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers.stations import router as stations_router
from routers.forecast import router as forecast_router
from services.noaa_client import get_station_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Coastal Tide Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stations_router, prefix="/api")
app.include_router(forecast_router, prefix="/api")

@app.websocket("/ws/live/{station_id}")
async def websocket_live(websocket: WebSocket, station_id: str):
    await websocket.accept()
    try:
        while True:
            meta = await get_station_metadata(station_id)
            if meta:
                await websocket.send_json({
                    "station_id": station_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "water_level": None
                })
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for station {station_id}")

@app.on_event("startup")
async def startup_event():
    logger.info("API started")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)