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
class ManagerGet(BrynQPanderaDataFrameModel):
    manager_id: Series[pa.String] = pa.Field(coerce=True, description="Manager unique identifier", alias="managerId")
    number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The manager's number", alias="number")
    first_name: Series[pa.String] = pa.Field(coerce=True, description="The manager's first name", alias="firstName")
    last_name: Series[pa.String] = pa.Field(coerce=True, description="The manager's last name", alias="lastName")
    gender: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="The manager's gender", alias="gender")
    phone_number: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="The manager's phone number", alias="phoneNumber")
    cellphone: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="The manager's cellphone", alias="cellphone")
    fax: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="The manager's fax", alias="fax")
    email: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="The manager's email", alias="email")
    department_id: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Department ID", alias="department.departmentId")
    department_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Department Code", alias="department.code")
    department_description: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Department Description", alias="department.description")
    department_created_at: Series[datetime] = pa.Field(coerce=True, nullable=True, description="Department Created At", alias="department.createdAt")
    function_id: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Function ID", alias="function.functionId")
    function_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Function Code", alias="function.code")
    function_description: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Function Description", alias="function.description")
    function_created_at: Series[datetime] = pa.Field(coerce=True, nullable=True, description="Function Created At", alias="function.createdAt")

    class _Annotation:
        primary_key = "manager_id"

class ManagerBasicGet(BrynQPanderaDataFrameModel):
    manager_id: Series[pa.String] = pa.Field(coerce=True, description="Manager unique identifier", alias="managerId")
    first_name: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager first name", alias="firstName")
    last_name: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager last name", alias="lastName")
    email: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager email", alias="email")

    class _Annotation:
        primary_key = "manager_id"

class EmployeeManagerGet(BrynQPanderaDataFrameModel):
    employee_id: Series[pa.String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    manager_id: Series[pa.String] = pa.Field(coerce=True, description="Manager ID", alias="managerId")
    number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Manager number", alias="number")
    first_name: Series[pa.String] = pa.Field(coerce=True, description="Manager first name", alias="firstName")
    last_name: Series[pa.String] = pa.Field(coerce=True, description="Manager last name", alias="lastName")
    gender: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager gender", alias="gender")
    phone_number: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager phone number", alias="phoneNumber")
    cellphone: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager cellphone", alias="cellphone")
    fax: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager fax", alias="fax")
    email: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager email", alias="email")
    created_at: Series[datetime] = pa.Field(coerce=True, description="Manager created at", alias="createdAt")
    period_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period", alias="period.period")
    period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year", alias="period.year")
    department_id: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Department ID", alias="department.departmentId")
    department_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Department Code", alias="department.code")
    department_description: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Department Description", alias="department.description")
    department_created_at: Series[datetime] = pa.Field(coerce=True, nullable=True, description="Department Created At", alias="department.createdAt")
    function_id: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Function ID", alias="function.functionId")
    function_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Function Code", alias="function.code")
    function_description: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Function Description", alias="function.description")
    function_created_at: Series[datetime] = pa.Field(coerce=True, nullable=True, description="Function Created At", alias="function.createdAt")

    class _Annotation:
        primary_key = "manager_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class ManagerHistoricBasicGet(BrynQPanderaDataFrameModel):
    employee_id: Series[pa.String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    manager_id: Series[pa.String] = pa.Field(coerce=True, description="Manager ID", alias="managerId")
    first_name: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager first name", alias="firstName")
    last_name: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager last name", alias="lastName")
    email: Series[pa.String] = pa.Field(coerce=True, nullable=True, description="Manager email", alias="email")
    created_at: Series[datetime] = pa.Field(coerce=True, description="Manager created at", alias="createdAt")

    class _Annotation:
        primary_key = "manager_id"
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

class ManagerCreate(BaseModel):
    number: int = Field(..., ge=1, example=1, description="Manager number", alias="number")
    first_name: str = Field(..., max_length=100, example="John", description="Manager first name", alias="firstName")
    last_name: str = Field(..., max_length=100, example="Doe", description="Manager last name", alias="lastName")
    gender: Optional[str] = Field(None, example="Male", description="Manager gender", alias="gender")
    phone_number: Optional[str] = Field(None, max_length=50, example="0640986755", description="Manager phone number", alias="phoneNumber")
    cellphone: Optional[str] = Field(None, max_length=50, example="0640986755", description="Manager cellphone", alias="cellphone")
    fax: Optional[str] = Field(None, max_length=50, description="Manager fax", alias="fax")
    email: Optional[str] = Field(None, max_length=100, example="john.doe@company.com", description="Manager email", alias="email")

class ManagerUpdate(BaseModel):
    manager_id: str = Field(..., example="2f6aa11c-504a-49a1-903b-e15e79965702", description="Manager ID", alias="managerId")
    period_details: Period = Field(..., alias="periodDetails")

class ManagerDelete(BaseModel):
    manager_id: str = Field(..., example="2f6aa11c-504a-49a1-903b-e15e79965702", description="Manager ID", alias="managerId")

class UpdateEmployeeManager(BaseModel):
    manager_id: str = Field(..., example="2f6aa11c-504a-49a1-903b-e15e79965702", description="Manager ID", alias="managerId")
    period_details: Period = Field(..., alias="periodDetails")
