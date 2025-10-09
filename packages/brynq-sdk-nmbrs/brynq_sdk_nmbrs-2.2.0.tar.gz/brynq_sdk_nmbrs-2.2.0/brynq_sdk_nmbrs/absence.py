from typing import Any, Dict, List, Union, Tuple
import pandas as pd
from .schemas.absence import AbsenceCreate, AbsenceGet
from zeep.exceptions import Fault
from zeep.ns import WSDL, SOAP_ENV_11
from zeep.xsd import ComplexType, Element, String
from zeep.helpers import serialize_object
# import logging
from brynq_sdk_functions import Functions


class Absence:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.soap_client_companies = nmbrs.soap_client_companies
        self.soap_client_employees = nmbrs.soap_client_employees

    def get(self, employee_id: int = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get salary tables for all companies for a specific period and year.

        Args:
            period (int): The period number
            year (int): The year

        Returns:
            pd.DataFrame: DataFrame containing the salary tables
        """
        absences = pd.DataFrame()
        for company in self.nmbrs.soap_company_ids.to_dict(orient='records'):
            absences_temp = self._get(company['i_d'], employee_id=employee_id)
            if not absences_temp.empty:
                absences_temp['companyId'] = company['number']
                absences = pd.concat([absences, absences_temp])

        valid_absences, invalid_absences = Functions.validate_data(df=absences, schema=AbsenceGet, debug=True)

        # No validation schema for now, but could be added later
        return valid_absences, invalid_absences

    def _get(self, company_id: int, employee_id: int = None) -> pd.DataFrame:
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

            if employee_id is None:
                response = self.soap_client_employees.service.Absence_GetAll_AllEmployeesByCompany(
                    CompanyId=company_id,
                    _soapheaders=[auth_header]
                )
            else:
                # Make SOAP request with the proper header structure
                response = self.soap_client_employees.service.Absence_GetList(
                    EmployeeId=employee_id,
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

    def create(self, data: Dict[str, Any]) -> pd.DataFrame:
        try:
            absence_model = AbsenceCreate(**data)

            if self.nmbrs.mock_mode:
                return absence_model

            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Use the model's built-in SOAP conversion method
            absence_settings = absence_model.to_soap_settings(self.nmbrs.soap_client_employees)

            # Make SOAP request with clean, simple call
            response = self.nmbrs.soap_client_employees.service.Absence_Create(
                EmployeeId=absence_model.employee_id,
                Dossier=absence_model.new_dossier,
                Absence=absence_settings,
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
