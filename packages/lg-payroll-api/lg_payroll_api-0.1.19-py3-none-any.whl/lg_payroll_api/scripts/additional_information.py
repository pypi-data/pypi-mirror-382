from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import LgApiPaginationReturn, LgApiReturn, LgApiExecutionReturn
from lg_payroll_api.helpers.base_client import BaseLgServiceClient, LgAuthentication
from lg_payroll_api.utils.enums import (
    EnumTipoEntidadeInformacaoAdicional,
    EnumTipoDeInformacaoAdicional
)


class LgApiAdditionalInformationClient(BaseLgServiceClient):
    """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

    Default class to connect with the additional information endpoints
    """
    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(
            lg_auth=lg_auth, wsdl_service="v1/ServicoDeInformacaoAdicional"
        )

    def consult_list_on_demand(
        self,
        concept_code: EnumTipoEntidadeInformacaoAdicional,
        group_code: int = None,
        type: EnumTipoDeInformacaoAdicional = None,
    ) -> LgApiPaginationReturn:
        """Consult list of additional information fields on demand
        """
        if isinstance(concept_code, EnumTipoEntidadeInformacaoAdicional):
            concept_code = concept_code.value

        if isinstance(type, EnumTipoDeInformacaoAdicional):
            type = type.value

        params = {
            
            "ConceitoDaInformacaoAdicional": concept_code,
            "CodigoDoGrupo": group_code,
            "Tipo": type,
        }

        return LgApiPaginationReturn(
            auth=self.lg_client,
            wsdl_service=self.wsdl_client,
            service_client=self.wsdl_client.service.ConsultarListaPorDemanda,
            body=params,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaPorDemanda,
                    body=params,
                )
            )
        )
