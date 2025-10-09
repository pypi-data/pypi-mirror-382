import math
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from typing import Dict, Any
from .schemas.bank import BankGet, BankCreate, BankUpdate, BankDelete


class Bank:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        banks = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            banks = pd.concat([banks, self._get(company, created_from)])

        valid_banks, invalid_banks = Functions.validate_data(df=banks, schema=BankGet, debug=True)

        return valid_banks, invalid_banks

    def _get(self,
            company_id: str,
            created_from: str = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        try:
            request = requests.Request(method='GET',
                                       url=f"{self.nmbrs.base_url}companies/{company_id}/employees/bankaccounts",
                                       params=params)

            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='bankAccounts',
                meta=['employeeId']
            )
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new bank account for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing bank account data in the format matching BankCreate schema

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, BankCreate)
        bank_model = BankCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return bank_model

        # Convert validated model to dict for API payload
        payload = bank_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/bankaccount",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update a bank account for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing bank account data in the format matching BankUpdate schema

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, BankUpdate)
        bank_model = BankUpdate(**nested_data)

        if self.nmbrs.mock_mode:
            return bank_model

        # Convert validated model to dict for API payload
        payload = bank_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/bankaccount",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, bank_account_id: str):
        """
        Delete a bank account for an employee.

        Args:
            employee_id: The ID of the employee
            bank_account_id: The ID of the bank account to delete

        Returns:
            Response from the API
        """
        # Create and validate a BankDelete model
        bank_model = BankDelete(bankAccountId=bank_account_id)

        if self.nmbrs.mock_mode:
            return bank_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/bankaccounts/{bank_account_id}",
            timeout=self.nmbrs.timeout
        )
        return resp
