import pandas as pd
import requests
from brynq_sdk_functions import Functions as BrynQFunctions
import math
from typing import Dict, Any
from .schemas.manager import (
    ManagerGet, ManagerBasicGet, EmployeeManagerGet, ManagerHistoricBasicGet,
    ManagerCreate, ManagerUpdate, ManagerDelete, UpdateEmployeeManager
)


class EmployeeManager:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self, created_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employee manager history for all companies.

        Args:
            created_from: Optional filter to get managers created from a specific date

        Returns:
            Tuple of (valid_managers, invalid_managers) DataFrames
        """
        managers = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            managers = pd.concat([managers, self._get(company, created_from)])

        valid_managers, invalid_managers = BrynQFunctions.validate_data(df=managers, schema=EmployeeManagerGet, debug=True)

        return valid_managers, invalid_managers

    def _get(self, company_id: str, created_from: str = None) -> pd.DataFrame:
        """
        Get employee manager history for a specific company.

        Args:
            company_id: The ID of the company
            created_from: Optional filter to get managers created from a specific date

        Returns:
            DataFrame containing employee manager data
        """
        params = {}
        if created_from:
            params['createdFrom'] = created_from

        try:
            request = requests.Request(
                method='GET',
                url=f"{self.nmbrs.base_url}companies/{company_id}/employees/managers",
                params=params
            )
            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='managers',
                meta=['employeeId']
            )
            df['companyId'] = company_id
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df

    def get_historic_basic(self, created_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get historic basic manager information for employees.

        Args:
            created_from: Optional filter to get managers created from a specific date

        Returns:
            Tuple of (valid_managers, invalid_managers) DataFrames
        """
        managers = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            managers = pd.concat([managers, self._get_historic_basic(company, created_from)])

        valid_managers, invalid_managers = BrynQFunctions.validate_data(df=managers, schema=ManagerHistoricBasicGet, debug=True)

        return valid_managers, invalid_managers

    def _get_historic_basic(self, company_id: str, created_from: str = None) -> pd.DataFrame:
        """
        Get historic basic manager information for a specific company.

        Args:
            company_id: The ID of the company
            created_from: Optional filter to get managers created from a specific date

        Returns:
            DataFrame containing historic basic manager data
        """
        params = {}
        if created_from:
            params['createdFrom'] = created_from

        try:
            request = requests.Request(
                method='GET',
                url=f"{self.nmbrs.base_url}companies/{company_id}/employees/managers",
                params=params
            )
            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='managers',
                meta=['employeeId']
            )
            df['companyId'] = company_id
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update the manager of a specific employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing manager data with fields matching
                 the UpdateEmployeeManager schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        manager_model = UpdateEmployeeManager(**data)

        if self.nmbrs.mock_mode:
            return manager_model

        # Convert validated model to dict for API payload
        payload = manager_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/manager",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp


class Manager:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self, debtor_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get all managers for a specific debtor.

        Args:
            debtor_id: The ID of the debtor

        Returns:
            Tuple of (valid_managers, invalid_managers) DataFrames
        """
        try:
            request = requests.Request(
                method='GET',
                url=f"{self.nmbrs.base_url}debtors/{debtor_id}/managers"
            )

            data = self.nmbrs.get_paginated_result(request)
            df = pd.DataFrame(data)
            df['debtorId'] = debtor_id

            valid_managers, invalid_managers = BrynQFunctions.validate_data(df=df, schema=ManagerGet, debug=True)

        except requests.HTTPError as e:
            df = pd.DataFrame()
            valid_managers = df
            invalid_managers = df

        return valid_managers, invalid_managers

    def get_basic(self, debtor_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get basic manager information for a specific debtor.

        Args:
            debtor_id: The ID of the debtor

        Returns:
            Tuple of (valid_managers, invalid_managers) DataFrames
        """
        try:
            request = requests.Request(
                method='GET',
                url=f"{self.nmbrs.base_url}debtors/{debtor_id}/managers"
            )

            data = self.nmbrs.get_paginated_result(request)
            df = pd.DataFrame(data)
            df['debtorId'] = debtor_id

            valid_managers, invalid_managers = BrynQFunctions.validate_data(df=df, schema=ManagerBasicGet, debug=True)

        except requests.HTTPError as e:
            df = pd.DataFrame()
            valid_managers = df
            invalid_managers = df

        return valid_managers, invalid_managers

    def create(self, debtor_id: str, data: Dict[str, Any]):
        """
        Create a new manager using Pydantic validation.

        Args:
            debtor_id: The ID of the debtor
            data: Dictionary containing manager data with fields matching
                 the ManagerCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        manager_model = ManagerCreate(**data)

        if self.nmbrs.mock_mode:
            return manager_model

        # Convert validated model to dict for API payload
        payload = manager_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}debtors/{debtor_id}/managers",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, debtor_id: str, data: Dict[str, Any]):
        """
        Update a manager using Pydantic validation.

        Args:
            debtor_id: The ID of the debtor
            data: Dictionary containing manager data with fields matching
                 the ManagerUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        manager_model = ManagerUpdate(**data)

        if self.nmbrs.mock_mode:
            return manager_model

        # Convert validated model to dict for API payload
        payload = manager_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}debtors/{debtor_id}/managers/{payload['managerId']}",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, debtor_id: str, data: Dict[str, Any]):
        """
        Delete a manager using Pydantic validation.

        Args:
            debtor_id: The ID of the debtor
            data: Dictionary containing manager data with fields matching
                 the ManagerDelete schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        manager_model = ManagerDelete(**data)

        if self.nmbrs.mock_mode:
            return manager_model

        # Convert validated model to dict for API payload
        payload = manager_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}debtors/{debtor_id}/managers/{payload['managerId']}",
            timeout=self.nmbrs.timeout
        )
        return resp
