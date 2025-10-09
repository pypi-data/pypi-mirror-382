from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import pandera as pa
from pandera import Bool, Int
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, Field

# ---------------------------
# Get Schemas
# ---------------------------
class ScheduleGet(BrynQPanderaDataFrameModel):
    schedule_id: Series[String] = pa.Field(coerce=True, description="Schedule ID", alias="scheduleId")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start Date", alias="startDate")
    parttime_percentage: Series[Float] = pa.Field(coerce=True, description="Part-Time Percentage", alias="parttimePercentage")
    week1_hours_monday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Monday", alias="week1.hoursMonday")
    week1_hours_tuesday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Tuesday", alias="week1.hoursTuesday")
    week1_hours_wednesday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Wednesday", alias="week1.hoursWednesday")
    week1_hours_thursday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Thursday", alias="week1.hoursThursday")
    week1_hours_friday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Friday", alias="week1.hoursFriday")
    week1_hours_saturday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Saturday", alias="week1.hoursSaturday")
    week1_hours_sunday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Sunday", alias="week1.hoursSunday")
    week2_hours_monday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Monday", alias="week2.hoursMonday")
    week2_hours_tuesday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Tuesday", alias="week2.hoursTuesday")
    week2_hours_wednesday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Wednesday", alias="week2.hoursWednesday")
    week2_hours_thursday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Thursday", alias="week2.hoursThursday")
    week2_hours_friday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Friday", alias="week2.hoursFriday")
    week2_hours_saturday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Saturday", alias="week2.hoursSaturday")
    week2_hours_sunday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Sunday", alias="week2.hoursSunday")
    created_at: Series[datetime] = pa.Field(coerce=True, description="Created At", alias="createdAt")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")

    class _Annotation:
        primary_key = "schedule_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }


# ---------------------------
# Upload Schemas
# ---------------------------
class ScheduleHours(BaseModel):
    """Schedule hours for each day of the week"""
    hours_monday: Optional[float] = Field(None, description="Monday hours", alias="hoursMonday")
    hours_tuesday: Optional[float] = Field(None, description="Tuesday hours", alias="hoursTuesday")
    hours_wednesday: Optional[float] = Field(None, description="Wednesday hours", alias="hoursWednesday")
    hours_thursday: Optional[float] = Field(None, description="Thursday hours", alias="hoursThursday")
    hours_friday: Optional[float] = Field(None, description="Friday hours", alias="hoursFriday")
    hours_saturday: Optional[float] = Field(None, description="Saturday hours", alias="hoursSaturday")
    hours_sunday: Optional[float] = Field(None, description="Sunday hours", alias="hoursSunday")

class ScheduleCreate(BaseModel):
    """
    Pydantic model for creating a new schedule
    """
    start_date_schedule: datetime = Field(..., description="Start date of the schedule", example="2021-01-01T09:29:18Z", alias="startDate")
    hours_per_week: Optional[float] = Field(None, description="Hours per week", example=40, alias="hoursPerWeek")
    week1: Optional[ScheduleHours] = Field(None, description="Week 1 schedule hours", alias="week1")
    week2: Optional[ScheduleHours] = Field(None, description="Week 2 schedule hours", alias="week2")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "start_date": "2021-01-01T09:29:18Z",
                "hours_per_week": 40,
                "week1": {
                    "hours_monday": 8,
                    "hours_tuesday": 8,
                    "hours_wednesday": 8,
                    "hours_thursday": 8,
                    "hours_friday": 2.5,
                    "hours_saturday": 0,
                    "hours_sunday": 0
                },
                "week2": {
                    "hours_monday": 8,
                    "hours_tuesday": 8,
                    "hours_wednesday": 8,
                    "hours_thursday": 8,
                    "hours_friday": 2.5,
                    "hours_saturday": 0,
                    "hours_sunday": 0
                }
            }
        }
