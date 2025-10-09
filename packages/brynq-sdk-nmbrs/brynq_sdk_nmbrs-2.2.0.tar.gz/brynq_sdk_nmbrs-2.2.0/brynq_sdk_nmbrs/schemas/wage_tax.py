import math
import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints
from datetime import datetime


class WageTaxGet(BrynQPanderaDataFrameModel):
    wagetax_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Loonaangifte ID", alias="LoonaangifteID")
    serial_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Serial Number", alias="SerialNumber")
    payment_reference: Series[String] = pa.Field(coerce=True, description="Payment Reference", alias="PaymentReference")
    total_general: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Total General", alias="TotalGeneral")
    period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period", alias="Period")
    year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year", alias="Year")
    status: Series[String] = pa.Field(coerce=True, description="Status", alias="Status")
    sent_at: Series[DateTime] = pa.Field(coerce=True, description="Sent At", alias="SentAt")
    period_start: Series[DateTime] = pa.Field(coerce=True, description="Tijdvak Start", alias="TijdvakStart")
    period_end: Series[DateTime] = pa.Field(coerce=True, description="Tijdvak End", alias="TijdvakEnd")
    correction_period_start: Series[DateTime] = pa.Field(nullable=True, coerce=True, description="Correction Tijdvak Start", alias="CorrectionTijdvakStart")
    correction_period_end: Series[DateTime] = pa.Field(nullable=True, coerce=True, description="Correction Tijdvak End", alias="CorrectionTijdvakEnd")


class WageTaxUpdate(BaseModel):
    employee_id: Optional[int] = Field(None, example="1234567890", description="Employee ID", alias="EmployeeId")
    wage_tax_id: Optional[int] = Field(None, example="1234567890", description="Wage Tax Settings ID", alias="Id")
    yearly_salary: Optional[float] = Field(None, example="1234567890", description="Yearly Salary", alias="JaarloonBT")
    deviation_special_rate_payroll_tax_deduction: Optional[float] = Field(None, example="1234567890", description="Afw Bijz Tarief LH", alias="AfwBijzTariefLH")
    auto_small_jobs: Optional[bool] = Field(None, example="1234567890", description="Auto Kleine Banen Regeling", alias="AutoKleineBanenRegeling")
    payroll_tax_deduction: Optional[bool] = Field(None, example="1234567890", description="Loonheffingkorting", alias="Loonheffingkorting")
    benefit_scheme: Optional[bool] = Field(None, example="1234567890", description="Voordeelreg", alias="Voordeelreg")
    payroll_tax: Optional[bool] = Field(None, example="1234567890", description="Loonheffing", alias="Loonheffing")
    code_tax_reduction: Optional[int] = Field(None, example="1234567890", description="Code Afdrachtvermindering", alias="CodeAfdrachtvermindering")
    color_table: Optional[int] = Field(None, example="1234567890", description="Kleur Tabel", alias="KleurTabel")
    type_of_income: Optional[int] = Field(None, example="1234567890", description="Soort Inkomen", alias="SoortInkomen")
    special_table: Optional[int] = Field(None, example="1234567890", description="Speciale Tabel", alias="SpecialeTabel")
    period_table: Optional[int] = Field(None, example="1234567890", description="Tijdvak Tabel", alias="TijdvakTabel")
    holiday_vouchers: Optional[int] = Field(None, example="1234567890", description="Vakantie Bonnen", alias="VakantieBonnen")
    code_calculate_30_percent_rule: Optional[int] = Field(None, example="1234567890", description="Code Calc 30% Rule", alias="CodeCalc30PercRule")

    def to_soap_settings(self, soap_client):
        """Convert to SOAP WageTaxSettings object"""
        WageTaxSettingsType = soap_client.get_type(
            '{https://api.nmbrs.nl/soap/v3/EmployeeService}WageTaxSettings'
        )

        # Get payload with alias renaming, excluding employee_id field
        payload = self.model_dump(exclude_none=True, by_alias=True, exclude={'employee_id'})

        return WageTaxSettingsType(**payload)

    class Config:
        populate_by_name = True
