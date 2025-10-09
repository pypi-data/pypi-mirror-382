from typing import Union
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zeep import Client, Transport
from zeep.plugins import HistoryPlugin
from lg_payroll_api.utils.settings import LG_API_DTO
from lg_payroll_api.helpers.authentication import LgAuthentication
from lg_payroll_api.helpers.envelope_logger import EnvelopeLogger
from lg_payroll_api.utils.aux_functions import clean_none_values_dict

class BaseLgServiceClient:
    """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

    Default class to send requests to LG Soap API services
    """

    def __init__(
        self,
        lg_auth: LgAuthentication,
        wsdl_service: Union[str, Client],
    ):
        super().__init__()
        self.envelope_logger = EnvelopeLogger(HistoryPlugin())
        self.lg_client = lg_auth
        self.lg_dto = LG_API_DTO
        if isinstance(wsdl_service, Client):
            self.wsdl_client: Client = wsdl_service

        elif isinstance(wsdl_service, str):
            session = Session()
            adapter = HTTPAdapter(
                pool_connections=20,
                pool_maxsize=20,   
                max_retries=Retry(
                    total=5,           
                    backoff_factor=0.5,
                    status_forcelist=[502, 503, 504],
                )
            )
            session.mount("https://", adapter)
            self.wsdl_client: Client = Client(
                wsdl=f"{self.lg_client.base_url}/{wsdl_service}?wsdl",
                plugins=[self.envelope_logger.requests_history],
                transport=Transport(session=session),
            )

        else:
            raise ValueError("Wsdl must be zeep Client or String.")

    def send_request(
        self,
        service_client: Client,
        body: dict,
        parse_body_on_request: bool = False,
        send_none_values: bool = False,
        show_envelope=True
    ):
        if not send_none_values:
            body = clean_none_values_dict(body)

        if parse_body_on_request:
            response = service_client(**body, _soapheaders=self.lg_client.auth_header)

        else:
            response = service_client(body, _soapheaders=self.lg_client.auth_header)
        if show_envelope:
            self.envelope_logger.log_envelope("request")
        return response
