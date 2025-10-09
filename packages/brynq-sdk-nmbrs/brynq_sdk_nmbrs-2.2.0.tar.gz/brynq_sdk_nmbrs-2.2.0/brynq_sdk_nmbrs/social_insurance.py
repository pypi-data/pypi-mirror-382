from typing import Any, Dict, List, Union, Tuple
import pandas as pd

from .schemas.social_insurance import SocialInsuranceUpdate
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
# import logging
from brynq_sdk_functions import Functions


class SocialInsurance:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.soap_client_employees = nmbrs.soap_client_employees

    def update(self, data: Dict[str, Any]) -> pd.DataFrame:
        try:
            social_insurance_model = SocialInsuranceUpdate(**data)

            if self.nmbrs.mock_mode:
                return social_insurance_model

            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Use the model's built-in SOAP conversion method
            social_insurance_settings = social_insurance_model.to_soap_settings(self.nmbrs.soap_client_employees)

            # Make SOAP request with clean, simple call
            response = self.nmbrs.soap_client_employees.service.SVW_UpdateCurrent(
                EmployeeId=social_insurance_model.employee_id,
                SVWSettings=social_insurance_settings,
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
            raise Exception(f"Failed to update Social Insurance: {str(e)}")
