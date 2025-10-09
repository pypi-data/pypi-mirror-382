import pandas as pd
import requests
from typing import Dict, Any
from .schemas.days import (
    VariableDaysGet, VariableDaysCreate, FixedDaysCreate, FixedDaysGet
)
from brynq_sdk_functions import Functions


class VariableDays:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            employee_id: str,
            created_from: str = None,
            period: int = None,
            year: int = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if period:
            params['period'] = period
        if year:
            params['year'] = year
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}employees/{employee_id}/variabledays",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)

        df = pd.DataFrame(data)

        df['employeeId'] = employee_id  # Add employee_id for tracking
        df['period'] = period
        df['year'] = year
        # Validate data using the schema
        valid_days, invalid_days = Functions.validate_data(df=df, schema=VariableDaysGet, debug=True)

        return valid_days, invalid_days

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create variable hours for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing hours data with fields matching
                 the VariableHoursCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, VariableDaysCreate)
        hours_model = VariableDaysCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return hours_model

        # Convert validated model to dict for API payload
        payload = hours_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/variabledays",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp


class FixedDays:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            company_id: str,
            created_from: str = None,
            employee_id: str = None,
            period: int = None,
            year: int = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if employee_id:
            params['employeeId'] = employee_id
        if period:
            params['period'] = period
        if year:
            params['year'] = year
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}employees/{employee_id}/fixeddays",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.DataFrame(data)
        df['employeeId'] = employee_id  # Add employee_id for tracking
        df['period'] = period
        df['year'] = year

        # Validate data using the schema
        valid_days, invalid_days = Functions.validate_data(df=df, schema=VariableDaysGet, debug=True)

        return valid_days, invalid_days

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create fixed hours for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing hours data with fields matching
                 the FixedHoursCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, FixedDaysCreate)
        hours_model = FixedDaysCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return hours_model

        # Convert validated model to dict for API payload
        payload = hours_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/fixeddays",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp
