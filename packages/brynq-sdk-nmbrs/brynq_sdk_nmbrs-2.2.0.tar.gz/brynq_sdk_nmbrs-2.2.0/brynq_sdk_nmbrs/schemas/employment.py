import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# ---------------------------
# Get Schemas
# ---------------------------
class EmploymentGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    employment_id: Series[String] = pa.Field(coerce=True, description="Employment ID", alias="employmentId")
    start_date: Series[DateTime] = pa.Field(coerce=True, description="Start Date Employment", alias="startDate")
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="End Date Employment", alias="endDate")
    end_contract_reason: Series[String] = pa.Field(coerce=True, nullable=True, description="End Contract Reason", alias="endContractReason")

    class _Annotation:
        primary_key = "employment_id"
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
class EmploymentCreate(BaseModel):
    start_date: datetime = Field(..., example="2021-06-07T07:59:11Z", description="Start Date Employment", alias="startDate")
    seniority_date: Optional[datetime] = Field(None, example="2021-06-09T07:59:11Z", description="Seniority Date Employment", alias="seniorityDate")

class EmploymentUpdate(BaseModel):
    employment_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Employment ID", alias="employmentId")
    seniority_date: Optional[datetime] = Field(None, example="2021-06-07T07:59:11Z", description="Seniority Date Employment", alias="seniorityDate")
    end_of_service_date: Optional[datetime] = Field(None, example="2021-10-01T00:00:00Z", description="End of Service Date Employment", alias="endOfServiceDate")
    end_of_contract_reason: Optional[int] = Field(None, ge=0, example=3, description="End of Contract Reason Employment", alias="endOfContractReason")

class EmploymentDelete(BaseModel):
    employment_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Employment ID", alias="employmentId")