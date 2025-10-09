import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

# ---------------------------
# Get Schemas
# ---------------------------
class AddressGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    address_id: Series[String] = pa.Field(coerce=True, description="Address ID", alias="addressId")
    is_default: Series[Bool] = pa.Field(coerce=True, description="Default Address", alias="isDefault")
    type: Series[String] = pa.Field(
        coerce=True,
        isin=["homeAddress", "postAddress", "absenceAddress", "holidaysAddress", "weekendAddress", "workAddress"],
        description="Address Type",
        alias="type"
    )
    street: Series[String] = pa.Field(coerce=True, description="Street", alias="street")
    house_number: Series[String] = pa.Field(coerce=True, nullable=True, description="House Number", alias="houseNumber")
    house_number_addition: Series[String] = pa.Field(coerce=True, nullable=True, description="House Number Addition", alias="houseNumberAddition")
    postal_code: Series[String] = pa.Field(coerce=True, description="Postal Code", alias="postalCode")
    city: Series[String] = pa.Field(coerce=True, description="City", alias="city")
    state_province: Series[String] = pa.Field(coerce=True, nullable=True, description="State or Province", alias="stateProvince")
    country_i_s_o_code: Series[String] = pa.Field(coerce=True, nullable=True, description="Country ISO code", alias="countryISOCode")
    period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Year", alias="period.year")
    period_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Period", alias="period.period")

    class _Annotation:
        primary_key = "address_id"
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

class Period(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")

class AddressCreate(BaseModel):
    is_default: Optional[bool] = Field(None, description="Default Address", alias="isDefault")
    type: Annotated[
        str,
        StringConstraints(
            pattern=r'^(homeAddress|postAddress|absenceAddress|holidaysAddress|weekendAddress|workAddress)$',
            strip_whitespace=True
        )
    ] = Field(..., example="homeAddress")
    street: str = Field(..., min_length=1, max_length=200, example="Naritaweg", description="Street", alias="street")
    house_number: Optional[str] = Field(None, max_length=20, example="70", description="House Number", alias="houseNumber")
    house_number_addition: Optional[str] = Field(None, max_length=20, example="A", description="House Number Addition", alias="houseNumberAddition")
    postal_code: Optional[str] = Field(None, max_length=15, example="1043BZ", description="Postal Code", alias="postalCode")
    city: str = Field(..., min_length=1, max_length=100, example="Amsterdam", description="City", alias="city")
    state_province: Optional[str] = Field(None, max_length=100, example="Noord-Holland", description="State or Province", alias="stateProvince")
    country_code: Annotated[
        str,
        StringConstraints(
            pattern=r'^[A-Za-z]+$',
            strip_whitespace=True,
            min_length=2,
            max_length=3
        )
    ] = Field(..., example="NL", description="Country ISO Code", alias="countryISOCode")
    period: Period
