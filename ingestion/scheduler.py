import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncpg
import httpx
import pandas as pd

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/tidedb")
NOAA_BATCH_SIZE = int(os.getenv("NOAA_BATCH_SIZE", "20"))

pool = None

async def init_pool():
    global pool
    db_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)

# --- Inline NOAA Client Functions ---
STATIONS_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=waterlevels"
DATA_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

async def get_all_stations():
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
        logging.warning(f"Error fetching all stations: {e}")
        return []

async def get_station_observations(station_id: str, start_date: datetime, end_date: datetime):
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
            
            if "t" in df.columns:
                df = df.rename(columns={"t": "datetime"})
            if "v" in df.columns:
                df = df.rename(columns={"v": "water_level"})
            if "q" in df.columns:
                df = df.rename(columns={"q": "quality"})
                
            for col in ["datetime", "water_level", "quality"]:
                if col not in df.columns:
                    df[col] = None

            df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce').dt.tz_localize('UTC')
            df["water_level"] = pd.to_numeric(df["water_level"], errors='coerce')
            df = df.dropna(subset=["water_level"])
            df = df[df["quality"] != "M"]
            
            return df[["datetime", "water_level", "quality"]].copy()
            
    except Exception as e:
        logging.warning(f"Error fetching observations for station {station_id}: {e}")
        return pd.DataFrame(columns=["datetime", "water_level", "quality"])

# --- Scheduler Jobs ---
async def startup_backfill():
    logger = logging.getLogger("startup_backfill")
    logger.info("Starting startup_backfill...")
    
    stations = await get_all_stations()
    async with pool.acquire() as conn:
        for st in stations:
            await conn.execute('''
                INSERT INTO stations (station_id, name, state, lat, lon, is_active)
                VALUES ($1, $2, $3, $4, $5, true)
                ON CONFLICT (station_id) DO UPDATE SET name=EXCLUDED.name, is_active=true
            ''', st["station_id"], st["name"], st["state"], st["lat"], st["lon"])
            
    top_20 = [
        "8443970","8724580","9414290","8518750","8771341",
        "8761927","9447130","8467150","8534720","8665530",
        "8419317","8510560","9410660","8771013","8638610",
        "9462620","1612340","8454049","8726520","9414750"
    ]
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    for station_id in top_20:
        async with pool.acquire() as conn:
            count = await conn.fetchval('''
                SELECT COUNT(*) FROM observations 
                WHERE station_id=$1 AND timestamp > NOW() - INTERVAL '30 days'
            ''', station_id)
            
            if count < 100:
                logger.info(f"Backfilling station {station_id} (count={count}) for last 30 days")
                df = await get_station_observations(station_id, start_date, end_date)
                if not df.empty:
                    records = []
                    for _, row in df.iterrows():
                        records.append((station_id, row["datetime"].to_pydatetime().replace(tzinfo=None), row["water_level"], row["quality"]))
                    
                    if records:
                        await conn.executemany('''
                            INSERT INTO observations (station_id, timestamp, water_level, quality_flag)
                            VALUES ($1, $2, $3, $4)
                            ON CONFLICT (station_id, timestamp) DO NOTHING
                        ''', records)
                        logger.info(f"Inserted {len(records)} records for station {station_id}")
            else:
                logger.info(f"Station {station_id} has sufficient data (count={count}), skipping backfill.")

async def hourly_fetch():
    logger = logging.getLogger("hourly_fetch")
    logger.info("Starting hourly_fetch...")
    
    async with pool.acquire() as conn:
        records = await conn.fetch("SELECT station_id FROM stations WHERE is_active = true")
        station_ids = [r["station_id"] for r in records]
        
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(hours=2)
    
    total_inserted = 0
    for i in range(0, len(station_ids), NOAA_BATCH_SIZE):
        batch = station_ids[i:i+NOAA_BATCH_SIZE]
        logger.info(f"Fetching batch {i//NOAA_BATCH_SIZE + 1} of {(len(station_ids)-1)//NOAA_BATCH_SIZE + 1}")
        
        tasks = [get_station_observations(sid, start_date, end_date) for sid in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for sid, res in zip(batch, results):
            if isinstance(res, Exception):
                logger.error(f"Error fetching data for {sid}: {res}")
                continue
            if res.empty:
                continue
                
            db_records = []
            for _, row in res.iterrows():
                db_records.append((sid, row["datetime"].to_pydatetime().replace(tzinfo=None), row["water_level"], row["quality"]))
                
            if db_records:
                async with pool.acquire() as conn:
                    await conn.executemany('''
                        INSERT INTO observations (station_id, timestamp, water_level, quality_flag)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (station_id, timestamp) DO NOTHING
                    ''', db_records)
                    
                    await conn.execute('''
                        UPDATE stations SET last_fetched = NOW() WHERE station_id = $1
                    ''', sid)
                    total_inserted += len(db_records)
                    
        await asyncio.sleep(2)
        
    logger.info(f"hourly_fetch completed. Total new observations processed: {total_inserted}")

async def invalidate_forecast_cache():
    logger = logging.getLogger("invalidate_forecast_cache")
    logger.info("Starting invalidate_forecast_cache...")
    async with pool.acquire() as conn:
        status = await conn.execute('''
            DELETE FROM forecast_cache
            WHERE created_at < NOW() - INTERVAL '6 hours'
        ''')
        logger.info(f"invalidate_forecast_cache completed: {status} rows deleted.")

async def create_tables():
    logger = logging.getLogger("create_tables")
    logger.info("Creating tables if they don't exist...")
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS stations (
                station_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(200),
                state VARCHAR(50),
                lat FLOAT,
                lon FLOAT,
                is_active BOOLEAN DEFAULT true,
                last_fetched TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS observations (
                id SERIAL PRIMARY KEY,
                station_id VARCHAR(20) REFERENCES stations(station_id),
                timestamp TIMESTAMP,
                water_level FLOAT,
                quality_flag VARCHAR(5),
                UNIQUE(station_id, timestamp)
            );
            CREATE TABLE IF NOT EXISTS forecast_cache (
                id SERIAL PRIMARY KEY,
                station_id VARCHAR(20) REFERENCES stations(station_id),
                created_at TIMESTAMP DEFAULT NOW(),
                horizon_hours INTEGER DEFAULT 168,
                timestamps JSON,
                q10 JSON,
                q25 JSON,
                q50 JSON,
                q75 JSON,
                q90 JSON
            );
        ''')
        logger.info("Tables created.")

async def main():
    await init_pool()
    await create_tables()
    await startup_backfill()
    
    scheduler = AsyncIOScheduler(timezone=timezone.utc)
    scheduler.add_job(hourly_fetch, "interval", hours=1, id="hourly_fetch")
    scheduler.add_job(invalidate_forecast_cache, "interval", hours=6, id="cache_invalidate")
    scheduler.start()
    
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(main())