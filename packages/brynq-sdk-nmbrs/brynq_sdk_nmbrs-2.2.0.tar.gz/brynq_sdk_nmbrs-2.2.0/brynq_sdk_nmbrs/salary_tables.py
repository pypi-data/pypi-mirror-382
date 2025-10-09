from typing import Dict, List, Union, Tuple
import pandas as pd
from zeep.exceptions import Fault
from zeep.ns import WSDL, SOAP_ENV_11
from zeep.xsd import ComplexType, Element, String
from zeep.helpers import serialize_object
# import logging
from brynq_sdk_functions import Functions
from .schemas.salary import SalaryTableGet, SalaryScalesGet, SalaryStepsGet


class SalaryTables:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.soap_client_companies = nmbrs.soap_client_companies

    def get(self, period: int, year: int) -> (pd.DataFrame, pd.DataFrame):
        """
        Get salary tables for all companies for a specific period and year.

        Args:
            period (int): The period number
            year (int): The year

        Returns:
            pd.DataFrame: DataFrame containing the salary tables
        """
        salary_tables = pd.DataFrame()
        for company in self.nmbrs.soap_company_ids.to_dict(orient='records'):
            salary_table_temp = self._get(company['i_d'], period, year)
            if not salary_table_temp.empty:
                salary_table_temp['companyId'] = company['number']
                salary_tables = pd.concat([salary_tables, salary_table_temp])

        valid_salary_tables, invalid_salary_tables = Functions.validate_data(df=salary_tables, schema=SalaryTableGet, debug=True)

        # No validation schema for now, but could be added later
        return valid_salary_tables, invalid_salary_tables

    def _get(self, company_id: int, period: int, year: int) -> pd.DataFrame:
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
            response = self.soap_client_companies.service.SalaryTable2_Get(
                CompanyId=company_id,
                Period=period,
                Year=year,
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


class SalaryScales:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.soap_client_companies = nmbrs.soap_client_companies

    def get(self, period: int, year: int) -> (pd.DataFrame, pd.DataFrame):
        """
        Get salary scales for all companies for a specific period and year.

        Args:
            period (int): The period number
            year (int): The year

        Returns:
            pd.DataFrame: DataFrame containing the salary scales
        """
        salary_scales = pd.DataFrame()
        for company in self.nmbrs.soap_company_ids.to_dict(orient='records'):
            salary_scale_temp = self._get(company['i_d'], period, year)
            if not salary_scale_temp.empty:
                salary_scale_temp['companyId'] = company['number']
                salary_scales = pd.concat([salary_scales, salary_scale_temp])

        valid_salary_scales, invalid_salary_scales = Functions.validate_data(df=salary_scales, schema=SalaryScalesGet, debug=True)

        return valid_salary_scales, invalid_salary_scales

    def _get(self, company_id: int, period: int, year: int) -> pd.DataFrame:
        """
        Get salary scales for a specific company, period and year.

        Args:
            company_id (int): The ID of the company
            period (int): The period number
            year (int): The year

        Returns:
            pd.DataFrame: DataFrame containing the salary scales
        """
        try:
            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Make SOAP request with the proper header structure
            response = self.soap_client_companies.service.SalaryTable2_GetScales(
                CompanyId=company_id,
                Period=period,
                Year=year,
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
            raise Exception(f"Failed to get salary scales: {str(e)}")


class SalarySteps:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.soap_client_companies = nmbrs.soap_client_companies

    def get(self, period: int, year: int, scale: dict) -> (pd.DataFrame, pd.DataFrame):
        """
        Get salary steps for all companies for a specific period, year and scale.

        Args:
            period (int): The period number
            year (int): The year
            scale (dict): Dictionary containing scale information with keys:
                - scale (str): The scale identifier (e.g., "Swapper")
                - schaal_description (str): Description of the scale
                - scale_value (float): The scale value
                - scale_percentage_max (float): Maximum percentage
                - scale_percentage_min (float): Minimum percentage

        Returns:
            pd.DataFrame: DataFrame containing the salary steps
        """
        salary_steps = pd.DataFrame()
        for company in self.nmbrs.soap_company_ids.to_dict(orient='records'):
            salary_steps_temp = self._get(company['i_d'], period, year, scale)
            if not salary_steps_temp.empty:
                salary_steps_temp['companyId'] = company['number']
                salary_steps = pd.concat([salary_steps, salary_steps_temp])

        valid_salary_steps, invalid_salary_steps = Functions.validate_data(df=salary_steps, schema=SalaryStepsGet, debug=True)

        return valid_salary_steps, invalid_salary_steps

    def _get(self, company_id: int, period: int, year: int, scale: dict) -> pd.DataFrame:
        """
        Get salary steps for a specific company, period, year and scale.

        Args:
            company_id (int): The ID of the company
            period (int): The period number
            year (int): The year
            scale (dict): Dictionary containing scale information with keys:
                - scale (str): The scale identifier (e.g., "Swapper")
                - schaal_description (str): Description of the scale
                - scale_value (float): The scale value
                - scale_percentage_max (float): Maximum percentage
                - scale_percentage_min (float): Minimum percentage

        Returns:
            pd.DataFrame: DataFrame containing the salary steps
        """
        try:
            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Make SOAP request with the proper header structure
            response = self.soap_client_companies.service.SalaryTable2_GetSteps(
                CompanyId=company_id,
                Period=period,
                Year=year,
                Scale={
                    'Scale': scale.get('scale', ''),
                    'SchaalDescription': scale.get('schaal_description', ''),
                    'ScaleValue': scale.get('scale_value', 0),
                    'ScalePercentageMax': scale.get('scale_percentage_max', 0),
                    'ScalePercentageMin': scale.get('scale_percentage_min', 0)
                },
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
            # logger.exception(f"SOAP Fault: {str(e)}")
            raise Exception(f"SOAP request failed: {str(e)}")
        except Exception as e:
            # logger.exception("Exception in SalarySteps.get:")
            raise Exception(f"Failed to get salary steps: {str(e)}")
