import math
import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Float
from brynq_sdk_functions import BrynQPanderaDataFrameModel

from typing import Optional
from pydantic import BaseModel, Field, conint, confloat


# ---------------------------
# Get Schemas
# ---------------------------
class FixedWageComponentGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    fixed_wage_component_id: Series[String] = pa.Field(coerce=True, description="Fixed Wage Component ID", alias="fixedWageComponentId")
    code: Series[String] = pa.Field(coerce=True, description="Wage Component Code", alias="code")
    value: Series[Float] = pa.Field(coerce=True, description="Wage Component Value", alias="value")
    end_year: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True, description="End Year", alias="endYear")
    end_period: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True, description="End Period", alias="endPeriod")
    comment: Series[String] = pa.Field(nullable=True, coerce=True, description="Comment", alias="comment")
    cost_center_id: Series[String] = pa.Field(nullable=True, coerce=True, description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Series[String] = pa.Field(nullable=True, coerce=True, description="Cost Unit ID", alias="costUnitId")

    class Config:
        coerce = True

    class _Annotation:
        primary_key = "fixed_wage_component_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class VariableWageComponentGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    variable_wage_component_id: Series[String] = pa.Field(coerce=True, description="Variable Wage Component ID", alias="variableWageComponentId")
    code: Series[String] = pa.Field(coerce=True, description="Wage Component Code", alias="code")
    value: Series[Float] = pa.Field(coerce=True, description="Wage Component Value", alias="value")
    comment: Series[String] = pa.Field(nullable=True, coerce=True, description="Comment", alias="comment")
    cost_center_id: Series[String] = pa.Field(nullable=True, coerce=True, description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Series[String] = pa.Field(nullable=True, coerce=True, description="Cost Unit ID", alias="costUnitId")

    class Config:
        coerce = True

    class _Annotation:
        primary_key = "variable_wage_component_id"
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
class PeriodPost(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")

class FixedWageComponentCreate(BaseModel):
    code: int = Field(..., ge=1, example=1100, description="Wage Component Code", alias="code")
    value: float = Field(..., ge=0, example=500, description="Wage Component Value", alias="value")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, example=2023, description="End Year", alias="endYear")
    end_period: Optional[int] = Field(None, ge=1, le=53, example=6, description="End Period", alias="endPeriod")
    comment: Optional[str] = Field(None, example="some comment", description="Comment", alias="comment")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    period_details: PeriodPost
    unprotected_mode: Optional[bool] = Field(None, example=True, description="Unprotected Mode", alias="unprotectedMode")

class FixedWageComponentUpdate(BaseModel):
    fixed_wage_component_id: str = Field(..., example="643c6b90-57c6-4199-9e4e-ded553572d78", description="Fixed Wage Component ID", alias="fixedWageComponentId")
    code: Optional[int] = Field(None, ge=1, example=1100, description="Wage Component Code", alias="code")
    value: Optional[float] = Field(None, ge=0, example=500, description="Wage Component Value", alias="value")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, example=2023, description="End Year", alias="endYear")
    end_period: Optional[int] = Field(None, ge=1, le=53, example=6, description="End Period", alias="endPeriod")
    comment: Optional[str] = Field(None, example="string", description="Comment", alias="comment")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    period_details: Optional[PeriodPost] = None
    unprotected_mode: Optional[bool] = Field(None, example=True, description="Unprotected Mode", alias="unprotectedMode")

class VariableWageComponentCreate(BaseModel):
    code: int = Field(..., ge=1, example=3045, description="Wage Component Code", alias="code")
    value: float = Field(..., ge=0, example=200, description="Wage Component Value", alias="value")
    comment: Optional[str] = Field(None, example="comment", description="Comment", alias="comment")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    period_details: PeriodPost
    unprotected_mode: Optional[bool] = Field(None, example=True, description="Unprotected Mode", alias="unprotectedMode")

class VariableWageComponentUpdate(BaseModel):
    variable_wage_component_id: str = Field(..., example="7fc59095-daed-4746-a7f8-a454e38e3683", description="Variable Wage Component ID", alias="variableWageComponentId")
    code: Optional[int] = Field(None, ge=1, example=3045, description="Wage Component Code", alias="code")
    value: Optional[float] = Field(None, ge=0, example=2200, description="Wage Component Value", alias="value")
    comment: Optional[str] = Field(None, example="comment", description="Comment", alias="comment")
    cost_center_id: Optional[str] = Field(None, example="aa506564-d1db-4fa8-83dc-d68db4cfcd82", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="d8ac6afb-2ac6-43bf-9880-2d382cdace43", description="Cost Unit ID", alias="costUnitId")
    period_details: Optional[PeriodPost] = None
    unprotected_mode: Optional[bool] = Field(None, example=True, description="Unprotected Mode", alias="unprotectedMode")

class WageComponentDelete(BaseModel):
    wage_component_id: str = Field(..., example="7fc59095-daed-4746-a7f8-a454e38e3683", description="Wage Component ID", alias="wageComponentId")