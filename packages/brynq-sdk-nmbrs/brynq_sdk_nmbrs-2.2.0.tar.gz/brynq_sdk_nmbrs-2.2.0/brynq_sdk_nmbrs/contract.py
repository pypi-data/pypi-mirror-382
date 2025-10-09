import math
import pandas as pd
import requests
from typing import Dict, Any
from .schemas.contracts import ContractGet, ContractCreate, ContractUpdate, ContractDelete
from brynq_sdk_functions import Functions


class Contract:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None) -> (pd.DataFrame, pd.DataFrame):
        contracts = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            contracts = pd.concat([contracts, self._get(company, created_from, employee_id)])

        valid_contracts, invalid_contracts = Functions.validate_data(df=contracts, schema=ContractGet, debug=True)

        return valid_contracts, invalid_contracts

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
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/contracts",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='contracts',
            meta=['employeeId']
        )

        df['company_id'] = company_id

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new contract for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing contract data with fields matching
                 the ContractCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, ContractCreate)
        contract_model = ContractCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return contract_model

        # Convert validated model to dict for API payload
        payload = contract_model.model_dump_json(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/contract",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update a contract for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing contract data with fields matching
                 the ContractUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, ContractUpdate)
        contract_model = ContractUpdate(**nested_data)

        if self.nmbrs.mock_mode:
            return contract_model

        # Convert validated model to dict for API payload
        payload = contract_model.model_dump_json(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/contract",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, contract_id: str):
        """
        Delete a contract for an employee.

        Args:
            employee_id: The ID of the employee
            contract_id: The ID of the contract to delete

        Returns:
            Response from the API
        """
        # Create and validate a ContractDelete model
        contract_model = ContractDelete(contractId=contract_id)

        if self.nmbrs.mock_mode:
            return contract_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/contracts/{contract_id}",
            timeout=self.nmbrs.timeout
        )
        return resp
