from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

STATUSES = {"idea", "building", "submitted", "won"}
PRIORITIES = {"low", "medium", "high"}


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    team_name: str = Field(..., min_length=1, max_length=120)
    hackathon: str = Field(..., min_length=1, max_length=120)
    track: str = Field(default="open", max_length=120)
    status: str = Field(default="idea")
    priority: str = Field(default="medium")
    description: Optional[str] = None
    deadline: Optional[date] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in STATUSES:
            raise ValueError(f"status must be one of {sorted(STATUSES)}")
        return v

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, v: str) -> str:
        if v not in PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(PRIORITIES)}")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    team_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    hackathon: Optional[str] = Field(default=None, min_length=1, max_length=120)
    track: Optional[str] = Field(default=None, max_length=120)
    status: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v is not None and v not in STATUSES:
            raise ValueError(f"status must be one of {sorted(STATUSES)}")
        return v

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, v):
        if v is not None and v not in PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(PRIORITIES)}")
        return v


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
