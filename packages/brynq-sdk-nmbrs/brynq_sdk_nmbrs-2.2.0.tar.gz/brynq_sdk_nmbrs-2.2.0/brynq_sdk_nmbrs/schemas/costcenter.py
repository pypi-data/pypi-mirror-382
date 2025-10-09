import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# ---------------------------
# Get Schemas
# ---------------------------
class EmployeeCostcenterGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    employee_cost_center_id: Series[String] = pa.Field(coerce=True, description="Employee Cost Center ID", alias="employeeCostCenterId")
    cost_centers_cost_center_id: Series[String] = pa.Field(coerce=True, description="Cost Center ID", alias="costCenters.costCenterId")
    cost_centers_code: Series[String] = pa.Field(coerce=True, description="Cost Centers Code", alias="costCenters.code")
    cost_centers_description: Series[String] = pa.Field(coerce=True, description="Cost Centers Description", alias="costCenters.description")
    cost_units_cost_unit_id: Series[String] = pa.Field(coerce=True, description="Cost Unit ID", alias="costUnits.costUnitId")
    cost_units_code: Series[String] = pa.Field(coerce=True, description="Cost Unit Code", alias="costUnits.code")
    cost_units_description: Series[String] = pa.Field(coerce=True, description="Cost Unit Description", alias="costUnits.description")
    percentage: Series[Float] = pa.Field(coerce=True, description="Percentage", alias="percentage")
    default: Series[Bool] = pa.Field(coerce=True, description="Default", alias="default")
    period_year: Series[int] = pa.Field(coerce=True, description="Year", alias="period.year")
    period_period: Series[int] = pa.Field(coerce=True, description="Period", alias="period.period")
    created_at: Series[DateTime] = pa.Field(coerce=True, description="Created At", alias="createdAt")

    class _Annotation:
        primary_key = "employee_cost_center_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class CostcenterGet(BrynQPanderaDataFrameModel):
    cost_center_id: Series[String] = pa.Field(coerce=True, description="Cost Center ID", alias="costCenterId")
    code: Series[String] = pa.Field(coerce=True, description="Code", alias="code")
    description: Series[String] = pa.Field(coerce=True, description="Description", alias="description")

    class _Annotation:
        primary_key = "cost_center_id"

# ---------------------------
# Upload Schemas
# ---------------------------
class CostcenterTable(BaseModel):
    costcenter_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")
    costunit_id: Optional[str] = Field(None, example="b505f980-1c4c-42c1-8ddb-2d90c58da0b2", description="Cost Unit ID", alias="costUnitId")
    percentage: Optional[float] = Field(100, example=100, description="Percentage", alias="percentage")
    default: Optional[bool] = Field(True, example=True, description="Default", alias="default")


class Period(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")


class EmployeeCostcenterUpdate(BaseModel):
    employee_id: str = Field(..., example="c605f980-1c4c-42c1-8ddb-2d90c58da0b3", description="Employee Cost Center ID", alias="employeeId")
    employee_cost_centers: List[CostcenterTable] = Field(..., description="Employee Cost Centers", alias="employeeCostCenters")
    period_details: Period = Field(..., example=Period(year=2021, period=4), description="Period details", alias="period")

    class Config:
        primary_key = "employee_id"


class EmployeeCostcenterDelete(BaseModel):
    employee_cost_center_id: str = Field(..., example="c605f980-1c4c-42c1-8ddb-2d90c58da0b3", description="Employee Cost Center ID", alias="employeeCostCenterId")

# CostCenter CRUD schemas - These are hypothetical since the API doesn't have create/update/delete endpoints
# but we add them for consistency with other schema files
class CostcenterCreate(BaseModel):
    code: str = Field(..., example="CC001", description="Code", alias="code")
    description: str = Field(..., example="Sales Department", description="Description", alias="description")

class CostcenterUpdate(BaseModel):
    cost_center_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")
    code: str = Field(..., example="CC001", description="Code", alias="code")
    description: str = Field(..., example="Sales Department", description="Description", alias="description")

    class Config:
        primary_key = "costCenterId"

class CostcenterDelete(BaseModel):
    cost_center_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")
