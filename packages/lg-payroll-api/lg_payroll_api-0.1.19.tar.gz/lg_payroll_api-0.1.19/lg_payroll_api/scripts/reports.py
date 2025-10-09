from typing import Union

from zeep.helpers import serialize_object

from lg_payroll_api.helpers.api_results import (
    LgApiAsyncConsultReturn,
    LgApiAsyncExecutionReturn,
)
from lg_payroll_api.helpers.base_client import BaseLgServiceClient, LgAuthentication
from lg_payroll_api.utils import ReportParameters


class LgReportServiceClient(BaseLgServiceClient):
    """Lg API report service client class to access report service endpoints.

    This class able you to use report service to generate and consult reports in Lg system.

    Reference: https://portalgentedesucesso.lg.com.br/api.aspx
    """

    def __init__(self, lg_auth: LgAuthentication):
        super().__init__(lg_auth=lg_auth, wsdl_service="v1/ServicoDeRelatorio")

    def consult_task(self, task_id: str) -> LgApiAsyncConsultReturn:
        params = {"IdTarefa": task_id}
        return LgApiAsyncConsultReturn(
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.ConsultarTarefa,
                    body=params,
                    show_envelope=False,
                )
            )
        )

    def generate_report(
        self, company_code: int, report_parameters: Union[list[dict], ReportParameters]
    ) -> LgApiAsyncExecutionReturn:
        """Generate report with parameters configuration. You can create parameters configuration by
        following the oficial documentation, but we recommend to use the `ReportParameters` object to
        create your parameters configuration.

        Args:
            company_code (int, mandatory): Company code, this not affect filters in report.
            report_parameters (Union[list[dict], ReportParameters], mandatory): Parameters used to generate report.

        Return:
            LgApiAsyncExecutionReturn

        Usage Example:
            ```python
            # Example of parameters configuration using ReportParameters

            from lg_payroll_api import LgPayrollApi, LgAuthentication, ReportParameters

            # Set report parameters in variable
            # You can see that format in object lg_payroll_api.utils.models.Relatorio.
            # Alternatively, you can use the format automatically created when you generate a new report at front of system,
            # Getting the "GereListaRelatorio.json" file.
            parameters = [
                {
                    "Id": "123",
                    "Nome": "name.fpl",
                    "DescricaoRelatorio": "description",
                    "TipoArquivoGerado": 0,
                    "TiposDeArquivosDisponiveisParaGeracao": ["0"],
                    "GruposDeParametros": [
                        {
                            "TipoGrupoDeParametrosRelatorio": 0,
                            "Id": 0,
                            "Nome": "name",
                            "IndiceGrupo": 0,
                            "ParametrosDeRelatorio": [
                                {
                                    "IdRelatorio":"123",
                                    "Id":"id",
                                    "IndiceReal":0,
                                    "Nome":"name",
                                    "Descricao":"description",
                                    "Operacao":0,
                                    "TipoDeDado":0,
                                    "Tamanho":0,
                                    "MascaraFormatacao":"",
                                    "Opcional":True,
                                    "PodeConsultarValor":True,
                                    "PossuiDescricao":True,
                                    "CampoDefinidoPorFormula":False,
                                    "Opcoes": [],
                                    "RegrasDeAtivacao": [],
                                    "ValoresPadroes": [],
                                    "ValoresSelecionados": []
                                }
                            ]
                        }
                    ]
                }
            ]

            auth = LgAuthentication()
            lg_api = LgPayrollApi(auth)

            # Instantiate ReportParameters object passing parameters defined before
            report_params = ReportParameters(parameters)

            lg_api.report_service.generate_report(company_code=0, report_parameters=report_params)
            ```
        """
        if isinstance(report_parameters, ReportParameters):
            report_parameters = report_parameters.get_formatted_parameters()

        params = {
            "Empresa": {"Codigo": company_code},
            "Relatorios": {"Relatorio": report_parameters},
        }

        return LgApiAsyncExecutionReturn(
            report_service_class=self,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.GerarRelatorio,
                    body=params,
                    send_none_values=True,
                )
            )
        )

    def generate_report_by_name(
        self, company_code: int, report_name: str, parameters: list[str] = None
    ) -> LgApiAsyncExecutionReturn:
        """LG API INFOS

        Args:
            company_id (int, mandatory): Id of company to generate report
            report_name (str, mandatory): Name of report
            parameters (list[str], optional): List of report parameters

        Returns:

        A LgApiAsyncExecutionReturn that represents an Object(RetornoDeExecucaoAsync) API response
            [
                Tipo : int
                Mensagens : [string]
                CodigoDoErro : string
                Retorno : Object(Empresa)
            ]

        Reference: https://portalgentedesucesso.lg.com.br/api.aspx
        """
        params = {
            "Empresa": {"Codigo": company_code},
            "NomeDoRelatorio": report_name,
            "Parametros": parameters,
        }

        return LgApiAsyncExecutionReturn(
            report_service_class=self,
            **serialize_object(
                self.send_request(
                    service_client=self.wsdl_client.service.GerarRelatorioPorNome,
                    body=params,
                )
            )
        )
