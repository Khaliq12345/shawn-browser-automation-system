from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from src.config import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy import DateTime, Float, String, Text


def get_engine():
    engine = create_async_engine(
        f"postgresql+psycopg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
    )
    return engine


class Base(DeclarativeBase):
    pass


# Process Status Class
class ProcessStatus(SQLModel, table=True):
    process_id: Optional[str] = Field(default=None, primary_key=True)
    status: str
    platform: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    prompt: Optional[str] = None
    duration: Optional[float] = None


class Processes(AsyncAttrs, Base):
    __tablename__ = "processes"

    process_id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(15))
    platform: Mapped[str] = mapped_column(String(15))
    start_time: Mapped[datetime] = mapped_column(DateTime())
    end_time: Mapped[datetime] = mapped_column(DateTime())
    prompt: Mapped[str] = mapped_column(Text())
    duration: Mapped[float] = mapped_column(Float())


# Create all tables of the database
async def create_db_and_tables():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
