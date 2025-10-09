from datetime import datetime

from zeep import Client
from zeep.transports import Transport
import requests
import pandas as pd


class Children:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.client = Client(wsdl='https://api.nmbrs.nl/soap/v3/EmployeeService.asmx?wsdl') #, transport=Transport(session=self.nmbrs.session))
        # self.client.set_default_soapheaders([auth_header])
        AuthHeaderWithDomainType = self.client.get_element('ns0:AuthHeaderWithDomain')

        auth_header = AuthHeaderWithDomainType(
            Username="erwin.vink@brynq.com",
            Token="cc358715f5c14cda8add964deef99ba3",
            Domain="extdev-brynq"
        )
        self.client.set_default_soapheaders([auth_header])

    def get(self,
            company_id: str,
            created_from: str = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        try:
            request = requests.Request(method='GET',
                                       url=f"{self.nmbrs.base_url}companies/{company_id}/employees/functions",
                                       params=params)

            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='functions',
                meta=['employeeId']
            )
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df


    def create(self,
               employee_id: str,
               data: dict):

        required_fields = ["first_name", "period", "function_id"]
        allowed_fields = {}
        # self.nmbrs.check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        ChildType = self.client.get_type('ns0:Child')
        child = ChildType(
            Id=1,  # Use 0 or omit if adding a new child
            Name='Doe',
            FirstName='John',
            Initials='J.D.',
            Gender='male',  # Options: 'male', 'female', 'unknown', 'undefined'
            Birthday=datetime(2020, 1, 1)  # Using a datetime object
        )

        # Make the API call
        result = self.client.service.Children_Insert(
            EmployeeId=employee_id,
            child=child
        )
        print("Child inserted successfully. Result:", result)


# <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:emp="https://api.nmbrs.nl/soap/v3/EmployeeService">
#    <soap:Header>
#       <emp:AuthHeaderWithDomain>
#          <!--Optional:-->
#          <emp:Username>erwin.vink@brynq.com</emp:Username>
#          <!--Optional:-->
#          <emp:Token>cc358715f5c14cda8add964deef99ba3</emp:Token>
#          <!--Optional:-->
#          <emp:Domain>extdev-brynq</emp:Domain>
#       </emp:AuthHeaderWithDomain>
#    </soap:Header>
#    <soap:Body>
#       <emp:Children_Insert>
#          <emp:EmployeeId>11</emp:EmployeeId>
#          <!--Optional:-->
#          <emp:child>
#             <emp:Id>1</emp:Id>
#             <!--Optional:-->
#             <emp:Name>Doe</emp:Name>
#             <!--Optional:-->
#             <emp:FirstName>John</emp:FirstName>
#             <!--Optional:-->
#             <emp:Initials>J.</emp:Initials>
#             <emp:Gender>male</emp:Gender>
#             <emp:Birthday>2020-01-01T00:00:00</emp:Birthday>
#          </emp:child>
#       </emp:Children_Insert>
#    </soap:Body>
# </soap:Envelope>