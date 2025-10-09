from typing import Literal

from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import (
    LgApiPaginationReturn
)
from lg_payroll_api.helpers.base_client import (
    BaseLgServiceClient,
    LgAuthentication
)


class LgApiRoleClient(BaseLgServiceClient):
    """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

    Default class to connect with the role endpoints, service "v2/ServicoDeCargo"
    """

    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(lg_auth=lg_auth, wsdl_service="v2/ServicoDeCargo")

    def consult_list_by_demand(
        self,
        get_aditional_information: Literal[0, 1] = None,
        get_qualifications: Literal[0, 1] = None,
        code: str = None,
        company_code: int = None,
        only_with_perm_to_reg_emp: Literal[0, 1] = None,
        only_actives: Literal[0, 1] = None,

    ) -> LgApiPaginationReturn:
        """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

        Endpoint to retrieve role on LG System

        Return

        A List of OrderedDict that represents an Object(RetornoDeConsultaListaPorDemanda<CargoCompletoV2>) API response
            [
                Tipo : int
                Mensagens : [string]
                CodigoDoErro : string
                Cargo : Object(Cargo)
            ]
        """

        params = {"filtro": {
            "FiltroPorDemanda": {
                "TermoDaBusca": code,
                "Empresa": {"Codigo": company_code},
                "SomenteComPermissaoParaCadastrarColaborador": only_with_perm_to_reg_emp,
                "SomenteAtivos": only_actives,
            },
            "EhParaConsultarInformacaoAdicional": get_aditional_information,
            "EhParaConsultarHabilitacoes": get_qualifications
        }}

        return LgApiPaginationReturn(
            auth=self.lg_client,
            wsdl_service=self.wsdl_client,
            service_client=self.wsdl_client.service.ConsultarListaCargoCompletoPorDemanda,
            body=params,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaCargoCompletoPorDemanda,
                    body=params,
                    parse_body_on_request=True
                )
            )
        )
