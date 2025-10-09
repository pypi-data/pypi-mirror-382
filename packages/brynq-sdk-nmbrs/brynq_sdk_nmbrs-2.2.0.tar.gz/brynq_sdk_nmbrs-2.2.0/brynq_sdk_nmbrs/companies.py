import pandas as pd
import requests
import logging

from .leave import LeaveGroup
from .costcenter import Costcenter
from .costunit import Costunit
from .hours import Hours
from .bank import Bank
from .function import Functions
from zeep.exceptions import Fault
from zeep.helpers import serialize_object


class Companies:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.costcenters = Costcenter(nmbrs)
        self.costunits = Costunit(nmbrs)
        self.hours = Hours(nmbrs)
        self.banks = Bank(nmbrs)
        self.soap_client_companies = nmbrs.soap_client_companies
        self.logger = logging.getLogger(__name__)
        self.leave_groups = LeaveGroup(nmbrs)

    def get(self) -> pd.DataFrame:
        try:
            request = requests.Request(method='GET',
                                    url=f"{self.nmbrs.base_url}companies")
            data = self.nmbrs.get_paginated_result(request)
            df = pd.DataFrame(data)
        except requests.HTTPError as e:
            if e.response.status_code == 403 and e.response.json().get("title") == "ForbiddenMultiDebtor.":
                df = pd.DataFrame()
                for debtor_id in self.nmbrs.debtor_ids:
                    request = requests.Request(method='GET',
                                        url=f"{self.nmbrs.base_url}debtors/{debtor_id}/companies")
                    data = self.nmbrs.get_paginated_result(request)
                    df = pd.concat([df, pd.DataFrame(data)])
            else:
                raise e
        # TODO: add validation

        return df

    def get_soap_ids(self) -> pd.DataFrame:
        """
        Get all companies using the SOAP API.

        Returns:
            pd.DataFrame: DataFrame containing all companies
        """
        try:
            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Make SOAP request with the proper header structure
            response = self.soap_client_companies.service.List_GetAll(
                _soapheaders=[auth_header]
            )

            # Convert response to DataFrame
            if response:
                # Convert Zeep objects to Python dictionaries
                serialized_response = serialize_object(response)

                # TODO: add validation here
                # Convert to DataFrame
                df = pd.DataFrame(serialized_response)
                df = self.nmbrs._rename_camel_columns_to_snake_case(df)

                return df
            else:
                return pd.DataFrame()

        except Fault as e:
            raise Exception(f"SOAP request failed: {str(e)}")
        except Exception as e:
            self.logger.exception("Exception occurred:")
            raise Exception(f"Failed to get companies: {str(e)}")

    def get_current_period(self) -> int:
        try:
            df = pd.DataFrame()
            for company_id in self.nmbrs.company_ids:
                request = requests.Request(method='GET',
                                    url=f"{self.nmbrs.base_url}companies/{company_id}/period")
                data = self.nmbrs.get_paginated_result(request)
                df_temp = pd.json_normalize(data)
                df_temp['company_id'] = company_id
                df = pd.concat([df, df_temp])

            return df
        except Exception as e:
            self.logger.exception("Exception occurred:")
            raise Exception(f"Failed to get current period: {str(e)}")
