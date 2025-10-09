import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints
from enum import Enum
from datetime import datetime


class LeaveGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    leave_requests_id: Series[String] = pa.Field(coerce=True, nullable=True, description="Leave Requests ID", alias="leaveRequestsId")
    leave_group_id: Series[String] = pa.Field(coerce=True, nullable=True, description="Leave Group ID", alias="leaveGroupId")
    status: Series[String] = pa.Field(coerce=True, nullable=True, description="Leave Status", alias="status")
    leave_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Leave Type", alias="type")
    start_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Leave Start Date", alias="startDate")
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Leave End Date", alias="endDate")
    hours: Series[Float] = pa.Field(coerce=True, nullable=True, description="Leave Hours", alias="hours")
    created_at: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Leave Created At   ", alias="createdAt")
    changed_at: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Leave Changed At", alias="changedAt")

    class _Annotation:
        primary_key = "leave_requests_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }


class LeaveCreate(BaseModel):
    leave_group_id: str = Field(..., example="49a69eda-252e-4ccb-a220-38ea90511d4f", description="Leave Group ID", alias="leaveGroupId")
    start_date: datetime = Field(..., example="2025-01-01", description="Leave Start Date", alias="startDate")
    end_date: datetime = Field(..., example="2025-01-02", description="Leave End Date", alias="endDate")
    hours: float = Field(..., example=8.0, description="Leave Hours", alias="hours")
    description: Optional[str] = Field(None, example="Comment about leave request", description="Comment", alias="description")
    status: str = Field(..., example="Comment about leave request", description="Comment", alias="status")
    leave_type: str = Field(..., example="vacation", description="Leave Type", alias="type")


class LeaveDelete(BaseModel):
    leave_request_id: str = Field(..., example="49a69eda-252e-4ccb-a220-38ea90511d4f", description="Leave Request ID", alias="leaveRequestId")


class LeaveBalanceGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    leave_group_id: Series[String] = pa.Field(coerce=True, nullable=True, description="Leave Group ID", alias="leaveGroupId")
    balance: Series[Float] = pa.Field(coerce=True, nullable=True, description="Leave Balance", alias="leaveBalance")
