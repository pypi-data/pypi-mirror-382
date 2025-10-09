import math
import pandas as pd
import pandera as pa
from pandera.typing import Series, String, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

# ---------------------------
# Get Schemas
# ---------------------------
class EmployeeGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    personal_info_id: Series[String] = pa.Field(coerce=True, description="Personal Info ID", alias="personalInfoId")
    created_at: Series[DateTime] = pa.Field(coerce=True, description="Employee Created At", alias="createdAt", nullable=True)
    basic_info_employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee Number", alias="basicInfo.employeeNumber")
    basic_info_first_name: Series[String] = pa.Field(coerce=True, nullable=True, description="First Name", alias="basicInfo.firstName")
    basic_info_first_name_in_full: Series[String] = pa.Field(coerce=True, nullable=True, description="First Name In Full", alias="basicInfo.firstNameInFull")
    basic_info_prefix: Series[String] = pa.Field(coerce=True, nullable=True, description="Prefix", alias="basicInfo.prefix")
    basic_info_initials: Series[String] = pa.Field(coerce=True, nullable=True, description="Initials", alias="basicInfo.initials")
    basic_info_last_name: Series[String] = pa.Field(coerce=True, description="Last Name", alias="basicInfo.lastName")
    basic_info_employee_type: Series[String] = pa.Field(coerce=True, description="Employee Type", alias="basicInfo.employeeType")
    birth_info_birth_date: Series[DateTime] = pa.Field(coerce=True, description="Birth Date", alias="birthInfo.birthDate")
    birth_info_birth_country_code_iso: Series[String] = pa.Field(coerce=True, nullable=True, description="Birth Country Code ISO", alias="birthInfo.birthCountry.codeISO")
    birth_info_nationality_code_iso: Series[String] = pa.Field(coerce=True, nullable=True, description="Nationality Code ISO", alias="birthInfo.nationality.codeISO")
    birth_info_gender: Series[String] = pa.Field(coerce=True, nullable=True, description="Gender", alias="birthInfo.gender")
    contact_info_private_email: Series[String] = pa.Field(coerce=True, nullable=True, description="Private Email", alias="contactInfo.privateEmail")
    contact_info_business_email: Series[String] = pa.Field(coerce=True, nullable=True, description="Business Email", alias="contactInfo.businessEmail")
    contact_info_business_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Business Phone", alias="contactInfo.businessPhone")
    contact_info_business_mobile_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Business Mobile Phone", alias="contactInfo.businessMobilePhone")
    contact_info_private_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Private Phone", alias="contactInfo.privatePhone")
    contact_info_private_mobile_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Private Mobile Phone", alias="contactInfo.privateMobilePhone")
    contact_info_other_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Other Phone", alias="contactInfo.otherPhone")
    partner_info_partner_prefix: Series[String] = pa.Field(coerce=True, nullable=True, description="Partner Prefix", alias="partnerInfo.partnerPrefix")
    partner_info_partner_name: Series[String] = pa.Field(coerce=True, nullable=True, description="Partner Name", alias="partnerInfo.partnerName")
    period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year", alias="period.year")
    period_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period", alias="period.period")
    birth_info_birth_country: Series[String] = pa.Field(coerce=True, nullable=True, description="Birth Country", alias="birthInfo.birthCountry")
    company_id: Series[String] = pa.Field(coerce=True, description="Company ID", alias="companyId")

    class _Annotation:
        primary_key = "employee_id"

# ---------------------------
# Upload Schemas
# ---------------------------
class BasicInfo(BaseModel):
    employee_id: Optional[int] = Field(None, ge=1, example=98072, description="Employee Number", alias="employeeNumber")
    first_name: Optional[str] = Field(None, max_length=50, example="John", description="First Name", alias="firstName")
    first_name_in_full: Optional[str] = Field(None, max_length=100, example="John in Full", description="First Name In Full", alias="firstNameInFull")
    prefix: Optional[str] = Field(None, max_length=50, example="van der", description="Prefix", alias="prefix")
    initials: Optional[str] = Field(None, max_length=50, example="J.D.", description="Initials", alias="initials")
    last_name: str = Field(..., max_length=100, example="Doe", description="Last Name", alias="lastName")
    employee_type: Annotated[
        str,
        StringConstraints(
            pattern=r'^(applicant|newHire|payroll|formerPayroll|external|formerExternal|rejectedApplicant)$',
            strip_whitespace=True
        )
    ] = Field(..., example="payroll", description="Employee Type", alias="employeeType")

class BasicInfoUpdate(BaseModel):
    employee_id: Optional[int] = Field(None, ge=1, example=98072, description="Employee Number", alias="employeeNumber")
    first_name: Optional[str] = Field(None, max_length=50, example="John", description="First Name", alias="firstName")
    first_name_in_full: Optional[str] = Field(None, max_length=100, example="John in Full", description="First Name In Full", alias="firstNameInFull")
    prefix: Optional[str] = Field(None, max_length=50, example="van der", description="Prefix", alias="prefix")
    initials: Optional[str] = Field(None, max_length=50, example="J.D.", description="Initials", alias="initials")
    last_name: str = Field(..., max_length=100, example="Doe", description="Last Name", alias="lastName")

class BirthInfo(BaseModel):
    birth_date: Optional[str] = Field(None, example="1980-02-27", description="Birth Date", alias="birthDate")
    birth_country_code_iso: Optional[Annotated[
        str,
        StringConstraints(
            pattern=r'^[A-Za-z]+$',
            strip_whitespace=True,
            min_length=2,
            max_length=3
        )
    ]] = Field(None, example="NL", description="Birth Country Code ISO", alias="birthCountryCodeISO")
    nationality: Optional[Annotated[
        str,
        StringConstraints(
            pattern=r'^[A-Za-z]+$',
            strip_whitespace=True,
            min_length=2, 
            max_length=3
        )
    ]] = Field(None, example="PT", description="Nationality Code ISO", alias="nationalityCodeISO")
    deceased_on: Optional[str] = Field(None, example="1980-02-27", description="Deceased On", alias="deceasedOn")
    gender: Optional[Annotated[
        str,
        StringConstraints(
            pattern=r'^(unspecified|male|female|unknown)$',
            strip_whitespace=True
        )
    ]] = Field(None, example="male", description="Gender", alias="gender")

class ContactInfo(BaseModel):
    email_private: Optional[str] = Field(None, max_length=100, example="doe@private.com", description="Private Email", alias="privateEmail")
    email_work: Optional[str] = Field(None, max_length=100, example="doe@business.com", description="Business Email", alias="businessEmail")
    phone_work: Optional[str] = Field(None, max_length=50, example="+351222222", description="Business Phone", alias="businessPhone")
    mobile_work: Optional[str] = Field(None, max_length=50, example="+351222222", description="Business Mobile Phone", alias="businessMobilePhone")
    private_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Private Phone", alias="privatePhone")
    private_mobile_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Private Mobile Phone", alias="privateMobilePhone")
    other_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Other Phone", alias="otherPhone")

class PartnerInfo(BaseModel):
    partner_prefix: Optional[str] = Field(None, max_length=50, example="Mstr", description="Partner Prefix", alias="partnerPrefix")
    partner_name: Optional[str] = Field(None, max_length=100, example="Jane Doe", description="Partner Name", alias="partnerName")
    ascription_code: Optional[int] = Field(None, ge=0, example=0, description="Ascription Code", alias="ascriptionCode")

class Period(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")

class AdditionalEmployeeInfo(BaseModel):
    in_service_date: str = Field(..., example="2019-08-24", description="In Service Date", alias="inServiceDate")
    default_employee_template: Optional[str] = Field(None, description="Default Employee Template", alias="defaultEmployeeTemplate")

class CreateEmployeePersonalInfo(BaseModel):
    basic_info: BasicInfo  = Field(..., alias="basicInfo")
    birth_info: BirthInfo = Field(..., alias="birthInfo")
    contact_info: ContactInfo = Field(..., alias="contactInfo")
    partner_info: PartnerInfo = Field(..., alias="partnerInfo")
    period: Period = Field(..., alias="period")
    created_at: Optional[str] = Field(None, example="2021-07-01T10:15:08Z", description="Created At", alias="createdAt")

class EmployeeCreate(BaseModel):
    personal_info: CreateEmployeePersonalInfo = Field(..., alias="personalInfo")
    additional_employee_info: AdditionalEmployeeInfo = Field(..., alias="additionalEmployeeInfo")

class EmployeeUpdate(BaseModel):
    basic_info: Optional[BasicInfoUpdate] = Field(None, alias="basicInfo")
    birth_info: Optional[BirthInfo] = Field(None, alias="birthInfo")
    contact_info: Optional[ContactInfo] = Field(None, alias="contactInfo")
    partner_info: Optional[PartnerInfo] = Field(None, alias="partnerInfo")
    period: Period = Field(..., alias="period")

class EmployeeDelete(BaseModel):
    employee_id: str = Field(..., example="3054d4cf-b449-489d-8d2e-5dd30e5ab994", description="Employee ID", alias="employeeId")
