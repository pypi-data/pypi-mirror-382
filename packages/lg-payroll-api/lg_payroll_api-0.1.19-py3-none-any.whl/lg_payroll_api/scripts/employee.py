from typing import Union
from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import (
    LgApiPaginationReturn,
    LgApiReturn,
    LgApiExecReturn
)
from lg_payroll_api.helpers.base_client import (
    BaseLgServiceClient,
    LgAuthentication
)
from lg_payroll_api.utils.enums import EnumCampoContato
from lg_payroll_api.utils.enums import SITUATIONS
from lg_payroll_api.utils.lg_exceptions import LgParameterListLimitException
from datetime import date


class LgApiEmployee(BaseLgServiceClient):
    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(lg_auth=lg_auth, wsdl_service="v2/ServicoDeColaborador")

    def additional_information_list(
        self, contract_code: str, company_code: int
    ) -> LgApiReturn:
        body = {
            "Colaborador": {
                "Matricula": contract_code,
                "Empresa": {"Codigo": company_code},
            }
        }

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaValorDaInformacaoAdicionalDaPessoa,
                    body=body,
                )
            )
        )

    def consult(self, person_id: str) -> LgApiReturn:
        body = {"PessoaId": person_id}
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.Consultar, body=body
                )
            )
        )

    def documents_with_identification(
        self,
        company_code: int,
        contracts_codes: list[str] = None,
        situations: list[SITUATIONS] = None,
        page: int = None,
    ) -> LgApiPaginationReturn:
        body = {
            "CodigoDaEmpresa": company_code,
            "ListaDeMatriculas": [{"string": contract} for contract in contracts_codes]
            if contracts_codes
            else None,
            "TiposDeSituacoes": [{"int": situation} for situation in situations]
            if situations
            else None,
            "PaginaAtual": page,
        }
        return LgApiPaginationReturn(
            auth=self.lg_client,
            wsdl_service=self.wsdl_client,
            service_client=self.wsdl_client.service.ConsultarDocumentosComIdentificacao,
            body=body,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarDocumentosComIdentificacao,
                    body=body,
                )
            )
        )

    def consult_list(self, person_ids: list[str]) -> LgApiReturn:
        if len(person_ids) > 50:
            raise LgParameterListLimitException(
                "Person ids list has exceeded the limit of 50 items."
            )

        body = {"filtro": {"ListaDePessoaId": {"string": person_ids}}}

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarLista,
                    body=body,
                    parse_body_on_request=True,
                )
            )
        )

    def consult_summary_list(self, person_ids: list[str]) -> LgApiReturn:
        if len(person_ids) > 50:
            raise LgParameterListLimitException(
                "Person ids list has exceeded the limit of 50 items."
            )

        body = {"ListaDePessoaId": [{"string": person_id} for person_id in person_ids]}

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaResumida,
                    body=body,
                )
            )
        )

    def update_contact(
        self,
        contract_code: str,
        company_code: int,
        fields_of_contract: list[tuple[EnumCampoContato, str]],
        historic_date: Union[date, None] = None
    ) -> LgApiExecReturn:
        """Change contact fields in employee contract

        Args:
            contract_code (str, mandatory): Enrollment code of the contract
            company_code (int, mandatory): Company code
            fields_of_contract (list[tuple[int, str]], mandatory): List of tuples containing (EnumCampoContato, "new value")
            historic_date (date, Optional): Date of historic. If None, the current historic will be considered

        Examples:
            ```python
            # Import LG Client
            from lg_payroll_api import LgPayrollApi

            # Import the enum of contact fields
            from lg_payroll_api.utils.enums import EnumCampoContato


            lg_client = LgPayrollApi(auth)

            # Set contact fields to change
            fields_to_change = [
                (EnumCampoContato.EMAIL_CORPORATIVO, "email@domain.com"),
                (EnumCampoContato.CELULAR, "911111111")
            ]

            # Send request to LG system
            lg_client.employee_service.update_contact(
                contract_code="1",
                company_code=1,
                fields_of_contract=fields_to_change
            )
            ```
        """
        def contact_fields() -> list[dict]:
            return [
                {
                    "CampoDoContato": {
                        "CampoContato": int(field),
                        "Valor": value
                    }
                } for field, value in fields_of_contract
            ]

        body = {
            "Colaborador": {
                "Matricula": contract_code,
                "Empresa": {
                    "Codigo": company_code
                }
            },
            "DataDoHistorico": (
                historic_date.strftime("%Y-%m-%d")
                if historic_date else None
            ),
            "CamposDoContato": contact_fields()
        }

        return LgApiExecReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.AtualizarContato,
                    body=body,
                )
            )
        )
