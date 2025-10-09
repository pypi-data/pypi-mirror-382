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
class DebtorsGet(BrynQPanderaDataFrameModel):
    debtor_id: Series[String] = pa.Field(coerce=True, description="Debtor ID", alias="debtorId")
    number: Series[String] = pa.Field(coerce=True, description="Debtor number", alias="number")
    name: Series[Bool] = pa.Field(coerce=True, description="Debtor name", alias="name")