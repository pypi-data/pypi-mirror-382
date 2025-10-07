from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Schedule(BaseModel):
    interval: int = Field(..., gt=0)
    interval_units: Optional[Literal["minutes", "hours", "days"]] = Field(
        None, alias="intervalUnits"
    )
    crontab: Optional[str]
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")

    class Config:
        populate_by_name = True
