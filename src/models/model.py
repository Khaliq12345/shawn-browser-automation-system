from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class Browsers(SQLModel, table=True):
    process_id: str = Field(primary_key=True)
    status: str
    platform: str
    start_time: datetime
    end_time: Optional[datetime] = Field(default=None)
    prompt: str
    duration: float = Field(default=0.0)
    brand_report_id: str = Field(foreign_key="reports.brand_report_id")


class Reports(SQLModel, table=True):
    brand_report_id: str = Field(primary_key=True)
    languague: str
    country: str
    brand: str
    domain: str
    date: datetime


class Schedules(SQLModel, table=True):
    prompt_id: str = Field(primary_key=True)
    prompt: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    brand_report_id: str = Field(foreign_key="reports.brand_report_id")
