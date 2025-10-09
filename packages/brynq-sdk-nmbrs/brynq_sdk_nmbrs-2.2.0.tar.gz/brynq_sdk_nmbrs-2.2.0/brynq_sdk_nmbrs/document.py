from io import BytesIO

import pandas as pd
import requests


class Payslip:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            employee_id: str,
            period: int = None,
            year: int = None) -> pd.DataFrame:
        params = {}
        if period:
            params['period'] = period
        if year:
            params['year'] = year
        resp = self.nmbrs.session.get(f"{self.nmbrs.base_url}employees/{employee_id}/payslipperperiod/",
                                      params=params,
                                      timeout=self.nmbrs.timeout)
        resp.raise_for_status()
        task_id = resp.json()['taskId']

        resp = self.nmbrs.session.get(f"{self.nmbrs.base_url}documents/{task_id}", timeout=self.nmbrs.timeout)

        return BytesIO(resp.content)


