import pandas as pd
import requests
import math
from brynq_sdk_functions import Functions
from .schemas.schedules import ScheduleGet, ScheduleCreate
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class Schedule:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        schedules = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            schedules = pd.concat([schedules, self._get(company, created_from, employee_id)])

        valid_schedules, invalid_schedules = Functions.validate_data(df=schedules, schema=ScheduleGet, debug=True)

        return valid_schedules, invalid_schedules

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
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/schedules",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='schedules',
            meta=['employeeId']
        )
        return df

    def create(self,
               employee_id: str,
               data: Dict[str, Any]):
        """
        Create a new schedule for an employee using Pydantic validation

        Args:
            employee_id: The employee ID
            data: Schedule data dictionary with the following keys:
                - start_date_schedule: Start date of the schedule
                - weekly_hours: Hours per week (optional)
                - hours_monday, hours_tuesday, etc.: Hours for each day

        Returns:
            Response from the API
        """
        # Validate with Pydantic schema
        try:
            nested_data = self.nmbrs.flat_dict_to_nested_dict(data, ScheduleCreate)
            validated_data = ScheduleCreate(**nested_data)

            if self.nmbrs.mock_mode:
                return validated_data

            # Convert validated model to dict for API payload
            payload = validated_data.model_dump_json(exclude_none=True, by_alias=True)

            # Use the validated data for the API call
            resp = self.nmbrs.session.post(
                url=f"{self.nmbrs.base_url}employees/{employee_id}/schedule",
                data=payload,
                timeout=self.nmbrs.timeout,
                headers={'Content-Type': 'application/json'}
            )
            return resp

        except Exception as e:
            raise ValueError(f"Schedule validation failed: {str(e)}")
