from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from src.config import config
from sqlalchemy import create_engine, DateTime, Float, String, Text
from pydantic import Field, BaseModel


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


# EndPoints Response Models


#
class StartBrowserOutput(BaseModel):
    message: str = Field(
        default=..., json_schema_extra={"example": "Browser started for google"}
    )
    process_id: str = Field(
        default=..., json_schema_extra={"example": "google_1694948567"}
    )


class StartBrowserResponse(BaseModel):
    details: StartBrowserOutput = Field(...)


#
class CheckStatusOutput(BaseModel):
    process_id: str = Field(
        default=..., json_schema_extra={"example": "google_1694948567"}
    )
    status: str = Field(default=..., json_schema_extra={"example": "running"})


class CheckStatusResponse(BaseModel):
    details: CheckStatusOutput = Field(...)


#
class ProcessItem(BaseModel):
    process_id: str = Field(
        default=..., json_schema_extra={"example": "google_1694948567"}
    )
    status: str = Field(
        default=..., json_schema_extra={"example": "running"}
    )  # ou "completed", "failed"
    name: str = Field(default=..., json_schema_extra={"example": "google"})
    country: str = Field(default=..., json_schema_extra={"example": "FR"})


class GetProcessesResponse(BaseModel):
    details: List[ProcessItem] = Field(...)


#
#
class GetLogsResponse(BaseModel):
    details: List[str] = Field(
        ...,
        json_schema_extra={
            "example": [
                "2025-09-17 12:00:01 [INFO] Process started",
                "2025-09-17 12:00:05 [INFO] Step 1 completed",
                "2025-09-17 12:01:12 [ERROR] Step 2 failed",
            ]
        },
    )


#
#
class JobSuccessRateOutput(BaseModel):
    platform: str = Field(default=..., json_schema_extra={"example": "google"})
    success_rate: float = Field(
        default=..., json_schema_extra={"example": 0.92}
    )  # valeur entre 0 et 1


class JobSuccessRateResponse(BaseModel):
    details: JobSuccessRateOutput = Field(...)


#
class AverageJobDurationOutput(BaseModel):
    platform: str = Field(..., json_schema_extra={"example": "chatgpt"})
    average_duration: float = Field(
        ..., json_schema_extra={"example": 12.5}
    )  # durée en secondes


class AverageJobDurationResponse(BaseModel):
    details: AverageJobDurationOutput = Field(...)


#
class AverageTotalTimePerPromptItem(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Generate text"})
    average_duration: float = Field(
        ..., json_schema_extra={"example": 3.45}
    )  # en secondes


class AverageTotalTimePerPromptResponse(BaseModel):
    details: List[AverageTotalTimePerPromptItem]


#
class ScraperErrorRateItem(BaseModel):
    platform: str = Field(..., json_schema_extra={"example": "google"})
    error_rate: float = Field(..., json_schema_extra={"example": 0.12})  # 12%


class ScraperErrorRateResponse(BaseModel):
    details: Optional[ScraperErrorRateItem] = Field(
        None, description="Résultat pour la plateforme spécifiée"
    )


#
class PromptCoverageRateItem(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Find hotels in Paris"})
    coverage_rate: float = Field(..., json_schema_extra={"example": 0.85})  # 85%


class PromptCoverageRateResponse(BaseModel):
    details: List[PromptCoverageRateItem] = Field(
        ..., description="Liste des prompts avec leur taux de couverture"
    )


#
class LastRunTimestampItem(BaseModel):
    platform: str = Field(..., json_schema_extra={"example": "google"})
    last_run_timestamp: Optional[str] = Field(
        None,
        description="Horodatage du dernier run au format ISO 8601",
        json_schema_extra={"example": "2025-09-17T10:15:30Z"},
    )


class LastRunTimestampResponse(BaseModel):
    details: LastRunTimestampItem


#
class TotalRunningJobsItem(BaseModel):
    platform: str = Field(..., json_schema_extra={"example": "google"})
    total_running_jobs: int = Field(
        ...,
        description="Nombre total de jobs en cours",
        json_schema_extra={"example": 42},
    )


class TotalRunningJobsResponse(BaseModel):
    details: Optional[TotalRunningJobsItem] = Field(
        None, description="Résultat pour la plateforme donnée"
    )
