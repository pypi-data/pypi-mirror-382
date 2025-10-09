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
class ContractGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    contract_id: Series[String] = pa.Field(coerce=True, description="Contract ID", alias="contractId")
    start_date: Series[DateTime] = pa.Field(coerce=True, description="Start Date Contract", alias="startDate")
    trial_period: Series[String] = pa.Field(coerce=True, nullable=True, description="Trial Period Contract", alias="trialPeriod")
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="End Date Contract", alias="endDate")
    indefinite: Series[Bool] = pa.Field(coerce=True, description="Indefinite Contract", alias="indefinite")
    written_contract: Series[Bool] = pa.Field(coerce=True, description="Written Contract", alias="writtenContract")
    weekly_hours: Series[Float] = pa.Field(coerce=True, nullable=True, description="Contract Hours per Week", alias="hoursPerWeek")
    created_at: Series[DateTime] = pa.Field(coerce=True, description="Contract Created At", alias="createdAt")

    class _Annotation:
        primary_key = "contract_id"
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
class ContractCreate(BaseModel):
    start_date_contract: datetime = Field(..., example="2021-01-01T09:29:18Z", description="Start Date Contract", alias="startDate")
    trial_period: Optional[datetime] = Field(None, example="2021-02-01T00:00:00Z", description="Trial Period Contract", alias="trialPeriod")
    end_date_contract: Optional[datetime] = Field(None, example="2021-08-24T14:15:22Z", description="End Date Contract", alias="endDate")
    indefinite_contract: bool = Field(..., example=True, description="Indefinite Contract", alias="indefinite")
    written_contract: Optional[bool] = Field(None, example=True, description="Written Contract", alias="writtenContract")
    weekly_hours: Optional[float] = Field(None, ge=0, le=168, example=40, description="Contract Hours per Week", alias="hoursPerWeek")

class ContractUpdate(BaseModel):
    contract_id: str = Field(..., example="e35e343b-55a3-4e44-bc4b-f41c3b93bcf5", description="Contract ID", alias="contractId")
    trial_period: Optional[datetime] = Field(None, example="2021-07-31T00:00:00Z", description="Trial Period Contract", alias="trialPeriod")
    end_date_contract: Optional[datetime] = Field(None, example="2021-12-31T00:00:00Z", description="End Date Contract", alias="endDate")
    indefinite_contract: bool = Field(..., example=True, description="Indefinite Contract", alias="indefinite")
    written_contract: Optional[bool] = Field(None, example=True, description="Written Contract", alias="writtenContract")
    weekly_hours: Optional[float] = Field(None, ge=0, le=168, example=20, description="Contract Hours per Week", alias="hoursPerWeek")

    class Config:
        primary_key = "contractId"

class ContractDelete(BaseModel):
    contract_id: str = Field(..., example="e35e343b-55a3-4e44-bc4b-f41c3b93bcf5", description="Contract ID", alias="contractId")
