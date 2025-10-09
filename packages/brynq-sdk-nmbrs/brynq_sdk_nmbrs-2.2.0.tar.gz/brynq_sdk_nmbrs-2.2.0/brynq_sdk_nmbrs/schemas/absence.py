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

#<AbsenceId>int</AbsenceId>
# <Comment>string</Comment>
# <Percentage>int</Percentage>
# <Start>dateTime</Start>
# <RegistrationStartDate>dateTime</RegistrationStartDate>
# <End>dateTime</End>
# <RegistrationEndDate>dateTime</RegistrationEndDate>
# <Dossier>string</Dossier>
# <Dossiernr>int</Dossiernr>

class AbsenceGet(BrynQPanderaDataFrameModel):
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee ID", alias="EmployeeId")
    absence_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Absence ID", alias="AbsenceId")
    comment: Series[String] = pa.Field(coerce=True, description="Comment", alias="Comment")
    percentage: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Percentage", alias="Percentage")
    start: Series[DateTime] = pa.Field(coerce=True, description="Start", alias="Start")
    registration_start_date: Series[DateTime] = pa.Field(coerce=True, description="Registration Start Date", alias="RegistrationStartDate")
    end: Series[DateTime] = pa.Field(coerce=True, description="End", alias="End")
    registration_end_date: Series[DateTime] = pa.Field(coerce=True, description="Registration End Date", alias="RegistrationEndDate")
    dossier: Series[String] = pa.Field(coerce=True, description="Dossier", alias="Dossier")
    dossiernr: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Dossier Number", alias="Dossiernr")


class AbsenceCreate(BaseModel):
    employee_id: Optional[int] = Field(None, example="1234567890", description="Employee ID", alias="EmployeeId")
    absence_id: int = Field(coerce=True, description="Absence ID", alias="AbsenceId")
    comment: str = Field(coerce=True, description="Comment", alias="Comment")
    percentage: int = Field(coerce=True, description="Percentage", alias="Percentage")
    start: datetime = Field(coerce=True, description="Start", alias="Start")
    registration_start_date: datetime = Field(coerce=True, description="Registration Start Date", alias="RegistrationStartDate")
    end: datetime = Field(coerce=True, description="End", alias="End")
    registration_end_date: datetime = Field(coerce=True, description="Registration End Date", alias="RegistrationEndDate")
    dossier: str = Field(coerce=True, description="Dossier", alias="Dossier")
    dossiernr: int = Field(coerce=True, description="Dossier Number", alias="Dossiernr")
    new_dossier: bool = pa.Field(coerce=True, description="New Dossier", alias="NewDossier")


    def to_soap_settings(self, soap_client):
        """Convert to SOAP Absence object"""
        AbsenceType = soap_client.get_type(
            '{https://api.nmbrs.nl/soap/v3/EmployeeService}Absence'
        )

        # Get payload with alias renaming, excluding employee_id field
        payload = self.model_dump(exclude_none=True, by_alias=True, exclude={'employee_id', 'new_dossier'})

        return AbsenceType(**payload)

    class Config:
        populate_by_name = True
