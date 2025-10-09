from enum import Enum
from typing import Literal


def get_enum_value(value: Enum) -> int:
    if isinstance(value, Enum):
        value = value.value

    return value


SITUATIONS = Literal["Afastamento", "Atividade normal", "Férias", "Recesso", "Rescisão"]
Bool = Literal[0, 1]


class EnumTipoDeDadosModificados(int, Enum):
    CONTRATUAIS = 1
    PESSOAIS = 2
    CONTRATUAIS_E_PESSOAIS = 3


class EnumTipoDeOperacao(int, Enum):
    INCLUSAO = 1
    ALTERACAO = 2
    EXCLUSAO = 3


class EnumTipoDeOperacaoContratoLog(int, Enum):
    INCLUSAO = 1
    ALTERACAO = 2
    EXCLUSAO = 3


class EnumTipoDeDadosModificadosDaUnidadeOrganizacional(int, Enum):
    DADOS_QUE_ALTERAM_HIERARQUIA = 1


class EnumTipoDeRetorno(int, Enum):
    SUCESSO = 0
    INCONSISTENCIA = 1
    ERRO = 2
    NAO_PROCESSADO = 3


class EnumOperacaoExecutada(int, Enum):
    NENHUM = 0
    OBJETO_SEM_ALTERACAO = 1
    CADASTRO = 2
    ATUALIZACAO = 3
    EXCLUSAO = 4
    CADASTRO_EM_LOTE = 5
    VALIDACAO = 6


class EnumCampoDeBuscaDoContratoDeTrabalho(int, Enum):
    MATRICULA = 0
    ID_PESSOA = 1
    CPF = 2
    IDENTIDADE = 3
    RIC = 4
    CTPS = 5
    PIS = 6
    TITULO_ELEITOR = 7
    CNH = 8


# Reports Enums


class EnumTipoArquivoRelatorio(int, Enum):
    PDF = 0
    TXT = 1
    CSV = 2


class EnumTipoGrupoDeParametrosRelatorio(int, Enum):
    PARAMETRO_DE_USUARIO = 0
    SENTENCA_SIMPLES = 1
    SENTENCA_DINAMICA = 2


class EnumOperacaoParametroRelatorio(int, Enum):
    IGUAL = 0
    DIFERENTE = 1
    MAIOR = 2
    MENOR = 3
    MAIOR_IGUAL = 4
    MENOR_IGUAL = 5
    UM_DOS_VALORES = 6
    NAO_UM_DOS_VALORES = 7


class EnumTipoDeDadoParametroRelatorio(int, Enum):
    FDT_CHAR = 0
    FDT_SHORT = 1
    FDT_INT = 2
    FDT_FLOAT = 3
    FDT_DATE_AMD = 4
    FDT_DATE_AM = 5
    FDT_BOOLEAN = 6
    FDT_DATE_SQL = 7


class EnumCampoContato(int, Enum):
    DDD_TELEFONE = 0
    TELEFONE = 1
    DDD_CELULAR = 2
    CELULAR = 3
    RAMAL = 4
    EMAIL_CORPORATIVO = 5
    EMAIL_PARTICULAR = 6
    LINKEDIN = 7
    FACEBOOK = 8
    TWITTER = 9

class EnumIdentificadorInformacaoAdicional(str ,Enum):
    CENTRO_DE_CUSTO = "InfoAdicCentroDeCusto"
    POSICAO = "InfoAdicPosicao"
    DEPARTAMENTO = "InfoAdicUnidadeOrganizacional"
    ESTABELECIMENTO = "InfoAdicEstabelecimento"
    CONTRATO_DE_TRABALHO = "InfoAdicContratoDeTrabalho"

class EnumTipoEntidadeInformacaoAdicional(int, Enum):
    NENHUM = 0
    EMPRESA = 2
    CENTRO_DE_CUSTO = 1000
    ORGAO_RESPONSAVEL = 1002
    CARGO = 1016
    DEPENDENTE = 1019
    PENSIONISTA = 1020
    SINDICATO = 1028
    PESSOA = 1029
    POSICAO = 1030
    DEPARTAMENTO = 1031
    ESTABELECIMENTO = 1032
    CONTRATO_DE_TRABALHO = 1034
    FUNCAO = 1058
    TOMADOR = 1062
    EVENTO = 1077
    FORNECEDOR = 1183
    AUTONOMO = 1194
    REQUISICAO = 3002
    CONTRATO_ATIVIDADE_APROVACAO = 3004
    VAGA = 3010
    CANDIDATO = 3014
    MOVIMENTACAO_WORKFLOW = 3020
    WKF_FERIAS = 3021
    WKF_RECESSO = 3022
    WKF_RESCISAO = 3023
    WKF_MOVIMENTACAO_CEDER = 3024
    WKF_MOVIMENTACAO_BUSCAR = 3025
    WKF_REQUISICAO = 3026
    WKF_DADOS_PESSOAIS = 3027
    WKF_DEPENDENTES = 3028
    WKF_BENEFICIOS = 3029
    ATIVIDADE = 3030
    VALE_TRANSPORTE = 3031
    WKF_AFASTAMENTO = 3032
    WKF_LANCAMENTO_DE_VALORES = 3033
    HEADCOUNT = 4011
    LINHA_DE_TRANSPORTE = 5000
    UNIDADE_DE_ENTREGA = 5002
    OKR_QUADRO = 8000
    OKR_OBJETIVO = 8001
    OKR_KEYRESULT = 8002
    OKR_INICIATIVA = 8003


class EnumTipoDeInformacaoAdicional(int, Enum):
    TEXTO = 0
    VERDADEIRO_OU_FALSO = 1
    NUMERO = 2
    MOEDA = 3
    DATA = 4
    LISTA_SELECAO_UNICA = 5
    LISTA_MULTIPLA_SELECAO = 6


class EnumTipoStatus(int, Enum):
    ATIVO = 0
    INATIVO = 1
    INATIVACAO_PROGRAMADA = 2
    RESTRITO = -1111


class EnumTipoPonto(int, Enum):
    Manual = 1
    Eletronico = 2


class EnumGrauDeInstrucao(int, Enum):
    NENHUM = 0
    ANALFABETO = 1
    ATEQUARTASERIEINCOMPLETAENSINOFUNDAMENTAL = 2
    QUARTASERIECOMPLETAENSINO = 3
    QUINTAOITAVAENSINOFUNDAMENTAL = 4
    ENSINOFUNDAMENTALCOMPLETO = 5
    ENSINOMEDIOINCOMPLETO = 6
    ENSINOMEDIOCOMPLETO = 7
    EDUCACAOSUPERIORINCOMPLETA = 8
    EDUCACAOSUPERIORCOMPLETA = 9
    POSGRADUACAOCOMPLETA = 10
    DOUTORADOCOMPLETO = 11
    SEGUNDO_GRAU_TECNICO_INCOMPLETO = 12
    SEGUNDO_GRAU_TECNICO_COMPLETO = 13
    MESTRADOCOMPLETO = 14
    POS_DOUTORADO = 15


class EnumMesesExperiencia(int, Enum):
    TRES_MESES = 3
    SEIS_MESES = 6
    NOVE_MESES = 9
    UM_ANO = 12
    DOIS_ANOS = 24
    TRES_ANOS = 36
    QUATRO_ANOS = 48
    CINCO_ANOS = 60
    SEIS_ANOS = 72
    SETE_ANOS = 84
    OITO_ANOS = 96
    NOVE_ANOS = 108
    DEZ_ANOS = 120
    QUINZE_ANOS = 180
    VINTE_ANOS = 240


class EnumModeloPosicao(int, Enum):
    POSICAO_TEMPORARIA = 0
    DUPLICAR_POSICAO = 1


class EnumTipoDeAdmissao(int, Enum):
    ADMISSAO = 1
    TRANSFERENCIA_DE_EMPRESA_DO_MESMO_GRUPO = 2
    TRANSFERENCIA_DE_EMPRESA_CONSORCIADA = 3
    TRANSFERENCIA_POR_MOTIVO_DE_SUCESSÃO = 4
    MUDANCA_DE_CPF = 6
    TRANSFERENCIA_DE_EMPRESA_SUCEDIDA_INAPTA = 7


class EnumAgenteNocivo(int, Enum):
    TRABALHADOR_NUNCA_ESTEVE_EXPOSTO = 0
    NAO_EXPOSTO_UNICO_VINCULO = 1
    EXPOSTO_APOSENTADORIA_EM_15_ANOS_DE_SERVICO = 2
    EXPOSTO_APOSENTADORIA_EM_20_ANOS_DE_SERVICO = 3
    EXPOSTO_APOSENTADORIA_EM_25_ANOS_DE_SERVICO = 4
    NAO_EXPOSTO_MULTIPLOS_VINCULOS = 5
    EXPOSTO_APOSENTADORIA_EM_15_ANOS_DE_SERVICO_MULTIPLOS_VINCULOS = 6
    EXPOSTO_APOSENTADORIA_EM_20_ANOS_DE_SERVICO_MULTIPLOS_VINCULOS = 7
    EXPOSTO_APOSENTADORIA_EM_25_ANOS_DE_SERVICO_MULTIPLOS_VINCULOS = 8


class EnumFiliacaoSindical(int, Enum):
    NAO_FILIADO = 0
    FILIADO_AO_SINDICATO = 1
    FILIADO_AO_SINDICATO_PROFICIONAL_LIBERAL = 2
    FILIADO_EM_AMBOS_OS_SINDICATOS = 3


class EnumFormaDePagamento(int, Enum):
    NENHUM = 0
    CREDITO_EM_CONTA_CORRENTE = 1
    CARTAO_SALARIO = 2
    CARTAO_SAQUE = 3
    CHEQUE_ADMINISTRATIVO = 4
    CONTA_EXPRESSA = 5
    CREDITO_EM_CONTA_POUPANCA = 6
    CREDITO_EM_CONTA_REAL_TIME = 7
    PAGAMENTO_DOC = 8
    FICHA_DE_COMPENSACAO = 9
    ORDEM_DE_PAGAMENTO = 10
    RECIBO = 11
    PAGAMENTO_TED = 12
    PAGAMENTO_DINHEIRO = 13


class EnumTipoDeDepartamento(int, Enum):
    NORMAL = 0
    STAFF = 1


class EnumTipoIdentificacaoGestor(int, Enum):
    CARGO = 1016
    POSICAO = 1030
    COLABORADOR = 1079
