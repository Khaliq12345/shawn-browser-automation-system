from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from src.config import config
from sqlalchemy import create_engine, DateTime, Float, String, Text


def get_engine():
    engine = create_engine(
        f"postgresql+psycopg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:5432/{config.DB_NAME}"
    )
    return engine


class Base(DeclarativeBase):
    pass


# Process Model
class Processes(Base):
    __tablename__ = "processes"

    process_id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(15))
    platform: Mapped[str] = mapped_column(String(15))
    start_time: Mapped[datetime] = mapped_column(DateTime())
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(), nullable=True)
    prompt: Mapped[str] = mapped_column(Text())
    duration: Mapped[float] = mapped_column(Float(), default=0.0)


# AWS Upload Tracking Model
class AWSUploads(Base):
    __tablename__ = "awsuploads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    aws_key: Mapped[str] = mapped_column(Text())
    browser: Mapped[str] = mapped_column(String(15))
    prompt: Mapped[str] = mapped_column(Text())
    date: Mapped[datetime] = mapped_column(DateTime())


# Create all tables of the database
def create_db_and_tables():
    engine = get_engine()
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    engine.dispose()
