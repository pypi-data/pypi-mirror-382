from typing import Optional
from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import (
    LgApiReturn,
)
from lg_payroll_api.helpers.base_client import BaseLgServiceClient, LgAuthentication


class LgApiWorkScaleClient(BaseLgServiceClient):
    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(lg_auth=lg_auth, wsdl_service="v2/ServicoDeEscala")

    def consult_list_on_demand(
        self,
        permission_filter: Optional[bool] = None,
        search_term: Optional[str] = None,
        only_actives: Optional[bool] = None,
        scale_code: Optional[str] = None,
        current_page: Optional[int] = 1,
    ) -> LgApiReturn:
        body = {
            "FiltroDeEscala": {
                "SomenteComPermissaoParaCadColaborador": permission_filter,
                "TermoDaBusca": search_term,
                "SomenteAtivos": only_actives,
                "CodigoDaEscala": scale_code,
                "PaginaAtual": current_page,
            }
        }

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaPorDemanda,
                    body=body,
                )
            )
        )
