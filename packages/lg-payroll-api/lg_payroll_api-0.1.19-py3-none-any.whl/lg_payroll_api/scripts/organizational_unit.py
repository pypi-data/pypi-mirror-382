from datetime import date
from typing import Literal

from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import LgApiPaginationReturn, LgApiReturn, LgApiExecReturn
from lg_payroll_api.helpers.base_client import BaseLgServiceClient, LgAuthentication
from lg_payroll_api.utils.enums import (
    EnumTipoDeDadosModificadosDaUnidadeOrganizacional,
    EnumTipoDeOperacao,
)
from lg_payroll_api.utils.enums import EnumTipoDeDepartamento, EnumTipoStatus, EnumTipoIdentificacaoGestor
from lg_payroll_api.utils.aux_functions import bool_to_int


class LgApiOrganizationalUnitClient(BaseLgServiceClient):
    """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

    Default class to connect with the organizational unit endpoints
    """

    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(
            lg_auth=lg_auth, wsdl_service="v1/ServicoDeUnidadeOrganizacional"
        )
    
    def save(
        self,
        code: int,
        description: str,
        status: EnumTipoStatus,
        company_code: int,
        level: int,
        start_date: date,
        end_date: date = None,
        parent_organizational_unit_code: int = None,
        observation: str = None,
        address_cep: str = None,
        address_street_type_description: str = None,
        address_street_type_code: int = None,
        address_street: str = None,
        address_number: str = None,
        address_complement: str = None,
        address_neighborhood: str = None,
        address_city_code: str = None,
        address_state_code: str = None,
        address_state_acronym: str = None,
        address_country_code: str = None,
        department_type: EnumTipoDeDepartamento = None,
        allowed_companies_codes: list[int] = None,
        allowed_offices_codes: list[int] = None,
        short_description: str = None,
        enable_employee_registration: bool = None,
        manager_identification_type: EnumTipoIdentificacaoGestor = None,
        manager_roles_codes: list[int] = None,
        managers_positions_codes: list[int] = None,

    ) -> LgApiExecReturn:
        """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

        Endpoint to save an organizational unit in LG System

        Returns:
            LgApiReturn: A List of OrderedDict that represents an Object(RetornoDeOperacao) API response
                [
                    Tipo : int
                    Mensagens : [string]
                    CodigoDoErro : string
                    Retorno : string
                ]
        """
        params = {
            "Empresa":{"Codigo": company_code},
            "Nivel": {"Codigo": level},
            "DataFinal": end_date.strftime("%Y-%m-%d") if end_date else None,
            "Observacao": observation,
            "Endereco": {
                "Cep": address_cep,
                "TipoDeLogradouro": {
                    "Descricao": address_street_type_description,
                    "Codigo": address_street_type_code,
                } if address_street_type_description or address_street_type_code else None,
                "Logradouro": address_street,
                "Numero": address_number,
                "Complemento": address_complement,
                "Bairro": address_neighborhood,
                "Municipio": {
                    "Codigo": address_city_code,
                    "Estado": {
                        "Codigo": address_state_code,
                        "Sigla": address_state_acronym,
                        "Pais": {"Codigo": address_country_code} if address_country_code else None,
                    } if address_state_code or address_state_acronym or address_country_code else None,
                } if address_city_code or address_state_code or address_country_code else None,
            } if address_street or address_street_type_code else None,
            "EnumTipoDeDepartamento": department_type,
            "Habilitacoes": {
                "Empresas": [
                    {"Codigo": codigo} for codigo in allowed_companies_codes
                ] if allowed_companies_codes else None,
                "Cargos": [
                    {"Codigo": codigo} for codigo in allowed_offices_codes
                ] if allowed_offices_codes else None,
            } if allowed_companies_codes or allowed_offices_codes else None,
            "DescricaoResumida": short_description,
            "PermiteCadastrarColaborador": bool_to_int(enable_employee_registration),
            "IdentificacaoGestor": manager_identification_type,
            "GestorCargo": [
                {"Codigo": codigo} for codigo in manager_roles_codes
            ] if manager_roles_codes else None,
            "GestorPosicao": [
                {"Codigo": codigo} for codigo in managers_positions_codes
            ] if managers_positions_codes else None,
            "UnidadeOrganizacionalSuperior": {"Codigo": parent_organizational_unit_code} if parent_organizational_unit_code else None,
            "DataInicial": start_date.strftime("%Y-%m-%d"),
            "Descricao": description,
            "Status": status,
            "Codigo": code,
        }
        
        return LgApiExecReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.Salvar,
                    body=params,
                    parse_body_on_request=False,
                )
            )
        )

    def consult_list(
        self,
        company_code: int,
        level: int = None,
        only_normal: Literal[0, 1] = None,
        only_actives: Literal[0, 1] = None,
        only_with_employees_registration_available: Literal[0, 1] = None,
        search_term: str = None,
    ) -> LgApiReturn:
        """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

        Endpoint to get list of organizational units in LG System

        Returns:
            LgApiReturn: A List of OrderedDict that represents an Object(RetornoDeConsultaLista<UnidadeOrganizacionalParcial>) API response
                [
                    Tipo : int
                    Mensagens : [string]
                    CodigoDoErro : string
                    Retorno : list[Object(UnidadeOrganizacionalParcial)]
                ]
        """

        params = {
            "Nivel": level,
            "SomenteNormais": only_normal,
            "SomenteAtivos": only_actives,
            "SomenteComPermissaoParaCadColaborador": only_with_employees_registration_available,
            "TermoDeBusca": search_term,
            "Empresa": {
                "FiltroComCodigoNumerico": {
                    "Codigo": company_code,
                }
            },
        }

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarLista,
                    body=params,
                    parse_body_on_request=False,
                )
            )
        )

    def list_on_demand(
        self,
        company_code: int = None,
        level: int = None,
        only_actives: Literal[0, 1] = None,
        only_with_employees_registration_available: Literal[0, 1] = None,
        search_term: str = None,
        page: int = None,
    ) -> LgApiPaginationReturn:
        """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

        Endpoint to get list on demand of organizational units in LG System

        Returns:

        A List of OrderedDict that represents an Object(RetornoDeConsultaListaPorDemanda<UnidadeOrganizacional>) API response
            [
                Tipo : int
                Mensagens : [string]
                CodigoDoErro : string
                UnidadeOrganizacional : list[Object(UnidadeOrganizacional)]
            ]
        """

        params = {
            "FiltroDeUnidadeOrganizacionalPorDemanda": {
                "Nivel": level,
                "SomenteAtivos": only_actives,
                "SomenteComPermissaoParaCadColaborador": only_with_employees_registration_available,
                "TermoDeBusca": search_term,
                "Empresa": {
                    "FiltroComCodigoNumerico": {
                        "Codigo": company_code,
                    }
                }
                if company_code
                else None,
                "PaginaAtual": page,
            }
        }

        return LgApiPaginationReturn(
            auth=self.lg_client,
            wsdl_service=self.wsdl_client,
            service_client=self.wsdl_client.service.ConsulteListaPorDemanda,
            body=params,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsulteListaPorDemanda,
                    body=params,
                )
            )
        )

    def consult_changed_list(
        self,
        start_date: date,
        end_date: date,
        operation_types: list[EnumTipoDeOperacao] = [
            EnumTipoDeOperacao.ALTERACAO.value,
            EnumTipoDeOperacao.INCLUSAO.value,
            EnumTipoDeOperacao.EXCLUSAO.value,
        ],
        organizational_units_codes: list[int] = None,
        modified_data_type: EnumTipoDeDadosModificadosDaUnidadeOrganizacional = None,
        consult_inferior_organizational_units: Literal[0, 1] = 0,
    ) -> LgApiReturn:
        """LG API INFOS https://portalgentedesucesso.lg.com.br/api.aspx

        Endpoint to get list of organizational units changed in LG System

        Returns:

        A List of OrderedDict that represents an Object(RetornoDeConsultaListaPorDemanda<UnidadeOrganizacional>) API response
            [
                Tipo : int
                Mensagens : [string]
                CodigoDoErro : string
                UnidadeOrganizacional : list[Object(UnidadeOrganizacional)]
            ]
        """

        params = {
            "filtro": {
                "ListaDeCodigos": organizational_units_codes,
                "TipoDeDadosModificados": modified_data_type,
                "ConsultarUnidadesOrganizacionaisInferiores": consult_inferior_organizational_units,
                "TiposDeOperacoes": [
                    {"Operacao": {"Valor": operation}} for operation in operation_types
                ],
                "PeriodoDeBusca": {
                    "DataInicio": start_date.strftime("%Y-%m-%d"),
                    "DataFim": end_date.strftime("%Y-%m-%d"),
                },
            }
        }

        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaDeUnidadesOrganizacionaisModificadas,
                    body=params,
                    parse_body_on_request=True,
                )
            )
        )
