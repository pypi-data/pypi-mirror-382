from datetime import date
from typing import Literal

from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import (
    LgApiExecutionReturn,
    LgApiPaginationReturn,
    LgApiReturn,
)
from lg_payroll_api.helpers.base_client import BaseLgServiceClient, LgAuthentication
from lg_payroll_api.utils.enums import (
    SITUATIONS,
    EnumCampoDeBuscaDoContratoDeTrabalho,
    EnumTipoDeDadosModificados,
    EnumTipoDeOperacaoContratoLog,
)
from lg_payroll_api.utils.lg_exceptions import LgParameterListLimitException


class LgApiEmploymentContract(BaseLgServiceClient):
    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(lg_auth=lg_auth, wsdl_service="v2/ServicoDeContratoDeTrabalho")

    def consult(self, contract_code: str, company_code: int) -> LgApiReturn:
        body = {
            "Colaborador": {
                "Matricula": contract_code,
                "Empresa": {"Codigo": company_code},
            }
        }

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.Consultar,
                    body=body,
                )
            )
        )

    def consult_work_shift(self, contract_code: str, company_code: int) -> LgApiReturn:
        body = {
            "Colaborador": {
                "Matricula": contract_code,
                "Empresa": {"Codigo": company_code},
            }
        }

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarEscala,
                    body=body,
                )
            )
        )

    def consult_list(
        self,
        company_code: int,
        search_field: EnumCampoDeBuscaDoContratoDeTrabalho = None,
        search_value: str = None,
        employee_type: Literal["Funcionário", "Autônomo"] = None,
    ) -> LgApiReturn:
        if (
            search_field == None
            and not search_value == None
            or search_value == None
            and not search_field == None
        ):
            raise ValueError(
                "If search field is defined, you need to define a search value or vice versa."
            )

        body = {
            "Empresa": {"FiltroComCodigoNumerico": {"Codigo": company_code}},
            "CampoDeBusca": search_field,
            "TipoDoColaborador": employee_type,
            "TermoDeBusca": search_value,
        }
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarLista,
                    body=body,
                )
            )
        )

    def consult_list_by_company(
        self,
        company_code: int,
        contracts_codes: list[str],
    ) -> LgApiReturn:

        if len(contracts_codes) > 50:
            raise LgParameterListLimitException(
                "Person ids list has exceeded the limit of 50 items."
            )

        body = {
            "CodigoDaEmpresa": company_code,
            "ListaDeMatriculas": {"string": contracts_codes},
        }
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaPorEmpresa,
                    body=body,
                )
            )
        )

    def list_on_demand(
        self,
        companies: list[int] = None,
        offices: list[tuple[int, int]] = None,
        employee_status: list[SITUATIONS] = None,
        current_page: int = None,
    ) -> LgApiPaginationReturn:
        body = {
            "Empresas": [
                {"FiltroComCodigoNumerico": {"Codigo": company}}
                for company in companies
            ]
            if companies
            else None,
            "Estabelecimentos": [
                {
                    "FiltroComCodigoNumericoEEmpresa": {
                        "Codigo": office[0],
                        "Empresa": {"Codigo": office[1]},
                    }
                }
                for office in offices
            ]
            if offices
            else None,
            "TiposDeSituacoes": [{"int": situation} for situation in employee_status]
            if employee_status
            else None,
            "PaginaAtual": current_page,
        }
        return LgApiPaginationReturn(
            auth=self.lg_client,
            wsdl_service=self.wsdl_client,
            service_client=self.wsdl_client.service.ConsultarListaPorDemanda,
            body=body,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaPorDemanda,
                    body=body,
                )
            )
        )

    def consult_manager_list(
        self,
        employee_code: str,
        employee_company_id: int,
        situations_types: list[SITUATIONS] = None,
    ) -> LgApiReturn:
        body = {
            "TiposDeSituacoes": situations_types,
            "Colaborador": {
                "Matricula": employee_code,
                "Empresa": {"Codigo": employee_company_id},
            },
        }
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaDeGestorImediato,
                    body=body,
                )
            )
        )

    def list_changed_contracts(
        self,
        company_code: int,
        start_date: date,
        end_date: date,
        operations_types: list[EnumTipoDeOperacaoContratoLog] = [
            EnumTipoDeOperacaoContratoLog.INCLUSAO.value,
            EnumTipoDeOperacaoContratoLog.ALTERACAO.value,
            EnumTipoDeOperacaoContratoLog.EXCLUSAO.value,
        ],
        situation_type: list[SITUATIONS] = None,
        modified_data_type: EnumTipoDeDadosModificados = EnumTipoDeDadosModificados.CONTRATUAIS_E_PESSOAIS.value,
        enrollments: list[str] = None,
    ) -> LgApiReturn:
        body = {
            "filtro": {
                "TiposDeSituacao": situation_type,
                "TipoDeDadosModificados": modified_data_type,
                "TiposDeOperacoes": [
                    {"TipoDeOperacao": {"Valor": operation}}
                    for operation in operations_types
                ],
                "CodigoDaEmpresa": company_code,
                "ListaDeMatriculas": enrollments,
                "PeriodoDeBusca": {
                    "DataInicio": start_date.strftime("%Y-%m-%d"),
                    "DataFim": end_date.strftime("%Y-%m-%d"),
                },
            }
        }
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaDeModificados,
                    body=body,
                    parse_body_on_request=True,
                )
            )
        )

    def insert_manager(
        self,
        employee_code: str,
        employee_company_id: int,
        manager_code: str,
        manager_company_id: int,
        start_date: date = None,
        end_date: date = None,
    ) -> LgApiExecutionReturn:
        body = {
            "ListaDeAssociacaoContratoGestor": {
                "FiltroDeAssociacaoContratoGestor": {
                    "Contrato": {
                        "Matricula": employee_code,
                        "Empresa": {
                            "Codigo": employee_company_id,
                        },
                    },
                    "Gestores": {
                        "FiltroComIdentificacaoDeContratoV2": {
                            "Matricula": manager_code,
                            "Empresa": {"Codigo": manager_company_id},
                        }
                    },
                }
            },
            "Periodo": {
                "DataInicio": start_date.strftime("%Y-%m-%d") if start_date else None,
                "DataFim": end_date.strftime("%Y-%m-%d") if end_date else None,
            },
        }
        return LgApiExecutionReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.InserirGestoresNaFicha,
                    body=body,
                )
            )
        )

    def delete_manager(
        self,
        employee_code,
        employee_company_id,
        manager_code,
        manager_company_id,
        start_date=None,
        end_date=None,
    ) -> LgApiExecutionReturn:
        body = {
            "ListaDeAssociacaoContratoGestor": {
                "FiltroDeAssociacaoContratoGestor": {
                    "Contrato": {
                        "Matricula": employee_code,
                        "Empresa": {"Codigo": employee_company_id},
                    },
                    "Gestores": {
                        "FiltroComIdentificacaoDeContratoV2": {
                            "Matricula": manager_code,
                            "Empresa": {"Codigo": manager_company_id},
                        }
                    },
                }
            },
            "Periodo": {
                "DataInicio": start_date if start_date else None,
                "DataFim": end_date if end_date else None,
            },
        }
        return LgApiExecutionReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ExcluirGestoresNaFicha,
                    body=body,
                )
            )
        )
