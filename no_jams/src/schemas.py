from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class IncidentType(str, Enum):
    accident = "accident"
    roadwork = "roadwork"
    traffic = "traffic"
    hazard = "hazard"
    clozure = "clozure"
    other = "other"


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, Enum):
    new = "new"
    in_process = "in_process"
    done = "done"


class StatusRequest(BaseModel):
    status: Status = Field(..., description="Новый статус")


class Location(BaseModel):
    latitude: float = Field(..., description="Широта")
    longitude: float = Field(..., description="Долгота")


class RoadReport(BaseModel):
    incident_type: IncidentType = Field(..., description="Тип происшествия")
    time: str = Field(
        ..., description="Время происшествия в формате HH:MM", pattern=r"^\d{2}:\d{2}$"
    )
    location: Location = Field(..., description="Местоположение происшествия")
    severity: SeverityLevel = Field(..., description="Серьезность ситуации")
    description: Optional[str] = Field(None, description="Описание происшествия")
