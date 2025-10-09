import math
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from typing import Dict, Any
from .schemas.employment import EmploymentGet, EmploymentCreate, EmploymentUpdate, EmploymentDelete


class Employment:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            changed_from: str = None,
            created_from: str = None,
            employee_id: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        employments = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            employments = pd.concat([employments, self._get(company, changed_from, created_from, employee_id)])

        valid_employments, invalid_employments = Functions.validate_data(df=employments, schema=EmploymentGet, debug=True)

        return valid_employments, invalid_employments

    def _get(self,
            company_id: str,
            changed_from: str = None,
            created_from: str = None,
            employee_id: str = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if employee_id:
            params['changedFrom'] = changed_from
        if employee_id:
            params['employeeId'] = employee_id
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/employments",
                                   params=params)
        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='employments',
            meta=['employeeId']
        )

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new employment record for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing employment data with fields matching
                 the EmploymentCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, EmploymentCreate)
        employment_model = EmploymentCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return employment_model

        # Convert validated model to dict for API payload
        payload = employment_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/employment",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update an employment record for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing employment data with fields matching
                 the EmploymentUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, EmploymentUpdate)
        employment_model = EmploymentUpdate(**nested_data)

        if self.nmbrs.mock_mode:
            return employment_model

        # Convert validated model to dict for API payload
        payload = employment_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/employment",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp
