import pandas as pd
import requests
from typing import Dict, Any

from brynq_sdk_functions import Functions
from .schemas.costunit import CostunitGet, CostunitCreate, CostunitUpdate, CostunitDelete


class Costunit:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        costunits = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            costunits = pd.concat([costunits, self._get(company)])

        valid_costunits, invalid_costunits = Functions.validate_data(df=costunits, schema=CostunitGet, debug=True)

        return valid_costunits, invalid_costunits

    def _get(self,
            company_id: str):
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/costunits")

        data = self.nmbrs.get_paginated_result(request)
        df = pd.DataFrame(data)

        return df

    def create(self, company_id: str, data: Dict[str, Any]):
        """
        Create a new costunit using Pydantic validation.

        Args:
            company_id: The ID of the company
            data: Dictionary containing costunit data with fields matching
                 the CostunitCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, CostunitCreate)
        costunit_model = CostunitCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return costunit_model

        # Convert validated model to dict for API payload
        payload = costunit_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}companies/{company_id}/costunit",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, company_id: str, data: Dict[str, Any]):
        """
        Update a costunit using Pydantic validation.

        Args:
            company_id: The ID of the company
            data: Dictionary containing costunit data with fields matching
                 the CostunitUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, CostunitUpdate)
        costunit_model = CostunitUpdate(**nested_data)

        if self.nmbrs.mock_mode:
            return costunit_model

        # Convert validated model to dict for API payload
        payload = costunit_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}companies/{company_id}/costunit",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp
