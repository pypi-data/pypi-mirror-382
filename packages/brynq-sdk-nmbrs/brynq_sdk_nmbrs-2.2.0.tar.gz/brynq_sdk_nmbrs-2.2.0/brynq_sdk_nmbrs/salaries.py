import math
import pandas as pd
import requests
from typing import Dict, Any
from brynq_sdk_functions import Functions
from .schemas.salary import SalaryGet, SalaryCreate


class Salaries:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        salaries = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            salaries = pd.concat([salaries, self._get(company, created_from, employee_id)])

        valid_salaries, invalid_salaries = Functions.validate_data(df=salaries, schema=SalaryGet, debug=True)

        return valid_salaries, invalid_salaries

    def _get(self,
            company_id: str,
            created_from: str = None,
            employee_id: str = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if employee_id:
            params['employeeId'] = employee_id
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/salaries",
                                   params=params)
        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='salaries',
            meta=['employeeId']
        )
        return df

    def get_salary_tables(self,
            salary_table_id: str) -> pd.DataFrame:
        params = {}
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}salarytable/{salary_table_id}",
                                   params=params)
        data = self.nmbrs.get_paginated_result(request)

        df = pd.DataFrame(data)

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new salary for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing salary data with fields matching
                 the SalaryCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, SalaryCreate)
        salary_model = SalaryCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return salary_model

        # Convert validated model to dict for API payload
        payload = salary_model.model_dump_json(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/salary",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.nmbrs.timeout
        )
        return resp
