import pandas as pd
import requests
from typing import Dict, Any
from .schemas.address import AddressCreate, AddressGet, Period
from brynq_sdk_functions import Functions

class Address:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None) -> pd.DataFrame:
        addresses = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            addresses = pd.concat([addresses, self._get(company, created_from)])

        valid_addresses, invalid_addresses = Functions.validate_data(df=addresses, schema=AddressGet, debug=True)

        return valid_addresses, invalid_addresses

    def _get(self,
            company_id: str,
            created_from: str = None) -> pd.DataFrame:
        params = {} if created_from is None else {'createdFrom': created_from}
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/addresses",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='addresses',
            meta=['employeeId']
        )

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new address for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing address data with fields matching
                 the AddressCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, AddressCreate)
        address_model = AddressCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return address_model

        # Convert validated model to dict for API payload
        payload = address_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/address",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp
