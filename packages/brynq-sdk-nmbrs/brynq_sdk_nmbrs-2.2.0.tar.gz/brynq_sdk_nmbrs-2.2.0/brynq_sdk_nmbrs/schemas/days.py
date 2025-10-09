import pandas as pd
import requests
import pandera as pa
from pandera.typing import Series, String, Float, DateTime
import pandas as pd
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional
from pydantic import BaseModel, Field

# ---------------------------
# Get Schemas
# ---------------------------
# PANDERA SCHEMA
class VariableDaysGet(BrynQPanderaDataFrameModel):
    days: Series[String] = pa.Field(coerce=True, description="Hour Component ID", alias="days")
    days_for_wage_components_per_day: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Hour Code", alias="daysForWageComponentsPerDay")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")

    class Config:
        coerce = True

class FixedDaysGet(BrynQPanderaDataFrameModel):
    days: Series[String] = pa.Field(coerce=True, description="Hour Component ID", alias="days")
    days_for_wage_components_per_day: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Hour Code", alias="daysForWageComponentsPerDay")
    end_year: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True, description="End Year", alias="endYear")
    end_period: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True, description="End Period", alias="endPeriod")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")

    class Config:
        coerce = True

# ---------------------------
# Upload Schemas
# ---------------------------
class PeriodModel(BaseModel):
    year: Optional[int] = Field(None, ge=1900, le=2100, example=2025, description="Year", alias="year")
    period: Optional[int] = Field(None, ge=1, le=53, example=1, description="Period", alias="period")

class PeriodPost(BaseModel):
    period: Optional[PeriodModel] = Field(None, description="Period", alias="period")
    unprotected_mode: Optional[bool] = Field(None, example=False, description="Unprotected Mode", alias="unprotectedMode")

class FixedHoursCreate(BaseModel):
    hour_code: int = Field(..., ge=1, example=2100, description="Hour Code", alias="hourCode")
    hours: float = Field(..., ge=0, le=1000, example=40, description="Hours", alias="hours")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    comment: Optional[str] = Field(None, example="Regular working hours with full details", description="Comment", alias="comment")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, example=2025, description="End Year", alias="endYear")
    end_period: Optional[int] = Field(None, ge=1, le=53, example=12, description="End Period", alias="endPeriod")
    period_details: Optional[PeriodPost] = None

class FixedHoursUpdate(BaseModel):
    hour_component_id: str = Field(..., example="ddaae291-47fa-4c67-bb2f-de0e5da9e8a1", description="Hour Component ID", alias="hourComponentId")
    hour_code: Optional[int] = Field(None, ge=1, example=2100, description="Hour Code", alias="hourCode")
    hours: Optional[float] = Field(None, ge=0, le=1000, example=40, description="Hours", alias="hours")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    comment: Optional[str] = Field(None, example="Comment about update", description="Comment", alias="comment")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, example=2025, description="End Year", alias="endYear")
    end_period: Optional[int] = Field(None, ge=1, le=53, example=12, description="End Period", alias="endPeriod")
    period_details: Optional[PeriodPost] = None

class VariableHoursCreate(BaseModel):
    hour_code: int = Field(..., ge=1, example=2100, description="Hour Code", alias="hourCode")
    hours: float = Field(..., ge=0, le=1000, example=3.5, description="Hours", alias="hours")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    comment: Optional[str] = Field(None, example="Shift hours", description="Comment", alias="comment")
    period_details: Optional[PeriodPost] = Field(None, example="Period details", description="Period details", alias="periodDetails")

class VariableHoursUpdate(BaseModel):
    hour_component_id: str = Field(..., example="49a69eda-252e-4ccb-a220-38ea90511d4f", description="Hour Component ID", alias="hourComponentId")
    hour_code: Optional[int] = Field(None, ge=1, example=2100, description="Hour Code", alias="hourCode")
    hours: Optional[float] = Field(None, ge=0, le=1000, example=45.5, description="Hours", alias="hours")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    comment: Optional[str] = Field(None, example="Comment about update", description="Comment", alias="comment")
    period_details: Optional[PeriodPost] = None

class HoursDelete(BaseModel):
    hour_component_id: str = Field(..., example="49a69eda-252e-4ccb-a220-38ea90511d4f", description="Hour Component ID", alias="hourComponentId")


class FixedDaysCreate(BaseModel):
    number_of_days: int = Field(..., ge=0, le=1000, example=40, description="Days", alias="days")
    days_for_wage_components_per_day: Optional[int] = Field(None, ge=0, le=1000, example=40, description="Days for Wage Components per Day", alias="daysForWageComponentsPerDay")
    period_details: Optional[PeriodPost] = Field(None, example="Period details", description="Period details", alias="periodDetails")

class VariableDaysCreate(BaseModel):
    number_of_days: int = Field(..., ge=0, le=1000, example=40, description="Days", alias="days")
    days_for_wage_components_per_day: Optional[int] = Field(None, ge=0, le=1000, example=40, description="Days for Wage Components per Day", alias="daysForWageComponentsPerDay")
    period_details: Optional[PeriodPost] = Field(None, example="Period details", description="Period details", alias="periodDetails")
