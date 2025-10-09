from typing import Union
from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import (
    LgApiReturn,
    LgApiSaveListReturn
)
from lg_payroll_api.helpers.base_client import (
    BaseLgServiceClient,
    LgAuthentication
)
from lg_payroll_api.utils.enums import EnumTipoDeAdmissao, EnumAgenteNocivo, EnumFiliacaoSindical, EnumFormaDePagamento, EnumTipoPonto
from lg_payroll_api.utils.lg_exceptions import LgParameterListLimitException
from datetime import date
from lg_payroll_api.utils.aux_functions import bool_to_int


class LgApiMovementClient(BaseLgServiceClient):
    """
    Client for interacting with the LG Payroll API's movement (employee transfer and update) services.
    This class provides methods to:
    - Consult the historic list of movements for a single contract, with various optional filters.
    - Consult the historic list of movements for multiple contracts within a company and date range.
    - Register (save) a movement for a contract, supporting a wide range of movement types and related data.
    - Delete a movement for a contract by contract code, company code, and occurrence date.

    Inheritance:
        BaseLgServiceClient: Provides base functionality for LG API service clients.
        lg_auth (LgAuthentication): Authentication object for accessing the LG API.

    Methods:
        consult_historic_list(...): Consults the historic list of a contract with optional search filters.
        consult_list_for_multiple_contracts(...): Consults the historical list for multiple contracts.
        save_movement(...): Registers a movement (transfer, update, or change) for a contract.
        delete_movement(...): Deletes a movement for a contract.

    Returns:
        LgApiReturn, LgApiSaveListReturn, or LgApiExecReturn: Depending on the operation performed.

    Raises:
        LgParameterListLimitException: If the number of contract codes exceeds the allowed limit in consult_list_for_multiple_contracts.
    """

    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(lg_auth=lg_auth, wsdl_service="v1/ServicoDeMovimentacao")
    
    def consult_historic_list(
        self,
        contract_code: str,
        company_code: int,
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
        search_company: bool = None,
        search_position: bool = None,
        search_office: bool = None,
        search_cost_center: bool = None,
        search_organizational_unit: bool = None,
        search_permanent_role: bool = None,
        search_commissioned_role: bool = None,
        search_tax_jurisdiction: bool = None,
        search_responsible_authority: bool = None,
        search_professional_nature: bool = None,
        search_union: bool = None,
        search_professional_liberal_union: bool = None,
        search_harmful_agent: bool = None,
        search_effective_function: bool = None,
        search_commissioned_function: bool = None,
        search_salarial_table: bool = None,
        search_work_shift: bool = None,
        search_banking_data: bool = None,
        search_salary_adjustment: bool = None,
        search_contract_type: bool = None,
    ) -> LgApiReturn:
        """
        Consults the historic list of a contract with various optional search filters.

        Parameters:
            contract_code (str): The contract's unique identifier (matricula).
            company_code (int): The code of the company associated with the contract.
            start_date (Union[date, None], optional): The start date for the search period. Defaults to None.
            end_date (Union[date, None], optional): The end date for the search period. Defaults to None.
            search_company (bool, optional): Whether to include company information in the search. Defaults to False.
            search_position (bool, optional): Whether to include position information in the search. Defaults to False.
            search_office (bool, optional): Whether to include office/establishment information in the search. Defaults to False.
            search_cost_center (bool, optional): Whether to include cost center information in the search. Defaults to False.
            search_organizational_unit (bool, optional): Whether to include organizational unit information in the search. Defaults to False.
            search_permanent_role (bool, optional): Whether to include permanent role information in the search. Defaults to False.
            search_commissioned_role (bool, optional): Whether to include commissioned role information in the search. Defaults to False.
            search_tax_jurisdiction (bool, optional): Whether to include tax jurisdiction information in the search. Defaults to False.
            search_responsible_authority (bool, optional): Whether to include responsible authority information in the search. Defaults to False.
            search_professional_nature (bool, optional): Whether to include professional nature information in the search. Defaults to False.
            search_union (bool, optional): Whether to include union information in the search. Defaults to False.
            search_professional_liberal_union (bool, optional): Whether to include professional liberal union information in the search. Defaults to False.
            search_harmful_agent (bool, optional): Whether to include harmful agent information in the search. Defaults to False.
            search_effective_function (bool, optional): Whether to include effective function information in the search. Defaults to False.
            search_commissioned_function (bool, optional): Whether to include commissioned function information in the search. Defaults to False.
            search_salarial_table (bool, optional): Whether to include salary table information in the search. Defaults to False.
            search_work_shift (bool, optional): Whether to include work shift information in the search. Defaults to False.
            search_banking_data (bool, optional): Whether to include banking data in the search. Defaults to False.
            search_salary_adjustment (bool, optional): Whether to include salary adjustment information in the search. Defaults to False.
            search_contract_type (bool, optional): Whether to include contract type information in the search. Defaults to False.

        Returns:
            LgApiReturn: The result of the API call, containing the historic list data according to the specified filters.
        """
        body = {
            "IdentificacaoDeContrato": {
                "Matricula": contract_code,
                "Empresa": {"Codigo": company_code},
            },
            "Periodo": {
                "DataInicio": (
                    start_date.strftime("%Y-%m-%d") if start_date else None
                ),
                "DataFim": (
                    end_date.strftime("%Y-%m-%d") if end_date else None
                ),
            },
            "EmpresaBuscar": bool_to_int(search_company),
            "PosicaoBuscar": bool_to_int(search_position),
            "EstabelecimentoBuscar": bool_to_int(search_office),
            "CentroDeCustoBuscar": bool_to_int(search_cost_center),
            "UnidadeOrganizacionalBuscar": bool_to_int(search_organizational_unit),
            "CargoEfetivoBuscar": bool_to_int(search_permanent_role),
            "CargoComissionadoBuscar": bool_to_int(search_commissioned_role),
            "LotacaoTributariaBuscar": bool_to_int(search_tax_jurisdiction),
            "OrgaoResponsavelBuscar": bool_to_int(search_responsible_authority),
            "NaturezaProfissionalBuscar": bool_to_int(search_professional_nature),
            "SindicatoBuscar": bool_to_int(search_union),
            "SindicatoProfissionalLiberalBuscar": bool_to_int(search_professional_liberal_union),
            "AgenteNocivoBuscar": bool_to_int(search_harmful_agent),
            "FuncaoEfetivaBuscar": bool_to_int(search_effective_function),
            "FuncaoComissionadaBuscar": bool_to_int(search_commissioned_function),
            "TabelaSalarialBuscar": bool_to_int(search_salarial_table),
            "EscalaBuscar": bool_to_int(search_work_shift),
            "DadosBancariosBuscar": bool_to_int(search_banking_data),
            "ReajusteSalarialBuscar": bool_to_int(search_salary_adjustment),
            "ModalidadeContratualBuscar": bool_to_int(search_contract_type),
        }
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaHistorico,
                    body=body,
                    parse_body_on_request=False,
                )
            )
        )
    
    def consult_list_for_multiple_contracts(
        self,
        company_code: int,
        contracts_codes: list[str],
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
    ) -> LgApiReturn:
        """
        Consults the historical list for multiple contracts within a specified company and date range.
        Args:
            company_code (int): The code of the company to query.
            contracts_codes (list[str], mandatory): A list of contract codes (matriculas) to consult. 
                The maximum allowed is 50.
            start_date (Union[date, None], optional): The start date for the period to consult. Defaults to None.
            end_date (Union[date, None], optional): The end date for the period to consult. Defaults to None.
        Returns:
            LgApiReturn: The result of the API call, containing the historical data for the specified contracts.
        Raises:
            LgParameterListLimitException: If the number of contract codes exceeds the allowed limit.
        """
        limit_contracts: int = 50
        if contracts_codes and len(contracts_codes) > limit_contracts:
            raise LgParameterListLimitException(
                f"The maximum number of contracts is {limit_contracts}."
            )
        
        body = {
            "CodigoDaEmpresa": company_code,
            "ListaDeMatriculas": [{"string": contract} for contract in contracts_codes],
            "Periodo": {
                "DataInicio": (
                    start_date.strftime("%Y-%m-%d") if start_date else None
                ),
                "DataFim": (
                    end_date.strftime("%Y-%m-%d") if end_date else None
                ),
            },
        }
        return LgApiReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarListaParaVariosContratos,
                    body=body,
                )
            )
        )

    def save_movement(
        self,
        contract_code: str,
        company_code: int,
        occurrence_date: date,
        description: str,
        reason_code: int,
        new_company_code: int = None,
        use_current_contract_code: bool = None,
        contract_code_in_new_company: str = None,
        contract_code_esocial_new_company: str = None,
        transfer_employee_historic: bool = None,
        admission_type_esocial: EnumTipoDeAdmissao = None,
        new_position_code: str = None,
        new_office_code: str = None,
        new_tax_jurisdiction_code: str = None,
        new_responsible_authority_code: str = None,
        new_organizational_unit_code: str = None,
        movement_even_if_the_colaborator_is_manager: bool = None,
        new_cost_center_code: str = None,
        new_effective_role_code: str = None,
        frame_new_effective_role: bool = None,
        new_salarial_table_effective_role_code: str = None,
        new_salarial_range_effective_role_code: str = None,
        new_salarial_level_effective_role_code: str = None,
        new_commissioned_role_code: str = None,
        new_salarial_table_commissioned_role_code: str = None,
        new_salarial_range_commissioned_role_code: str = None,
        new_salarial_level_commissioned_role_code: str = None,
        new_effective_function_code: str = None,
        new_salarial_table_effective_function_code: str = None,
        new_salarial_range_effective_function_code: str = None,
        new_salarial_level_effective_function_code: str = None,
        new_commissioned_function_code: str = None,
        new_salarial_table_commissioned_function_code: str = None,
        new_salarial_range_commissioned_function_code: str = None,
        new_salarial_level_commissioned_function_code: str = None,
        unlink_variable_salary: bool = None,
        variable_salary_description: str = None,
        new_harmful_agent_type: EnumAgenteNocivo = None,
        new_professional_nature_code: str = None,
        unlink_professional_nature: bool = None,
        new_union_code: str = None,
        unlink_union: bool = None,
        compare_salary_with_base_of_new_union: bool = None,
        new_professional_liberal_union_code: str = None,
        unlink_professional_liberal_union: bool = None,
        new_union_filiation_type: EnumFiliacaoSindical = None,
        unlink_union_filiation_type: bool = None,
        new_bank_agency_code: str = None,
        new_bank_code: str = None,
        new_bank_account_number: str = None,
        new_bank_account_digit: str = None,
        new_payment_method: EnumFormaDePagamento = None,
        new_account_type: str = None,
        unlink_banking_data: bool = None,
        new_work_shift_code: str = None,
        new_timekeeping_type: EnumTipoPonto = None,
        timekeeping_required: bool = None,
        new_contract_type_code: str = None,
        observations: str = None,
        class_description: str = None,
        unlink_class: bool = None,
    ) -> LgApiSaveListReturn:
        """
        Registers a movement (transfer, update, or change) for a contract in the payroll system.

        Args:
            contract_code (str): The contract code (employee registration number).
            company_code (int): The code of the company where the contract currently exists.
            occurrence_date (date): The date when the movement occurs.
            description (str): Description of the movement.
            reason_code (int): Code representing the reason for the movement.
            new_company_code (int, optional): Code of the destination company for transfer movements.
            use_current_contract_code (bool, optional): Whether to use the same contract code in the new company.
            contract_code_in_new_company (str, optional): Contract code to be used in the new company.
            contract_code_esocial_new_company (str, optional): eSocial contract code for the new company.
            transfer_employee_historic (bool, optional): Whether to transfer the employee's history.
            admission_type_esocial (EnumTipoDeAdmissao, optional): eSocial admission type for the new company.
            new_position_code (str, optional): Code of the new position.
            new_office_code (str, optional): Code of the new office/establishment.
            new_tax_jurisdiction_code (str, optional): Code of the new tax jurisdiction.
            new_responsible_authority_code (str, optional): Code of the new responsible authority.
            new_organizational_unit_code (str, optional): Code of the new organizational unit.
            movement_even_if_the_colaborator_is_manager (bool, optional): Move even if the employee is the unit manager.
            new_cost_center_code (str, optional): Code of the new cost center.
            new_effective_role_code (str, optional): Code of the new effective role.
            frame_new_effective_role (bool, optional): Whether to frame the new effective role.
            new_salarial_table_effective_role_code (str, optional): Code of the new salary table for the effective role.
            new_salarial_range_effective_role_code (str, optional): Code of the new salary range for the effective role.
            new_salarial_level_effective_role_code (str, optional): Code of the new salary level for the effective role.
            new_commissioned_role_code (str, optional): Code of the new commissioned role.
            new_salarial_table_commissioned_role_code (str, optional): Code of the new salary table for the commissioned role.
            new_salarial_range_commissioned_role_code (str, optional): Code of the new salary range for the commissioned role.
            new_salarial_level_commissioned_role_code (str, optional): Code of the new salary level for the commissioned role.
            new_effective_function_code (str, optional): Code of the new effective function.
            new_salarial_table_effective_function_code (str, optional): Code of the new salary table for the effective function.
            new_salarial_range_effective_function_code (str, optional): Code of the new salary range for the effective function.
            new_salarial_level_effective_function_code (str, optional): Code of the new salary level for the effective function.
            new_commissioned_function_code (str, optional): Code of the new commissioned function.
            new_salarial_table_commissioned_function_code (str, optional): Code of the new salary table for the commissioned function.
            new_salarial_range_commissioned_function_code (str, optional): Code of the new salary range for the commissioned function.
            new_salarial_level_commissioned_function_code (str, optional): Code of the new salary level for the commissioned function.
            unlink_variable_salary (bool, optional): Whether to unlink the variable salary.
            variable_salary_description (str, optional): Description for the variable salary.
            new_harmful_agent_type (EnumAgenteNocivo, optional): Type of harmful agent for the new position.
            new_professional_nature_code (str, optional): Code of the new professional nature.
            unlink_professional_nature (bool, optional): Whether to unlink the professional nature.
            new_union_code (str, optional): Code of the new union.
            unlink_union (bool, optional): Whether to unlink the union.
            compare_salary_with_base_of_new_union (bool, optional): Compare salary with the base of the new union.
            new_professional_liberal_union_code (str, optional): Code of the new professional liberal union.
            unlink_professional_liberal_union (bool, optional): Whether to unlink the professional liberal union.
            new_union_filiation_type (EnumFiliacaoSindical, optional): Type of new union filiation.
            unlink_union_filiation_type (bool, optional): Whether to unlink the union filiation type.
            new_bank_agency_code (str, optional): Code of the new bank agency.
            new_bank_code (str, optional): Code of the new bank.
            new_bank_account_number (str, optional): New bank account number.
            new_bank_account_digit (str, optional): New bank account digit.
            new_payment_method (EnumFormaDePagamento, optional): New payment method.
            new_account_type (str, optional): New account type.
            unlink_banking_data (bool, optional): Whether to unlink banking data.
            new_work_shift_code (str, optional): Code of the new work shift.
            new_timekeeping_type (EnumTipoPonto, optional): New timekeeping type.
            timekeeping_required (bool, optional): Whether timekeeping is required.
            new_contract_type_code (str, optional): Code of the new contract type.
            observations (str, optional): Additional observations.
            class_description (str, optional): Description of the class.
            unlink_class (bool, optional): Whether to unlink the class.

        Returns:
            LgApiExecReturn: The result of the movement registration operation.
        """
        factory_moved_items = self.wsdl_client.type_factory("ns1")
        moved_items = []
        if new_company_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoEmpresa(
                CodigoDaEmpresaDestino=new_company_code,
                UtilizarAMesmaMatriculaDaEmpresaDeOrigemNaEmpresaDestino=bool_to_int(use_current_contract_code),
                MatriculaNaEmpresaDestino=contract_code_in_new_company,
                MatriculaEsocialNaEmpresaDestino=contract_code_esocial_new_company,
                TransferirHistoricoDoColaborador=bool_to_int(transfer_employee_historic),
                TipoDeAdmissaoEsocial=(
                    admission_type_esocial.value
                    if admission_type_esocial else None
                ))
            )
        
        if new_position_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoPosicao(
                    Codigo=new_position_code,
                )
            )
        if new_office_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoEstabelecimento(
                Codigo=new_office_code,
            ))
        if new_tax_jurisdiction_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoLotacaoTributaria(
                Codigo=new_tax_jurisdiction_code,
            ))
        if new_responsible_authority_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoOrgaoResponsavel(
                Codigo=new_responsible_authority_code,
            ))
        if new_organizational_unit_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoUnidadeOrganizacional(
                Codigo=new_organizational_unit_code,
                MovimentarMesmoQueColaboradorSejaGestorDaUnidade=bool_to_int(movement_even_if_the_colaborator_is_manager),
            ))
        if new_cost_center_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoCentroDeCusto(
                Codigo=new_cost_center_code,
            ))
        if new_effective_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoCargoEfetivo(
                Codigo=new_effective_role_code,
                EnquadrarCargoEfetivo=bool_to_int(frame_new_effective_role),
            ))
        if new_salarial_table_effective_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoTabelaSalarialCargoEfetivo(
                Codigo=new_salarial_table_effective_role_code,
            ))
        if new_salarial_range_effective_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFaixaSalarialCargoEfetivo(
                Codigo=new_salarial_range_effective_role_code,
            ))
        if new_salarial_level_effective_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoNivelSalarialCargoEfetivo(
                Codigo=new_salarial_level_effective_role_code,
            ))
        if new_commissioned_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoCargoComissionado(
                Codigo=new_commissioned_role_code,
            ))
        if new_salarial_table_commissioned_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoTabelaSalarialCargoComissionado(
                Codigo=new_salarial_table_commissioned_role_code,
            ))
        if new_salarial_range_commissioned_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFaixaSalarialCargoComissionado(
                Codigo=new_salarial_range_commissioned_role_code,
            ))
        if new_salarial_level_commissioned_role_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoNivelSalarialCargoComissionado(
                Codigo=new_salarial_level_commissioned_role_code,
            ))
        if new_effective_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFuncaoEfetiva(
                Codigo=new_effective_function_code,
            ))
        if new_salarial_table_effective_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoTabelaSalarialFuncaoEfetiva(
                Codigo=new_salarial_table_effective_function_code,
            ))
        if new_salarial_range_effective_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFaixaSalarialFuncaoEfetiva(
                Codigo=new_salarial_range_effective_function_code,
            ))
        if new_salarial_level_effective_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoNivelSalarialFuncaoEfetiva(
                Codigo=new_salarial_level_effective_function_code,
            ))
        if new_commissioned_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFuncaoComissionada(
                Codigo=new_commissioned_function_code,
            ))
        if new_salarial_table_commissioned_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoTabelaSalarialFuncaoComissionada(
                Codigo=new_salarial_table_commissioned_function_code,
            ))
        if new_salarial_range_commissioned_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFaixaSalarialFuncaoComissionada(
                Codigo=new_salarial_range_commissioned_function_code,
            ))
        if new_salarial_level_commissioned_function_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoNivelSalarialFuncaoComissionada(
                Codigo=new_salarial_level_commissioned_function_code,
            ))
        if unlink_variable_salary is not None or variable_salary_description is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoDescricaoDoSalarioVariavel(
                Desvincular=bool_to_int(unlink_variable_salary),
                Descricao=variable_salary_description,
            ))
        if new_harmful_agent_type is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoAgenteNocivo(
                AgenteNocivo=new_harmful_agent_type.value,
            ))
        if new_professional_nature_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoNaturezaProfissional(
                Codigo=new_professional_nature_code,
                Desvincular=bool_to_int(unlink_professional_nature),
            ))
        if new_union_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoSindicato(
                Codigo=new_union_code,
                Desvincular=bool_to_int(unlink_union),
                CompararSalarioComOPisoDoNovoSindicato=compare_salary_with_base_of_new_union,
            ))
        if new_professional_liberal_union_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoSindicatoProfissionalLiberal(
                Codigo=new_professional_liberal_union_code,
                Desvincular=bool_to_int(unlink_professional_liberal_union),
            ))
        if new_union_filiation_type is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoFiliacaoSindical(
                FiliacaoSindical=new_union_filiation_type.value,
                Desvincular=bool_to_int(unlink_union_filiation_type),
            ))
        if new_bank_agency_code is not None or new_bank_code is not None or \
           new_bank_account_number is not None or new_bank_account_digit is not None or \
           new_payment_method is not None or new_account_type is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoDadosBancariosV3(
                CodigoDaAgencia=new_bank_agency_code,
                CodigoDoBanco=new_bank_code,
                Conta=new_bank_account_number,
                DigitoDaConta=new_bank_account_digit,
                FormaDePagamento=(
                    new_payment_method.value if new_payment_method else None
                ),
                TipoDaConta=new_account_type,
                Desvincular=bool_to_int(unlink_banking_data),
            ))
        
        if new_work_shift_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoEscala(
                Codigo=new_work_shift_code,
            ))
        if new_timekeeping_type is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoTipoDePonto(
                TipoDePonto=new_timekeeping_type.value,
            ))
        if timekeeping_required is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoMarcarPonto(
                Valor=bool_to_int(timekeeping_required),
            ))

        if new_contract_type_code is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoModalidadeContratual(
                Codigo=new_contract_type_code,
            ))
        
        if class_description is not None:
            moved_items.append(factory_moved_items.ItemMovimentadoTurma(
                Descricao=class_description,
                Desvincular=bool_to_int(unlink_class),
            ))

        body = {
            "MovimentacaoV2":{
                "IdentificacaoDoContrato": {
                    "Matricula": contract_code,
                    "Empresa": {"Codigo": company_code},
                },
                "DataDaOcorrencia": occurrence_date.strftime("%Y-%m-%d"),
                "ParametrosDeMovimentacao": {
                    "Descricao": description,
                    "Motivo": {"Codigo": reason_code},
                    "Observacoes": observations,
                },
                "ItensMovimentados": {
                    "ItemMovimentadoAbstratoV2": moved_items
                },
            }
        }
        return LgApiSaveListReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.CadastrarLista,
                    body=body,
                )
            )
        )

    def delete_movement(
        self,
        contract_code: str,
        company_code: int,
        occurrence_date: date,
    ) -> LgApiSaveListReturn:
        """
        Deletes a movement for a contract in the payroll system.

        Args:
            contract_code (str): The contract code (employee registration number).
            company_code (int): The code of the company where the contract currently exists.
            occurrence_date (date): The date when the movement occurs.

        Returns:
            LgApiExecReturn: The result of the movement deletion operation.
        """
        body = {
            "IdentificacaoDoContrato": {
                "IdentificacaoDeContrato": {
                    "Matricula": contract_code,
                    "Empresa": {"Codigo": company_code},
                },
                "DataOcorrencia": occurrence_date.strftime("%Y-%m-%d"),
            }
        }
        return LgApiSaveListReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ExcluirLista,
                    body=body,
                )
            )
        )
