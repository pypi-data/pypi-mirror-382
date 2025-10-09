import pandas as pd
import requests
from typing import Dict, Any
from .schemas.hours import (
    VariableHoursCreate, VariableHoursUpdate, HoursDelete,
    FixedHoursCreate, FixedHoursUpdate, VariableHoursGet, FixedHoursGet
)
from brynq_sdk_functions import Functions


class Hours:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get_types(self,
                  company_id: str) -> pd.DataFrame:
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/hourcodes")

        df = self.nmbrs.get_paginated_result(request)

        return df


class VariableHours:
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
                                   url=f"{self.nmbrs.base_url}employees/{employee_id}/variablehours",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)

        df = pd.DataFrame(data)

        df['employeeId'] = employee_id  # Add employee_id for tracking
        df['period'] = period
        df['year'] = year

        # Validate data using the schema
        valid_hours, invalid_hours = Functions.validate_data(df=df, schema=VariableHoursGet, debug=True)

        return valid_hours, invalid_hours

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
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, VariableHoursCreate)
        hours_model = VariableHoursCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return hours_model

        # Convert validated model to dict for API payload
        payload = hours_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/variablehours",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update variable hours for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing hours data with fields matching
                 the VariableHoursUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, VariableHoursUpdate)
        hours_model = VariableHoursUpdate(**nested_data)

        if self.nmbrs.mock_mode:
            return hours_model

        # Convert validated model to dict for API payload
        payload = hours_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/variablehours",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, hourcomponent_id: str):
        """
        Delete hours for an employee.

        Args:
            employee_id: The ID of the employee
            hourcomponent_id: The ID of the hour component to delete

        Returns:
            Response from the API
        """
        # Create and validate a HoursDelete model
        hours_model = HoursDelete(hourComponentId=hourcomponent_id)

        if self.nmbrs.mock_mode:
            return hours_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/hours/{hourcomponent_id}",
            timeout=self.nmbrs.timeout
        )
        return resp


class FixedHours:
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
                                   url=f"{self.nmbrs.base_url}employees/{employee_id}/fixedhours",
                                   params=params)

        df = self.nmbrs.get_paginated_result(request)

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
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, FixedHoursCreate)
        hours_model = FixedHoursCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return hours_model

        # Convert validated model to dict for API payload
        payload = hours_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/fixedhours",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update fixed hours for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing hours data with fields matching
                 the FixedHoursUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, FixedHoursUpdate)
        hours_model = FixedHoursUpdate(**nested_data)

        if self.nmbrs.mock_mode:
            return hours_model

        # Convert validated model to dict for API payload
        payload = hours_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/fixedhours",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, hourcomponent_id: str):
        """
        Delete hours for an employee.

        Args:
            employee_id: The ID of the employee
            hourcomponent_id: The ID of the hour component to delete

        Returns:
            Response from the API
        """
        # Create and validate a HoursDelete model
        hours_model = HoursDelete(hourComponentId=hourcomponent_id)

        if self.nmbrs.mock_mode:
            return hours_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/hours/{hourcomponent_id}",
            timeout=self.nmbrs.timeout
        )
        return resp
