import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints
from enum import Enum

# ---------------------------
# Enums
# ---------------------------
class BankAccountType(str, Enum):
    BANK_ACCOUNT_1 = "bankAccount1"
    BANK_ACCOUNT_2 = "bankAccount2"
    BANK_ACCOUNT_3 = "bankAccount3"
    BANK_ACCOUNT_4 = "bankAccount4"
    BANK_ACCOUNT_5 = "bankAccount5"
    SALARY_SAVINGS = "salarySavings"
    LIFECYCLE_SAVING_SCHEMES = "lifecycleSavingSchemes"
    STANDARD = "standard"

# ---------------------------
# Get Schemas
# ---------------------------
class BankGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    bank_account_id: Series[String] = pa.Field(coerce=True, nullable=True, description="Bank Account ID", alias="bankAccountId")
    number: Series[String] = pa.Field(coerce=True, nullable=True, description="Bank Account Number", alias="number")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="Bank Account Description", alias="description")
    iban: Series[String] = pa.Field(coerce=True, nullable=True, description="IBAN", alias="IBAN")
    city: Series[String] = pa.Field(coerce=True, nullable=True, description="City Bank", alias="city")
    name: Series[String] = pa.Field(coerce=True, nullable=True, description="Name Bank", alias="name")
    bank_account_type: Series[String] = pa.Field(
        coerce=True,
        isin=BankAccountType,
        description="Bank Account Type",
        alias="bankAccountType"
    )
    created_at: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Bank Account Created At", alias="createdAt")

    class _Annotation:
        primary_key = "bank_account_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "1:1"
            }
        }

# ---------------------------
# Upload Schemas
# ---------------------------
class BankCreate(BaseModel):
    number: Optional[str] = Field(None, max_length=34, example="123456789", description="Bank Account Number", alias="number")
    description: Optional[str] = Field(None, max_length=100, example="Salary Bank", description="Bank Account Description", alias="description")
    iban: str = Field(..., min_length=5, max_length=34, example="NL20INGB0001234567", description="IBAN", alias="IBAN")
    city: Optional[str] = Field(None, max_length=100, example="Amsterdam", description="City Bank", alias="city")
    name: Optional[str] = Field(None, max_length=100, example="ING Bank", description="Name Bank", alias="name")
    bank_account_type: Optional[BankAccountType] = Field(None, example=BankAccountType.BANK_ACCOUNT_1.value, description="Bank Account Type", alias="bankAccountType")

class BankUpdate(BaseModel):
    bank_account_id: str = Field(..., example="49a69eda-252e-4ccb-a220-38ea90511d4f", description="Bank Account ID", alias="bankAccountId")
    number: Optional[str] = Field(None, max_length=34, example="123456789", description="Bank Account Number", alias="number")
    description: Optional[str] = Field(None, max_length=100, example="Main Checking Account", description="Bank Account Description", alias="description")
    iban: Optional[str] = Field(None, min_length=5, max_length=34, example="NL20INGB0001234567", description="IBAN", alias="IBAN")
    city: Optional[str] = Field(None, max_length=100, example="Rotterdam", description="City Bank", alias="city")
    name: Optional[str] = Field(None, max_length=100, example="ABN AMRO", description="Name Bank", alias="name")
    country_code: Optional[Annotated[
        str,
        StringConstraints(
            pattern=r'^[A-Za-z]+$',
            strip_whitespace=True,
            min_length=2,
            max_length=3
        )
    ]] = Field(None, example="NL", description="Country Code Bank", alias="countryCode")

class BankDelete(BaseModel):
    bank_account_id: str = Field(..., example="49a69eda-252e-4ccb-a220-38ea90511d4f", description="Bank Account ID")
