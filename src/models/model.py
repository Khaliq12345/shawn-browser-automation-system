from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from src.config.config import ENGINE


# Process Status Class
class ProcessStatus(SQLModel, table=True):
    process_id: Optional[str] = Field(default=None, primary_key=True)
    status: str
    platform: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    prompt: Optional[str] = None
    duration: Optional[float] = None


# Create all tables of the database
def create_db_and_tables():
    SQLModel.metadata.create_all(ENGINE)
