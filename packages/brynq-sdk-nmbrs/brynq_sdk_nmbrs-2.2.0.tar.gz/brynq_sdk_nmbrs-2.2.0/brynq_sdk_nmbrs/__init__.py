import warnings
from typing import Union, List, Literal, Optional, get_args, get_origin
import re
import pandas as pd
from pydantic import BaseModel
import requests
from brynq_sdk_brynq import BrynQ
from .absence import Absence
from .wage_tax import WageTax
from .address import Address
from .bank import Bank
from zeep import Client, Settings
from .children import Children
from .companies import Companies
from .debtors import Debtors
from .contract import Contract
from .costcenter import EmployeeCostcenter, Costcenter
from .costunit import Costunit
from .department import EmployeeDepartment
from .document import Payslip
from .employees import Employees
from .salary_tables import SalaryTables, SalaryScales, SalarySteps
from .employment import Employment
from .function import EmployeeFunction
from .hours import VariableHours, FixedHours
from .days import VariableDays, FixedDays
from .manager import EmployeeManager, Manager
from .salaries import Salaries
from .schedules import Schedule
from .wagecomponents import EmployeeFixedWageComponents, EmployeeVariableWageComponents
import os


class Nmbrs(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False, mock_mode: bool = True):
        """
        Initialize the Nmbrs class.

        Args:
            label: The label of the system in BrynQ. legacy
            debug: Whether to print debug information
11            mock_mode: If true, data will NOT be sent to Nmbrs but only be tested for validity against Pydantic schemas
        """
        self.mock_mode = mock_mode
        self.debug = debug
        self.timeout = 3600
        self.system_type = system_type
        if mock_mode is False:
            super().__init__()
            self.data_interface_id = os.getenv("DATA_INTERFACE_ID")
            headers = self._get_request_headers()
            self.base_url = "https://api.nmbrsapp.com/api/"
            self.session = requests.Session()
            self.session.headers.update(headers)

            # Initialize SOAP client
            self.soap_settings = Settings(
                strict=False,
                xml_huge_tree=True,
                force_https=True
            )
            self.soap_client_companies = Client(
                'https://api.nmbrs.nl/soap/v3/CompanyService.asmx?wsdl',
                settings=self.soap_settings
            )
            self.soap_client_employees = Client(
                'https://api.nmbrs.nl/soap/v3/EmployeeService.asmx?wsdl',
                settings=self.soap_settings
            )

        self.address = Address(self)
        self.bank = Bank(self)
        self.children = Children(self)
        self.debtor = Debtors(self)
        self.companies = Companies(self)
        self.contract = Contract(self)
        self.department = EmployeeDepartment(self)
        debtors, _ = self.debtor.get()
        self.debtor_ids = debtors['debtor_id'].to_list()
        self.company_ids = self.companies.get()['companyId'].to_list()
        self.soap_company_ids = self.companies.get_soap_ids()
        self.employees = Employees(self)
        self.employment = Employment(self)
        self.function = EmployeeFunction(self)
        self.fixed_hours = FixedHours(self)
        self.fixed_days = FixedDays(self)
        self.variable_hours = VariableHours(self)
        self.variable_days = VariableDays(self)
        self.manager = Manager(self)
        self.employee_manager = EmployeeManager(self)
        self.salaries = Salaries(self)
        self.schedule = Schedule(self)
        self.fixed_wagecomponents = EmployeeFixedWageComponents(self)
        self.variable_wagecomponents = EmployeeVariableWageComponents(self)
        self.children = Children(self)
        self.salary_tables = SalaryTables(self)
        self.salary_scales = SalaryScales(self)
        self.salary_steps = SalarySteps(self)
        self.wage_tax = WageTax(self)
        self.absence = Absence(self)
        self.current_period = self.companies.get_current_period()

    def _get_request_headers(self):
        credentials = self.interfaces.credentials.get(system='nmbrs', system_type=self.system_type)
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {credentials.get('data').get('access_token')}",
            # partner identifier
            "X-Subscription-Key": credentials.get("custom_data").get("subscription_key")
        }

        return headers

    def _get_soap_auth_header(self):
        """
        Creates the SOAP authentication header using credentials from initial_credentials.

        Returns:
            AuthHeaderWithDomainType: The authentication header for SOAP requests
        """
        initial_credentials = self.get_system_credential(system='nmbrs', label='bob')
        config = initial_credentials.get("config", {})

        # Get the AuthHeaderWithDomain type from the WSDL
        AuthHeaderWithDomainType = self.soap_client_companies.get_element('ns0:AuthHeaderWithDomain')

        # Create the auth header using credentials from config
        auth_header = AuthHeaderWithDomainType(
            Username=config.get("soap_api_username"),
            Token=config.get("soap_api_token"),
            Domain=config.get("soap_api_domain")
        )

        return auth_header

    def get_paginated_result(self, request: requests.Request) -> List:
        has_next_page = True
        result_data = []
        while has_next_page:
            prepped = request.prepare()
            prepped.headers.update(self.session.headers)
            resp = self.session.send(prepped, timeout=self.timeout)
            resp.raise_for_status()
            response_data = resp.json()
            result_data += response_data['data']
            next_page_url = response_data.get('pagination').get('nextPage')
            has_next_page = next_page_url is not None
            request.url = next_page_url

        return result_data

    def check_fields(self, data: Union[dict, List], required_fields: List, allowed_fields: List):
        if isinstance(data, dict):
            data = data.keys()

        if self.debug:
            print(f"Required fields: {required_fields}")
            print(f"Allowed fields: {allowed_fields}")
            print(f"Data: {data}")

        for field in data:
            if field not in allowed_fields and field not in required_fields:
                warnings.warn('Field {field} is not implemented. Optional fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields)))

        for field in required_fields:
            if field not in data:
                raise ValueError('Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

    def _rename_camel_columns_to_snake_case(self, df: pd.DataFrame) -> pd.DataFrame:
        def camel_to_snake_case(column):
            # Replace periods with underscores
            column = column.replace('.', '_')
            # Insert underscores before capital letters and convert to lowercase
            return re.sub(r'(?<!^)(?=[A-Z])', '_', column).lower()

        df.columns = map(camel_to_snake_case, df.columns)

        return df

    def flat_dict_to_nested_dict(self, flat_dict: dict, model: BaseModel) -> dict:
        nested = {}
        for name, field in model.model_fields.items():
            key_in_input = name  # Original model field name as key in flat_dict
            alias = field.alias or name
            if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
                nested[alias] = self.flat_dict_to_nested_dict(flat_dict, field.annotation)
            elif any(isinstance(item, type) and issubclass(item, BaseModel) for item in get_args(field.annotation)):
                # get the basemodel class from the list
                nested_model_name = [item for item in get_args(field.annotation) if isinstance(item, type) and issubclass(item, BaseModel)][0]
                origin = get_origin(field.annotation)
                if origin in (list, List):
                    nested[alias] = [self.flat_dict_to_nested_dict(flat_dict, nested_model_name)]
                else:
                    nested[alias] = self.flat_dict_to_nested_dict(flat_dict, nested_model_name)
            else:
                if key_in_input in flat_dict:
                    nested[alias] = flat_dict[key_in_input]
        return nested
