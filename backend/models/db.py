# backend/models/db.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Boolean, DateTime, Integer, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/tidedb")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class Base(DeclarativeBase):
    pass

class Station(Base):
    __tablename__ = "stations"
    station_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    state: Mapped[str] = mapped_column(String(50), nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_fetched: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Observation(Base):
    __tablename__ = "observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(20), ForeignKey("stations.station_id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    water_level: Mapped[float] = mapped_column(Float)
    quality_flag: Mapped[str] = mapped_column(String(5), nullable=True)
    
    __table_args__ = (UniqueConstraint("station_id", "timestamp"),)

class ForecastCache(Base):
    __tablename__ = "forecast_cache"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(20), ForeignKey("stations.station_id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    horizon_hours: Mapped[int] = mapped_column(Integer, default=168)
    timestamps: Mapped[list] = mapped_column(JSON)
    q10: Mapped[list] = mapped_column(JSON)
    q25: Mapped[list] = mapped_column(JSON)
    q50: Mapped[list] = mapped_column(JSON)
    q75: Mapped[list] = mapped_column(JSON)
    q90: Mapped[list] = mapped_column(JSON)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)