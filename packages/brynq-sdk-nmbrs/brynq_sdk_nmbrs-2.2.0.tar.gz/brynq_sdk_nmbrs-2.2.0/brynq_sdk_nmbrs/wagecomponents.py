import math
import pandas as pd
import requests
from typing import Dict, Any
from .schemas.wagecomponents import (
    FixedWageComponentGet,
    VariableWageComponentGet,
    FixedWageComponentCreate, 
    FixedWageComponentUpdate, 
    VariableWageComponentCreate, 
    VariableWageComponentUpdate,
    WageComponentDelete
)
from brynq_sdk_functions import Functions


class EmployeeFixedWageComponents:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None,
            period: int = None,
            year: int = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        wagecomponents = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            wagecomponents = pd.concat([wagecomponents, self._get(company, created_from, employee_id, period, year)])

        valid_wagecomponents, invalid_wagecomponents = Functions.validate_data(df=wagecomponents, schema=FixedWageComponentGet, debug=True)

        return valid_wagecomponents, invalid_wagecomponents

    def _get(self,
            company_id: str,
            created_from: str = None,
            employee_id: str = None,
            period: int = None,
            year: int = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if employee_id:
            params['employeeId'] = employee_id
        if year:
            params['year'] = year
        if period:
            params['period'] = period
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/fixedwagecomponents",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='fixedWageComponents',
            meta=['employeeId']
        )

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new fixed wage component for an employee using Pydantic validation.
        
        Args:
            employee_id: The ID of the employee
            data: Dictionary containing fixed wage component data with fields matching
                 the FixedWageComponentCreate schema (using camelCase field names)
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        wage_component_model = FixedWageComponentCreate(**data)
        
        if self.nmbrs.mock_mode:
            return wage_component_model
        
        # Convert validated model to dict for API payload
        payload = wage_component_model.dict(exclude_none=True)
        
        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/fixedwagecomponent",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update an existing fixed wage component for an employee using Pydantic validation.
        
        Args:
            employee_id: The ID of the employee
            data: Dictionary containing fixed wage component data with fields matching
                 the FixedWageComponentUpdate schema (using camelCase field names)
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        wage_component_model = FixedWageComponentUpdate(**data)
        
        if self.nmbrs.mock_mode:
            return wage_component_model
        
        # Convert validated model to dict for API payload
        payload = wage_component_model.dict(exclude_none=True)
        
        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/fixedwagecomponent",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, wagecomponent_id: str):
        """
        Delete a wage component for an employee.
        
        Args:
            employee_id: The ID of the employee
            wagecomponent_id: The ID of the wage component to delete
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        delete_model = WageComponentDelete(wagecomponentId=wagecomponent_id)
        
        if self.nmbrs.mock_mode:
            return delete_model
            
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/wagecomponents/{wagecomponent_id}",
            timeout=self.nmbrs.timeout
        )
        return resp


class EmployeeVariableWageComponents:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None,
            period: int = None,
            year: int = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        wagecomponents = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            wagecomponents = pd.concat([wagecomponents, self._get(company, created_from, employee_id, period, year)])

        valid_wagecomponents, invalid_wagecomponents = Functions.validate_data(df=wagecomponents, schema=VariableWageComponentGet, debug=True)

        return valid_wagecomponents, invalid_wagecomponents

    def _get(self,
            company_id: str,
            created_from: str = None,
            employee_id: str = None,
            period: int = None,
            year: int = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if employee_id:
            params['employeeId'] = employee_id
        if year:
            params['year'] = year
        if period:
            params['period'] = period
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/variablewagecomponents",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='variablewagecomponents',
            meta=['employeeId']
        )

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new variable wage component for an employee using Pydantic validation.
        
        Args:
            employee_id: The ID of the employee
            data: Dictionary containing variable wage component data with fields matching
                 the VariableWageComponentCreate schema (using camelCase field names)
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        wage_component_model = VariableWageComponentCreate(**data)
        
        if self.nmbrs.mock_mode:
            return wage_component_model
        
        # Convert validated model to dict for API payload
        payload = wage_component_model.dict(exclude_none=True)
        
        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/variablewagecomponent",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update an existing variable wage component for an employee using Pydantic validation.
        
        Args:
            employee_id: The ID of the employee
            data: Dictionary containing variable wage component data with fields matching
                 the VariableWageComponentUpdate schema (using camelCase field names)
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        wage_component_model = VariableWageComponentUpdate(**data)
        
        if self.nmbrs.mock_mode:
            return wage_component_model
        
        # Convert validated model to dict for API payload
        payload = wage_component_model.dict(exclude_none=True)
        
        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/variablewagecomponent",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, wagecomponent_id: str):
        """
        Delete a wage component for an employee.
        
        Args:
            employee_id: The ID of the employee
            wagecomponent_id: The ID of the wage component to delete
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        delete_model = WageComponentDelete(wagecomponentId=wagecomponent_id)
        
        if self.nmbrs.mock_mode:
            return delete_model
            
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/wagecomponents/{wagecomponent_id}",
            timeout=self.nmbrs.timeout
        )
        return resp
