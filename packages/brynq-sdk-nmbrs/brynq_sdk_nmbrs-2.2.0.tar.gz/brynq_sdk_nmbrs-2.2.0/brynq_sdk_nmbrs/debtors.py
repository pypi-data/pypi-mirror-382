import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .department import Departments
from .function import Functions as NmbrsFunctions
from .schemas.debtor import DebtorsGet


class Debtors:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.departments = Departments(nmbrs)
        self.functions = NmbrsFunctions(nmbrs)


    def get(self) -> (pd.DataFrame, pd.DataFrame):
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}debtors")
        data = self.nmbrs.get_paginated_result(request)

        df = pd.DataFrame(data)

        valid_debtors, invalid_debtors = Functions.validate_data(df=df, schema=DebtorsGet, debug=True)

        return valid_debtors, invalid_debtors
