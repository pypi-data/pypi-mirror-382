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
class CostunitGet(BrynQPanderaDataFrameModel):
    cost_unit_id: Series[String] = pa.Field(coerce=True, description="Cost Unit ID", alias="costUnitId")
    code: Series[String] = pa.Field(coerce=True, description="Cost Unit Code", alias="code")
    description: Series[String] = pa.Field(coerce=True, description="Cost Unit Description", alias="description")

    class _Annotation:
        primary_key = "cost_unit_id"

# ---------------------------
# Upload Schemas
# ---------------------------
class CostunitCreate(BaseModel):
    code: str = Field(..., example="CU001", description="Code", alias="code")
    description: str = Field(..., example="Marketing Unit", description="Description", alias="description")

class CostunitUpdate(BaseModel):
    cost_unit_id: str = Field(..., example="b505f980-1c4c-42c1-8ddb-2d90c58da0b2", description="Cost Unit ID", alias="costUnitId")
    code: str = Field(..., example="CU001", description="Code", alias="code")
    description: str = Field(..., example="Marketing Unit", description="Description", alias="description")

    class Config:
        primary_key = "costUnitId"

class CostunitDelete(BaseModel):
    cost_unit_id: str = Field(..., example="b505f980-1c4c-42c1-8ddb-2d90c58da0b2", description="Cost Unit ID", alias="costUnitId")
