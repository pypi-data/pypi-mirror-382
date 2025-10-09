from datetime import datetime

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel

from typing import Optional
from pydantic import BaseModel, Field

# ---------------------------
# Get Schemas
# ---------------------------
class EmployeeFunctionGet(BrynQPanderaDataFrameModel):
    employee_id: Series[pa.String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    function_id: Series[pa.String] = pa.Field(coerce=True, description="Function ID", alias="functionId")
    code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Function Code", alias="code")
    description: Series[pa.String] = pa.Field(coerce=True, description="Function Description", alias="description")
    created_at: Series[datetime] = pa.Field(coerce=True, description="Function Created At", alias="createdAt")
    period_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period", alias="period.period")
    period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year", alias="period.year")

    class _Annotation:
        primary_key = "function_id"
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
class Period(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")

class FunctionGet(BrynQPanderaDataFrameModel):
    function_id: Series[pa.String] = pa.Field(coerce=True, description="Function ID", alias="functionId")
    code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Function Code", alias="code")
    description: Series[pa.String] = pa.Field(coerce=True, description="Function Description", alias="description")
    created_at: Series[datetime] = pa.Field(coerce=True, description="Function Created At", alias="createdAt")

class FunctionUpdate(BaseModel):
    function_id: str = Field(..., example="5981", description="Function ID", alias="functionId")
    period_details: Period = Field(..., alias="periodDetails")
