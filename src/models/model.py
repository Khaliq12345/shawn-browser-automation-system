from sqlmodel import Field, SQLModel
from src.config.config import ENGINE


class ProcessStatus(SQLModel, table=True):
    process_id: str | None = Field(default=None, primary_key=True)
    status: str


def create_db_and_tables():
    SQLModel.metadata.create_all(ENGINE)
