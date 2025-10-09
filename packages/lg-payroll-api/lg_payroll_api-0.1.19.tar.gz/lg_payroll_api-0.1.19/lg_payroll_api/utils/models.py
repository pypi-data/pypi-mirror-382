from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date, datetime

from zeep.client import Factory

from lg_payroll_api.utils.enums import (
    Bool,
    EnumOperacaoParametroRelatorio,
    EnumTipoArquivoRelatorio,
    EnumTipoDeDadoParametroRelatorio,
    EnumTipoGrupoDeParametrosRelatorio,
)


class ServiceParametersAdapter:
    """This class contains methods that help to transform dataclasses that represent
    API objects, in dictionaries, respecting the object nomenclature.
    """

    @classmethod
    def match_args(cls) -> dict:
        match_arguments: list = [_field.name for _field in fields(cls)]
        parameters = cls.__annotations__
        result: dict = {cls.__name__: match_arguments}

        for key, value in parameters.items():
            args = getattr(value, "__args__", None)
            args = args[0] if args else None

            if is_dataclass(value):
                if hasattr(value, "match_args"):
                    match_arguments.append(value.match_args())

            elif is_dataclass(args):
                if hasattr(args, "match_args"):
                    match_arguments.append(args.match_args())

        return result

    def as_dict(self, obj_factory: Factory = None) -> dict:
        """Generate dictionary of objects configured to use as report parameters"""
        parameters = self.__class__.__annotations__
        record = {}
        for key, value in parameters.items():
            param_value = self.__dict__[key]
            args = getattr(value, "__args__", None)
            args = args[0] if args else None

            if is_dataclass(value) and param_value:
                if hasattr(param_value, "as_dict"):
                    record[key] = param_value.as_dict()

                else:
                    record[key] = param_value

            elif isinstance(param_value, list) and param_value:
                record_list = []

                for val in param_value:
                    if hasattr(val, "as_dict"):
                        record_list.append(val.as_dict())
                        list_key = val.__class__.__name__

                    else:
                        record_list.append(val)
                        if isinstance(val, str):
                            list_key = "string"

                        else:
                            list_key = val.__class__.__name__

                record[key] = {list_key: record_list}

            else:
                record[key] = param_value

        if obj_factory:
            complexType = getattr(obj_factory, self.__class__.__name__)
            result = complexType(**record)

        else:
            result = record

        return result


@dataclass
class NestedDataClass:
    """Aux dataclass to work with dataclasses attributes into anothers dataclasses"""

    def __post_init__(self):
        self.__nested_objs()

    def __nested_objs(self):
        parameters = self.__class__.__annotations__
        for key, value in parameters.items():
            args = getattr(value, "__args__", None)
            args = args[0] if args else None
            param_value = self.__dict__[key]

            if is_dataclass(value) or is_dataclass(args):
                if isinstance(param_value, dict):
                    self.__dict__[key] = value(**param_value)

                elif isinstance(param_value, list):
                    self.__dict__[key] = [args(**item) for item in param_value]

            if value == date and isinstance(param_value, datetime):
                self.__dict__[key] = param_value.date()


@dataclass
class ValorParametro(ServiceParametersAdapter):
    IdentificacaoValorDoParametro: int = None
    Valor: int = None
    Descricao: int = None


@dataclass
class RegraDeAtivacaoDoParametro(ServiceParametersAdapter):
    IdentificadorDoParametro: str = None
    Operador: EnumOperacaoParametroRelatorio = None
    ListaDeValores: list[str] = field(default_factory=list)


@dataclass
class ParametroDeRelatorio(NestedDataClass, ServiceParametersAdapter):
    IdRelatorio: str
    Id: str
    IndiceReal: int
    Nome: str
    Descricao: str
    Operacao: EnumOperacaoParametroRelatorio
    TipoDeDado: EnumTipoDeDadoParametroRelatorio
    Tamanho: int
    MascaraFormatacao: str
    Opcional: Bool
    PodeConsultarValor: Bool
    PossuiDescricao: Bool
    CampoDefinidoPorFormula: Bool
    Opcoes: list[ValorParametro] = field(default_factory=list)
    RegrasDeAtivacao: list[RegraDeAtivacaoDoParametro] = field(default_factory=list)
    ValoresPadroes: list[str] = field(default_factory=list)
    ValoresSelecionados: list[ValorParametro] = field(default_factory=list)


@dataclass
class GrupoDeParametros(NestedDataClass, ServiceParametersAdapter):
    TipoGrupoDeParametrosRelatorio: EnumTipoGrupoDeParametrosRelatorio
    Id: int
    Nome: str
    IndiceGrupo: int
    ParametrosDeRelatorio: list[ParametroDeRelatorio]


@dataclass
class Relatorio(NestedDataClass, ServiceParametersAdapter):
    """Report data. Used to define report parameters."""

    Id: str
    Nome: str
    DescricaoRelatorio: str
    TipoArquivoGerado: EnumTipoArquivoRelatorio
    TiposDeArquivosDisponiveisParaGeracao: list[EnumTipoArquivoRelatorio] = field(
        default_factory=list
    )
    GruposDeParametros: list[GrupoDeParametros] = field(default_factory=list)
    GruposDeOrdenacao: list[str] = field(default_factory=list)
    GrupoDeOrdenacaoPadrao: str = None
    GrupoDeOrdenacaoSelecionado: str = None
    ExtensaoRelatorioGerado: str = None

    def __post_init__(self):
        self.TiposDeArquivosDisponiveisParaGeracao = [
            str(item) for item in self.TiposDeArquivosDisponiveisParaGeracao
        ]
        return super().__post_init__()
