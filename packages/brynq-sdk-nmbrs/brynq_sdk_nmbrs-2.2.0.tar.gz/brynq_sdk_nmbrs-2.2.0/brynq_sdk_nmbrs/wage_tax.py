from typing import Any, Dict, List, Union, Tuple
import pandas as pd
from .schemas.wage_tax import WageTaxGet, WageTaxUpdate
from zeep.exceptions import Fault
from zeep.ns import WSDL, SOAP_ENV_11
from zeep.xsd import ComplexType, Element, String
from zeep.helpers import serialize_object
# import logging
from brynq_sdk_functions import Functions


class WageTax:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.soap_client_companies = nmbrs.soap_client_companies
        self.soap_client_employees = nmbrs.soap_client_employees

    def get_settings(self, year: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get salary tables for all companies for a specific period and year.

        Args:
            period (int): The period number
            year (int): The year

        Returns:
            pd.DataFrame: DataFrame containing the salary tables
        """
        wagetax_settings = pd.DataFrame()
        for company in self.nmbrs.soap_company_ids.to_dict(orient='records'):
            wagetax_settings_temp = self._get(company['i_d'], year)
            if not wagetax_settings_temp.empty:
                wagetax_settings_temp['companyId'] = company['number']
                wagetax_settings = pd.concat([wagetax_settings, wagetax_settings_temp])

        valid_wagetax_settings, invalid_wagetax_settings = Functions.validate_data(df=wagetax_settings, schema=WageTaxGet, debug=True)

        # No validation schema for now, but could be added later
        return valid_wagetax_settings, invalid_wagetax_settings

    def _get(self, company_id: int, year: int) -> pd.DataFrame:
        """
        Get salary tables for a specific company, period and year.

        Args:
            company_id (int): The ID of the company
            period (int): The period number
            year (int): The year

        Returns:
            pd.DataFrame: DataFrame containing the salary tables
        """
        try:
            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Make SOAP request with the proper header structure
            response = self.soap_client_companies.service.WageTax_GetList(
                CompanyId=company_id,
                intYear=year,
                _soapheaders=[auth_header]
            )

            # Convert response to DataFrame
            if response:
                # Convert Zeep objects to Python dictionaries
                serialized_response = serialize_object(response)

                # Convert to list if it's not already
                if not isinstance(serialized_response, list):
                    serialized_response = [serialized_response]

                # Convert to DataFrame
                df = pd.DataFrame(serialized_response)

                return df
            else:
                return pd.DataFrame()

        except Fault as e:
            raise Exception(f"SOAP request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get salary tables: {str(e)}")

    def update(self, data: Dict[str, Any]) -> pd.DataFrame:
        try:
            wage_tax_model = WageTaxUpdate(**data)

            if self.nmbrs.mock_mode:
                return wage_tax_model

            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Use the model's built-in SOAP conversion method
            wage_tax_settings = wage_tax_model.to_soap_settings(self.nmbrs.soap_client_employees)

            # Make SOAP request with clean, simple call
            response = self.nmbrs.soap_client_employees.service.WageTax_UpdateCurrent(
                EmployeeId=wage_tax_model.employee_id,
                LoonheffingSettings=wage_tax_settings,
                _soapheaders=[auth_header]
            )

            # Convert response to DataFrame
            if response:
                # Convert Zeep objects to Python dictionaries
                serialized_response = serialize_object(response)

                # Convert to list if it's not already
                if not isinstance(serialized_response, list):
                    serialized_response = [serialized_response]

                # Convert to DataFrame
                df = pd.DataFrame(serialized_response)

                return df
            else:
                return pd.DataFrame()

        except Fault as e:
            raise Exception(f"SOAP request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to update WageTax: {str(e)}")
