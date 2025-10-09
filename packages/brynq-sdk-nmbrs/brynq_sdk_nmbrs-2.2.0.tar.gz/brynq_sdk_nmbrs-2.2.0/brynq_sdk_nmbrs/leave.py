import math
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from typing import Dict, Any
from .schemas.leave import LeaveBalanceGet, LeaveGet, LeaveCreate


class Leave:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            changed_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        leave = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            leave = pd.concat([leave, self._get(company, changed_from)])

        valid_leave, invalid_leave = Functions.validate_data(df=leave, schema=LeaveGet, debug=True)

        return valid_leave, invalid_leave

    def _get(self,
            company_id: str,
            changed_from: str = None) -> pd.DataFrame:
        params = {}
        if changed_from:
            params['changed_from'] = changed_from
        try:
            request = requests.Request(method='GET',
                                       url=f"{self.nmbrs.base_url}companies/{company_id}/employees/leaverequests",
                                       params=params)

            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='EmployeeLeaveRequests',
                meta=['employeeId']
            )
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new leave request for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing leave request data in the format matching LeaveCreate schema

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        nested_data = self.nmbrs.flat_dict_to_nested_dict(data, LeaveCreate)
        leave_model = LeaveCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return leave_model

        # Convert validated model to dict for API payload
        payload = leave_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/leaverequest",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def delete(self, employee_id: str, leave_request_id: str):
        """
        Delete a leave request for an employee.

        Args:
            employee_id: The ID of the employee
            leave_request_id: The ID of the leave request to delete

        Returns:
            Response from the API
        """
        # Create and validate a BankDelete model
        leave_model = LeaveDelete(leave_request_id=leave_request_id)

        if self.nmbrs.mock_mode:
            return leave_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/leave/{leave_request_id}",
            timeout=self.nmbrs.timeout
        )
        return resp


class LeaveBalance:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            changed_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        leave = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            leave = pd.concat([leave, self._get(company, changed_from)])

        valid_leave, invalid_leave = Functions.validate_data(df=leave, schema=LeaveBalanceGet, debug=True)

        return valid_leave, invalid_leave

    def _get(self,
            company_id: str) -> pd.DataFrame:
        try:
            request = requests.Request(method='GET',
                                       url=f"{self.nmbrs.base_url}companies/{company_id}/employees/leaveBalances")

            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='leaveBalances',
                meta=['employeeId']
            )
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df


class LeaveGroup:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            changed_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        leave = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            leave = pd.concat([leave, self._get(company, changed_from)])
