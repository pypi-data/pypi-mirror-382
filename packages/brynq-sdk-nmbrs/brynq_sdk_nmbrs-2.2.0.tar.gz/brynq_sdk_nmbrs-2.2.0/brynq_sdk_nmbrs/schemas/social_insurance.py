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

class SocialInsuranceUpdate(BaseModel):
    employee_id: int = Field(None, example="1234567890", description="Employee ID", alias="EmployeeId")
    influence_obliged_insurance: Optional[bool] = Field(None, example="1234567890", description="Influence Obliged Insurance", alias="InfluenceObligedInsurance")
    wage_cost_benefit: bool = Field(..., example="1234567890", description="Wage Cost Benefit", alias="WageCostBenefit")
    code_cao: int = Field(..., example="1234567890", description="Code Cao", alias="CodeCao")
    wao_wia: bool = Field(..., example="1234567890", description="Wao Wia", alias="Wao_Wia")
    ww: bool = Field(..., example="1234567890", description="Ww", alias="Ww")
    zw: bool = Field(..., example="1234567890", description="Zw", alias="Zw")
    income_related_contribution_zvw: bool = Field(None, example="1234567890", description="Income Related Contribution Zvw", alias="IncomeRelatedContributionZvw")
    code_zvw: Optional[int] = Field(None, example="1234567890", description="Code Zvw", alias="CodeZvw")
    risk_group: int = Field(None, example="1234567890", description="Risk Group", alias="RiskGroup")
    sector: int = Field(None, example="1234567890", description="Sector", alias="Sector")
    employment_type: int = Field(None, example="1234567890", description="Employment Type", alias="EmploymentType")
    phase_classification: int = Field(None, example="1234567890", description="Phase Classification", alias="PhaseClassification")
    employment_sequence_tax_id: int = Field(None, example="1234567890", description="Employment Sequence Tax Id", alias="EmploymentSequenceTaxId")

    def to_soap_settings(self, soap_client):
        """Convert to SOAP SVWSettings object"""
        SVWSettingsType = soap_client.get_type(
            '{https://api.nmbrs.nl/soap/v3/EmployeeService}SVWSettings'
        )

        # Get payload with alias renaming, excluding employee_id field
        payload = self.model_dump(exclude_none=True, by_alias=True, exclude={'employee_id'})

        return SVWSettingsType(**payload)

    class Config:
        populate_by_name = True
