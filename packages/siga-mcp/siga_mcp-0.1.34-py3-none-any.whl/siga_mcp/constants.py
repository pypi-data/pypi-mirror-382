import getpass
from os import getenv
from typing import cast

from siga_mcp._types import TransportType
from siga_mcp.clients import langfuse
from rsb.coroutines.run_sync import run_sync
import aiohttp
import ujson
from siga_mcp.xml_builder import XMLBuilder
import httpx


async def __buscar_matricula_por_ad(ad: str) -> str:
    """Busca a matrícula correspondente a um usuário AD.

    Args:
        ad (str): Nome do usuário AD no formato DOMINIO\\usuario

    Returns:
        int: Matrícula do usuário
    """
    api_key = getenv("AVA_API_KEY")
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/contasAd/buscarUsuarioAdSigaIA/",
            json={"apiKey": api_key, "descricao": ad},
        ) as response:
            json = await response.json(content_type=None)

            result: str = json["result"][0]["USUARIO"]
            return result


async def __buscar_gestores_dtd() -> list[str]:
    return ["8372", "16500", "24142", "25962"]


# Lista dos Tipos de Atendimento.
TYPE_TO_NUMBER = {
    "Suporte Sistema": 1,
    "Implementação": 2,
    "Manutenção Corretiva": 3,
    "Reunião": 4,
    "Treinamento": 5,
    "Mudança de Escopo": 20,
    "Anexo": 12,
    "Suporte Infraestrutura": 13,
    "Monitoramento": 21,
    "Incidente": 23,
    "Requisição": 24,
}

# Mapeamento de meses em português
MESES_PT = {
    "janeiro": 1,
    "jan": 1,
    "fevereiro": 2,
    "fev": 2,
    "março": 3,
    "mar": 3,
    "abril": 4,
    "abr": 4,
    "maio": 5,
    "mai": 5,
    "junho": 6,
    "jun": 6,
    "julho": 7,
    "jul": 7,
    "agosto": 8,
    "ago": 8,
    "aug": 8,
    "setembro": 9,
    "set": 9,
    "sep": 9,
    "outubro": 10,
    "out": 10,
    "oct": 10,
    "novembro": 11,
    "nov": 11,
    "dezembro": 12,
    "dez": 12,
    "dec": 12,
}

# Mapeamento de dias da semana em português
DIAS_SEMANA_PT = {
    "segunda": 0,
    "segunda-feira": 0,
    "seg": 0,
    "terça": 1,
    "terça-feira": 1,
    "ter": 1,
    "terca": 1,
    "terca-feira": 1,
    "quarta": 2,
    "quarta-feira": 2,
    "qua": 2,
    "quinta": 3,
    "quinta-feira": 3,
    "qui": 3,
    "sexta": 4,
    "sexta-feira": 4,
    "sex": 4,
    "sábado": 5,
    "sabado": 5,
    "sab": 5,
    "domingo": 6,
    "dom": 6,
}

# Palavras que indicam tempo futuro/passado
TEMPO_FUTURO = [
    "próximo",
    "proximo",
    "que vem",
    "seguinte",
    "vindouro",
    "daqui a",
    "daqui",
    "vindoura",
    "entrante",
]

TEMPO_PASSADO = [
    "passado",
    "anterior",
    "ultimo",
    "último",
    "atrás",
    "atras",
    "ha",
    "há",
    "retrasado",
    "retrasada",
]

# Números por extenso
NUMEROS_EXTENSO = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "três": 3,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14,
    "quatorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
}

# Expressões de período do dia
PERIODOS_DIA = {
    "manhã": 8,
    "manha": 8,
    "de manhã": 8,
    "de manha": 8,
    "tarde": 14,
    "de tarde": 14,
    "à tarde": 14,
    "a tarde": 14,
    "noite": 20,
    "de noite": 20,
    "à noite": 20,
    "a noite": 20,
    "madrugada": 2,
    "de madrugada": 2,
}

AD = getpass.getuser()

MCP_TRANSPORT: TransportType = cast(TransportType, getenv("MCP_TRANSPORT")) or "stdio"

# Avoid network calls when running under tests/CI or when explicitly disabled.
_DISABLE_NETWORK = getenv("SIGA_DISABLE_NETWORK", "").lower() in {"1", "true", "yes"}
_PYTEST_RUNNING = getenv("PYTEST_CURRENT_TEST") is not None


def _safe_buscar_matricula() -> str:
    # Allow overriding via env for deterministic tests
    override = getenv("SIGA_TEST_MATRICULA")
    if override:
        return override
    if MCP_TRANSPORT == "http" or _DISABLE_NETWORK or _PYTEST_RUNNING:
        return ""
    try:
        return run_sync(__buscar_matricula_por_ad(AD))
    except Exception:
        # Fall back to empty if lookup fails
        return ""


MATRICULA_USUARIO_ATUAL: str = _safe_buscar_matricula()


def _safe_buscar_matriculas_liberadas() -> list[str]:
    if _DISABLE_NETWORK or _PYTEST_RUNNING:
        # Minimal default; can be overridden in tests
        return []
    try:
        return run_sync(__buscar_gestores_dtd())
    except Exception:
        return []


MATRICULAS_LIBERADAS = _safe_buscar_matriculas_liberadas()


# Listagem para a Combo Tipos.
TIPO_TO_NUMBER_ATENDIMENTO_AVULSO = {
    "Suporte Sistema": 1,
    "Manutenção de Banco": 10,
    "Atividade Interna": 19,
}

# Listagem para a Combo Tipos para atendimento avulso de infraestrutura.
TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA = {
    "Atividade Interna": 19,
    "Implementação": 15,
    "Incidente": 23,
    "Manutenção Corretiva": 17,
    "Manutenção de Banco": 10,
    "Manutenção Preventiva": 16,
    "Monitoramento": 22,
    "Requisição": 24,
    "Suporte": 14,
    "Treinamento": 18,
}

# Listagem para a Combo Tipos para OS.
TIPO_TO_NUMBER_OS_SISTEMAS = {
    "Implementação": 2,
    "Manutenção Corretiva": 3,
    "Monitoramento": 21,
    "Mudança de Escopo": 20,
    "Suporte Infraestrutura": 13,
    "Suporte Sistema": 1,
    "Treinamento": 5,
}

# Listagem para a Combo Origem.
ORIGEM_TO_NUMBER = {
    "E-mail": 1,
    "Pessoalmente": 2,
    "Teams": 3,
    "Telefone": 4,
    "WhatsApp": 5,
    "Plantão": 7,
    "SAE": 11,
}

# Listagem para a Combo Origem para OS.
ORIGEM_OS_TO_NUMBER = {
    "E-mail": 1,
    "Pessoalmente": 2,
    "Teams": 3,
    "Telefone": 4,
    "WhatsApp": 5,
    "Plantão": 7,
    "SAE": 11,
    "SATIC": 8,
    "Siga": 6,
}


# Listagem para a Combo Sistema.
SISTEMA_TO_NUMBER = {
    "Abaris": 285,
    "Administrar Permissões e Acesso - Segurança": 45,
    "Analytics / BI": 282,
    "Analytics / BI (Administrativos/Hospitalares)": 305,
    "APP Pega Plantão": 304,
    "Assinatura Digital / Bird ID": 286,
    "Controle de Contratos": 106,
    "Custo/Orçamento Institucional": 226,
    "GEM - Aplicativo de Apoio": 92,
    "Intranet": 302,
    "MV - Almoxarifado": 154,
    "MV - Ambulatório": 155,
    "MV - Apoio à TI": 156,
    "MV - Auditoria e Glosa": 157,
    "MV - Caixa": 158,
    "MV - CCIH": 159,
    "MV - Central de Marcação": 160,
    "MV - Centro Cirúrgico e Obstétrico": 161,
    "MV - CME": 303,
    "MV - Conciliação de Convênios": 163,
    "MV - Contabilidade": 164,
    "MV - Contas a Pagar": 165,
    "MV - Contas a Receber": 166,
    "MV - Controle Bancário": 167,
    "MV - Custos": 217,
    "MV - Diagnóstico por Imagem": 168,
    "MV - Diretoria Clínica": 169,
    "MV - Faturamento de Convênios e Particulares": 170,
    "MV - Faturamento SUS": 171,
    "MV - Gerenciamento de Projetos": 239,
    "MV - Gestão de Documentos": 238,
    "MV - Gestão de Ocorrências": 236,
    "MV - Gestão de Riscos": 237,
    "MV - Higienização": 172,
    "MV - HMed": 264,
    "MV - Internação": 173,
    "MV - Laboratório de Análises Clínicas": 174,
    "MV - Lavanderia e Rouparia": 175,
    "MV - Manutenção": 176,
    "MV - MovDoc": 177,
    "MV - Nutrição": 178,
    "MV - Patrimônio": 179,
    "MV - PEP": 140,
    "MV - Repasse Médico": 219,
    "MV - SAC": 180,
    "MV - SAME": 181,
    "MV - Sistema de Apoio": 129,
    "MV - Tesouraria": 182,
    "MV - Urgência": 223,
    "Prefeitura Universitária": 124,
    "PROT - Protocolo": 108,
    "RCI  - Avaliador (Cópias e Impressões)": 4,
    "RH - Controle de Convênios": 121,
    "RH - Plano de Cargos e Salários": 115,
    "RH - Sistema de Apoio ao Recursos Humanos": 107,
    "RMS - Almoxarifado": 1,
    "RMS - Aprovador": 6,
    "RMS - Avaliador": 8,
    "RMS - Compras": 2,
    "RMS - Gestão de Logística": 122,
    "RMS - Gestão de Serviços": 103,
    "RMS - Gestão de Transporte": 113,
    "RMS - Marketing & Comunicacao": 138,
    "RMS - Patrimônio": 232,
    "RMS - Requisitante": 10,
    "RPA - Recibo de Pagamento Autônomo (Pessoa Física)": 274,
    "Sapiens - Contabilidade": 250,
    "Sapiens - Contas a Pagar": 266,
    "Sapiens - Contas a Receber": 269,
    "Sapiens - Fluxo de Caixa": 268,
    "Sapiens - Recebimento": 267,
    "Sapiens - Sistema de Apoio": 259,
    "Sapiens - Tesouraria": 270,
    "Sapiens - Tributos": 249,
    "Senior - Administração de Pessoal": 184,
    "Senior - Controle de Acesso": 185,
    "Senior - Controle de Ponto": 183,
    "Senior - Jurídico Trabalhista": 278,
    "Senior - Medicina e Segurança do Trabalho": 186,
    "SGA - Acadêmico": 131,
    "SGA - Atividades Administrativas": 110,
    "SGA - Carteirinhas": 125,
    "SGA - Censo": 290,
    "SGA - Contabilidade": 119,
    "SGA - Controle de Ponto": 30,
    "SGA - Controle de Reuniões do Conselho e Câmara": 116,
    "SGA - CPA": 287,
    "SGA - Estágio": 24,
    "SGA - Estágio (Novo)": 224,
    "SGA - Extrator de Dados": 227,
    "SGA - Financeiro": 38,
    "SGA - Formandos": 19,
    "SGA - FORMANDOS (DIPLOMA DIGITAL) - ANTIGO": 277,
    "SGA - FORMANDOS (DIPLOMA DIGITAL) - ATUAL": 300,
    "SGA - Pesquisa": 109,
    "SGA - PIME": 120,
    "SGA - Planejamento EAD": 127,
    "SGA - Pós-Graduação e Extensão": 23,
    "SGA - Pós-Graduação .Net": 248,
    "SGA - Processos Seletivos": 118,
    "SGA - Produção de Materiais Didáticos": 49,
    "SGA - Roteiros": 128,
    "SGA - SISCAP": 272,
    "SGA - Telemarketing": 37,
    "SGA - WEB Administrativo": 222,
    "SGB - Biblioteca": 126,
    "SGS - Clínicas Integradas": 104,
    "SGS - Laboratorio Protese": 230,
    "SGV - Administrativo": 51,
    "SGV - Ambulatório": 52,
    "SGV - Cirúrgico": 53,
    "SGV - Farmácia": 54,
    "SGV - Financeiro": 55,
    "SGV - Financeiro .Net": 229,
    "SGV - Imagem": 221,
    "SGV - Internação": 56,
    "SGV - Laboratório": 57,
    "SGV - LMVP": 58,
    "SGV - Patologia": 59,
    "SGV - Recepção": 60,
    "SIGA - Gestão de Solicitações a DTD / Atividades": 143,
    "Sistemas AVA": 271,
    "Site Institucional": 275,
    "Site UAGRO - Dottatec": 284,
    "Site Universidade do Agro (Drupal)": 301,
    "SITES SAUDE / HOSPITAIS": 295,
    "Sophia": 262,
    "Uniube Sistemas Integrados - USI": 291,
    "Uniube.br - Acesso restrito": 279,
    "Consist Gem - Contabilidade (INATIVO)": 144,
    "Consist Gem - Contas a Pagar (INATIVO)": 146,
    "ORSE - Aplicativo de Apoio (INATIVO)": 93,
    "SGA - Digitalizações (INATIVO)": 43,
    "SGA - Pesquisa MPHU (INATIVO)": 133,
}


# Listagem para a Combo Categoria da Infraestrutura.
CATEGORIA_TO_NUMBER = {
    "AD - Alterar Configuração do Domínio": 13,
    "AD - Criar usuário": 93,
    "AD - Desbloquear usuário": 68,
    "AD - Excluir/Bloquear usuário": 67,
    "AD - Liberar permissões de acesso": 11,
    "AD - Redefinir Senha": 12,
    "AD - Suporte/Dúvidas/Outros": 39,
    "BD - Alterar tabela": 72,
    "BD - Atividade Interna": 94,
    "BD - Atualizar esquema": 56,
    "BD - Corrigir lentidão e bloqueios": 57,
    "BD - Criar tabela/índice": 71,
    "BD - Criar usuário": 54,
    "BD - Liberar acessos/permissões": 69,
    "BD - Monitorar rotina de backups e testes de restauração": 55,
    "BD - Reiniciar tabela / Tablespace": 53,
    "BD - Restauração de LOG": 70,
    "BD - Tunning de instrução": 58,
    "DB - Suporte/Dúvidas/Outros": 96,
    "DPO - Analisar contratos": 74,
    "DPO - Analisar/Autorizar autorização de dados e imagens": 75,
    "DPO - Conscientizar sobre segurança digital": 76,
    "DPO - Criar/Implementar política de segurança": 77,
    "E-mail - Alterar Colaborador Responsável": 5,
    "E-mail - Configurar Google Workspace": 9,
    "E-mail - Configurar primeiro acesso": 8,
    "E-mail - Criar e-mail": 6,
    "E-mail - Desbloquear e-mail": 78,
    "E-mail - Excluir/Bloquear e-mail": 79,
    "E-mail - Redefinir senha": 7,
    "E-mail - Suporte/Dúvidas/Outros": 40,
    "Hardware - Atualizar driver(s)/Firmware(s)/Limpeza computador/notebook": 35,
    "Hardware - Atualizar driver(s)/Firmware(s)/Limpeza impressora/scanner": 65,
    "Hardware - Backup": 24,
    "Hardware - Consertar computador/notebook": 73,
    "Hardware - Consertar/Trocar impressora/scanner": 80,
    "Hardware - Formatar": 25,
    "Hardware - Instalar Antivírus": 34,
    "Hardware - Instalar/Desinstalar/Atualizar Software": 26,
    "Hardware - Suporte/Dúvidas/Outros": 27,
    "Inclusão / Remoção de Colaboradores": 62,
    "Liberar dispositivo de armazenamento": 97,
    "Publicação - AVA": 66,
    "Rede - Alterar perfil de acesso": 2,
    "Rede - Ativar/Crimpar Ponto de Rede": 19,
    "Rede - Configurar Firewall": 4,
    "Rede - Criar/Alterar regra Firewall": 3,
    "Rede - Instalar/Configurar/Atualizar AP/Câmera/Router/Voip": 22,
    "Rede - Instalar/Configurar/Atualizar controle de acesso/catraca": 23,
    "Rede - Instalar/Configurar/Atualizar REP": 21,
    "Rede - Instalar/Configurar/Atualizar Switch/VLAN": 20,
    "Rede - Liberar internet": 81,
    "Rede - Suporte VPN": 60,
    "Rede - Suporte/Dúvidas/Outros": 41,
    "Segurança - Investigar ataques cibernéticos": 83,
    "Segurança - Remover ameaças detectadas": 82,
    "Serviços - Atividade interna": 28,
    "Serviços - Empréstimo de Equipamento": 42,
    "Serviços - Realizar auditoria/Criar relatório": 1,
    "Serviços - Transferir/Recolher equipamento": 36,
    "Serviços - Treinamento": 29,
    "Servidores - Alterar configuração": 15,
    "Servidores - Atualizar driver(s)/Firmware(s)/Limpeza": 89,
    "Servidores - Atualizar/Reiniciar": 16,
    "Servidores - Criar usuário": 85,
    "Servidores - Disparar/Conferir/Restaurar backup": 18,
    "Servidores - Excluir/Bloquear Usuário": 84,
    "Servidores - Liberar/Bloquear permissões": 86,
    "Servidores - Manutenção Corretiva": 88,
    "Servidores - Manutenção Preventiva": 87,
    "Sistemas - Desbloquear usuário": 49,
    "Sistemas - Instalar sistema": 50,
    "Sistemas - Liberar Permissões": 91,
    "Sistemas - Redefinir senha": 51,
    "Sistemas - Retirar Permissões": 90,
    "Sistemas - Suporte/Dúvidas/Outros": 52,
    "Telefonia - Atualizar aparelho": 92,
    "Telefonia - Configurar aparelho": 44,
    "Telefonia - Consertar/Trocar aparelho": 45,
    "Telefonia - Suporte/Dúvidas/Outros": 46,
    "Verificar log de eventos": 98,
    "AD - Atribuir Direitos de Acesso em Pasta/Impressora (INATIVO)": 32,
    "AD - Criar/Renomear/Bloquear/Desbloquear usuário (INATIVO)": 10,
    "Alterar REP (INATIVO)": 63,
    "Catracas - Manutenção Corretiva/Preventiva (INATIVO)": 47,
    "Coletor Biométrico - Manutenção Corretiva/Preventiva (INATIVO)": 48,
    "DPO (INATIVO)": 64,
    "Equipamentos - Instalar/Desinstalar (INATIVO)": 30,
    "Equipamentos - Manutenção Corretiva/Preventiva (INATIVO)": 37,
    "Equipamentos - Suporte/Dúvida/Outros (INATIVO)": 31,
    "Firewall - Suporte/Dúvida/Outros (INATIVO)": 61,
    "Internet - Suporte/Dúvidas/Outros (INATIVO)": 43,
    "Servidores - Criar/Configurar (INATIVO)": 17,
    "Servidores - Criar/Deletar Usuários e/ou Diretórios (INATIVO)": 33,
    "Servidores - Manutenção Preventiva/Corretiva (INATIVO)": 14,
    "Sistemas - Liberar/Retirar Permissão (INATIVO)": 59,
}

# Listagem para a Combo Equipe.

# Note(Arthur): Fernando, isso aqui era pra ser números? Porque tá com siglas.
EQUIPE_TO_NUMBER = {
    "SGA - Acadêmico": "ACAD",
    "RMS (Requisições, Materiais e Serviços)": "RMS",
    "SGA - Financeiro": "FIN",
    "Recursos Humanos": "RH",
    "Financeiro e Contábil": "FINCONT",
    "Saúde": "SAUDE",
    "SGA - Web": "SGAWEB",
    "Administador de Banco de Dados": "DBA",
    "Escritório de Projetos": "PROJ",
    "Analytics": "Analytics",
    "Equipe AVA": "AVA",
}

# Listagem para a Combo Equipe Infraestrutura.

# TODO(Fernando): Atualizar os números quando forem definidos.
EQUIPE_INFRAESTRUTURA_TO_NUMBER = {
    "Administador de Banco de Dados": "DBA",
    "Gerenciamento de Redes": "REDES",
    "Gerenciamento de Redes - Linux": "LINUX",
    "Gerenciamento de Redes - Windows": "WINDOWS",
    "Help-Desk - Aeroporto": "Help Aero",
    "Help-Desk - Ambulatório": "Help Amb",
    "Help-Desk - Araxá": "Help Ara",
    "Help-Desk - Centro": "Help Cen",
    "Help-Desk - HR": "Help HR",
    "Help-Desk - HVU": "Help HVU",
    "Help-Desk - IMM": "Help IMM",
    "Help-Desk - MPHU": "Help MPHU",
    "Help-Desk - NPG": "Help NPG",
    "Help-Desk - UPA Mirante": "Help UPA_M",
    "Help-Desk - UPA São Benedito": "Help UPASB",
    "Help-Desk - Via Centro": "Help Mar",
    "Help-Desk - Vila Gávea": "Help Vila",
    "LIAE - Aeroporto": "LIAE Aero",
    "LIAE - Via Centro": "LIAE Mar",
    "Ouvidoria / Telefonia": "OUVIDORIA",
    "Proteção de dados": "DPO",
    "Publicação AVA": "Pub-AVA",
}

# Listagem para a Combo Projeto.
PROJETO_TO_NUMBER = {
    "Adequações para ONA 2022": (107),
    "Adequações para ONA 2024": 155,
    "Adequações para ONA 2025": 198,
    "Aditivos ao contrato dos alunos": 125,
    "Anonimização de prontuário do paciente": 143,
    "Análise Inicial - Implantação do sistema de imagens na Policlínica": 15,
    "APP do Paciente": 136,
    "Autoria": 77,
    "AVA - CORPORATIVO": 129,
    "Campus Villa Gávea - Infraestrutura e Segurança": 133,
    "Cartão Saúde Uniube": 181,
    "Cartão Vital": 189,
    "Consultoria externa Contábil/Financeiro": 170,
    "Consultoria externa HCM": 171,
    "Controle de limpeza de leitos hospitalares": 145,
    "Controle de registros dos médicos": 137,
    "Criar script de mapeamento das impressoras": 54,
    "Desenvolvimento Componentes / Framework": 188,
    "Desenvolvimento Web / Mobile": 186,
    "Estudo de plataformas de CRM e Vendas": 156,
    "Gestão de Sucesso dos Polos": 118,
    "Graduação - ajustes na transferência, 2ª graduação - 2025": 197,
    "Implantação do módulo jurídico": 99,
    "Implantação do sistema No Harm - Farmácia": 142,
    "Implantação Integração MVPEP e ATRIUM": 146,
    "Implantação UPAs": 131,
    "Integração da modalidade ECG com o PACs": 153,
    "Integração entre Sistema Epimed Monitor UTI e o MVPEP": 174,
    "Integração SAE e Protocolos": 75,
    "ITVix - SIG Polos Integração": 130,
    "Mapeamento AS IS Logística e Central de Malotes": 122,
    "Melhorias e automação de atendimento - MPHU e TakeBlip": 120,
    "Melhorias na Transferência externa e aproveitamento de estudos": 116,
    "Melhorias no módulo de treinamento": 196,
    "Melhorias no Sistema de Geração de Provas e Fechamento de Disciplinas do EAD": 103,
    "Melhorias para SADT - MPHU": 124,
    "Migração .Net (Entity + Crystal)": 101,
    "Migração de sistemas Fox Pro": 138,
    "Migração para o PHP 8": 100,
    "Novo CNES das Clínicas Integradas": 140,
    "Novo formato alfanumérico para o Cadastro Nacional da Pessoa Jurídica (CNPJ)": 205,
    "Operacao Publicacao AVA": 119,
    "Operaçao DPO": 114,
    "Operação Acadêmico": 28,
    "Operação Analytics": 151,
    "Operação AVA": 67,
    "Operação Banco de Dados": 207,
    "Operação Biblioteca": 30,
    "Operação Clínicas": 2,
    "Operação Compras": 3,
    "Operação Financeiro/Contabilidade": 4,
    "Operação Gestão de Relacionamento": 72,
    "Operação Help Desk": 61,
    "Operação HMed": 64,
    "Operação HVU": 5,
    "Operação Infraestrutura": 62,
    "Operação Jurídico Trabalhista": 201,
    "Operação LIAE": 63,
    "Operação Medicina do Trabalho": 199,
    "Operação MV": 6,
    "Operação RH": 7,
    "Operação RMS": 8,
    "Operação Saúde - Web": 187,
    "Operação Segurança do Trabalho": 200,
    "Operação SGA - Financeiro/Contabilidade": 29,
    "Operação Site Institucional": 98,
    "Operação TI": 19,
    "Operação WEB Administrativo": 27,
    "Overmind.ia - Automação entre MV e Convênios": 203,
    "Painéis interativos de sistemas de saúde": 135,
    "Projeto - Fluxo de locação de espaços físicos": 123,
    "Projeto APP Marcação de Ponto para Professores": 139,
    "Projeto App Pega Plantão": 202,
    "Projeto AVA 3.0": 73,
    "Projeto Banco de Questões": 84,
    "Projeto BI": 89,
    "Projeto Carrinhos Beira Leito": 173,
    "Projeto Contratos Empresariais - PROED": 20,
    "Projeto Controle de Acessos dos Hospitais": 157,
    "Projeto Cópia de perfil": 108,
    "Projeto de adequação Rede WIFI": 132,
    "Projeto de Automatização de Convênios do MPHU": 127,
    "Projeto de Controle de Vacinas no HVU": 147,
    "Projeto de desenvolvimento IA para Plano Terapeutico": 204,
    "Projeto de integração Comtele": 93,
    "Projeto de integração Intersaberes": 92,
    "Projeto de Melhoria de Agendamento de Serviços de Transportes": 193,
    "Projeto de melhorias nas Clínicas Integradas": 109,
    "Projeto de Melhorias no Controle de Contratos": 74,
    "Projeto de melhorias no faturamento MPHU": 106,
    "Projeto de melhorias no HVU": 105,
    "Projeto de Melhorias nos Setores Jurídicos": 126,
    "Projeto de melhorias SEU Financeiro": 112,
    "Projeto de Solicitação de Contratação": 110,
    "Projeto Digitalização Secretaria do Conselho Universitário": 160,
    "Projeto Diploma Digital": 97,
    "Projeto Documentação de Telas e Sistemas": 154,
    "Projeto DRG Brasil - Hospitais": 144,
    "Projeto Evolução do Sistema RMS-Almoxarifado": 195,
    "Projeto Fluxo de Situação Acadêmica EAD": 38,
    "Projeto Gestão da Permanência Qualificada": 36,
    "Projeto GIT": 83,
    "Projeto GPQ": 70,
    "Projeto Ilhas de Impressão": 128,
    "Projeto IMM - Implantação Multiempresa": 178,
    "Projeto Implantação Clínicas MV": 190,
    "Projeto Implantação Ábaris - secretaria digital e diplomas": 115,
    "Projeto Implantação Ábaris - XML histórico parcial e oficial": 164,
    "Projeto Inscrição e Matrícula dos Cursos de Graduação": 102,
    "Projeto LGPD": 88,
    "Projeto Limpeza dos Sistemas AVA": 79,
    "Projeto MELHORIA SISTEMA de APOIO RH": 113,
    "Projeto Melhorias no controle de acesso - Hospitais - Campus Centro - Estacionamentos": 177,
    "Projeto Migração para .Net SGA - Financeiro": 31,
    "Projeto Migração para o Sistemas Integrados WEB": 35,
    "Projeto Número de Alunos - Graduação": 149,
    "Projeto Número de Alunos - Pós-Graduação": 150,
    "Projeto Operação Formandos": 152,
    "Projeto Reestruturação do Repasse a Parceiros - PROED": 21,
    "Projeto Revisão Orçamento Institucional": 168,
    "Projeto RH - Análise de Danos Causados pelo Empregado": 185,
    "Projeto RH - Avaliação de Desenvolvimento": 172,
    "Projeto RH - Coleta de assinatura digital dos ASOs": 191,
    "Projeto RH - Plano de Cargos e Salários": 158,
    "Projeto SEAD CONSAE - Etapa 1": 16,
    "Projeto SEAD CONSAE - Etapa 2": 34,
    "Projeto Secretaria Digital": 86,
    "Projeto Sistema de Avaliação da EAD": 78,
    "Projeto Sistemas de Saúde - WEB": 175,
    "Projeto SMS": 85,
    "Projeto Unificação do PIAC": 81,
    "Projeto Unificação do PROEST": 80,
    "Projeto UniFlex": 39,
    "Projeto Universidade do Agro": 111,
    "Projeto Ábaris - Currículo dos cursos em XML": 165,
    "Projeto: Migração do sistema de Compras/Bionexo": 192,
    "Projetos ASSCOM": 90,
    "Projetos de BIs do sistema RMS": 141,
    "Projetos Estágio": 94,
    "Projetos PMO": 96,
    "Projetos PROPEPE": 91,
    "Projetos Setor Financeiro": 148,
    "Publicações AVA": 117,
    "Pós EAD 2.0": 87,
    "Reformulação do SITE MPHU": 180,
    "RMGV": 76,
    "Sistemas Parceiros": 82,
    "Site Hospitalares": 179,
    "Situações acadêmicas da Pós-Graduação": 182,
    "Transformação Digital": 104,
    "Transformação digital - Aproveitamento/transferencia/segunda graduação": 161,
    "Transformação Digital - Reabertura de atividades do AVA": 163,
    "Transformação Digital - Reemissão de boletos (Refit 2024)": 162,
    "Universidade do Agro - Novo site": 183,
    "Universidade MV": 159,
    "Upgrade SO Windows Server 2012 - fim do suporte": 134,
    "Vertifical da Saúde Uniube (projeto)": 206,
}


# Listagem para a Combo Tipos para OS.
LINGUAGEM_TO_NUMBER_OS_SISTEMAS = {
    "C#": 1,
    "Fox": 2,
    "SQL": 3,
    "ASP.Net": 4,
    "Access": 5,
    "PHP": 6,
    "Extrator de Dados": 7,
    "MV Painel de Indicadores": 8,
    "MV Editor": 9,
    "Gerador de Relatórios": 10,
    "Gerador de Cubos": 11,
    "Power BI": 18,
    "Gerador de Tela": 12,
    "Editor de Regra": 13,
    "Delphi": 14,
    "Script SO": 15,
    "Node.js": 23,
    "Senior - Gerador de visão dinâmica": 24,
    "Analytics": 20,
}

# Listagem para a Combo Interna para OS.
OS_INTERNA_OS_TO_NUMBER = {
    "Sim": 1,
    "Não": 0,
}


# Listagem para a Combo Status para OS.
STATUS_OS_TO_NUMBER = {
    "Concluída": 8,
    "Concluída por Encaminhamento": 9,
    "Concluída por substituição": 10,
    "Em Atendimento": 3,
    "Em Implantação": 7,
    "Em Teste": 5,
    "Não Planejada": 1,
    "Pendente-Aprovação": 96,
    "Pendente-Atendimento": 2,
    "Pendente-Atualização de Versão": 93,
    "Pendente-AVA": 94,
    "Pendente-Consultoria": 92,
    "Pendente-Equipe Infraestrutura": 95,
    "Pendente-Equipe Manutenção": 88,
    "Pendente-Fornecedor": 97,
    "Pendente-Help-Desk": 87,
    "Pendente-Liberação": 6,
    "Pendente-Marketing": 89,
    "Pendente-Sist. Acadêmicos": 90,
    "Pendente-Sist. Administrativos": 91,
    "Pendente-Teste": 4,
    "Pendente-Usuário": 98,
    "Solicitação em Aprovação": 101,
    "Cancelada-Usuário": 100,
    "Cancelamento DTD | Arquivado": 99,
}


# Listagem para a Combo Criticidade para OS.
CRITICIDADE_OS_TO_NUMBER = {
    "Nenhuma": 0,
    "Baixa": 1,
    "Média": 2,
    "Alta": 3,
}

# Listagem para a Combo Criticidade para OS.
PRIORIDADE_USUARIO_OS_TO_NUMBER = {
    "Nenhuma": 0,
    "Urgente": 1,
    "Alta": 2,
    "Média": 3,
    "Baixa": 4,
}


def _safe_langfuse_prompt(key: str, default: str = "") -> str:
    try:
        # langfuse may be None if not installed or not initialized
        if langfuse is None or _DISABLE_NETWORK or _PYTEST_RUNNING:
            return default
        prompt = langfuse.get_prompt(key)  # type: ignore[attr-defined]
        return prompt.compile()  # type: ignore[no-any-return]
    except Exception:
        return default


SYSTEM_INSTRUCTIONS: str = _safe_langfuse_prompt("siga.developer", default="")
COLABORADORES_PROMPT: str = _safe_langfuse_prompt("siga.colaboradores", default="")

TEAMS_CLIENT_ID = ""

TEAMS_CLIENT_SECRET = ""

TEAMS_TENANT_ID = ""

PACKAGE_NAME = "siga-mcp"

DEFAULT_PORT = 8000


# Lista todos os usuários responsáveis de acordo com a área informada
# Passar para o arquivo tools e montar o docstring.
# Servirá para quando o usuário pedir a lista de usuários responsáveis da OS
def listar_usuarios_responsaveis_os_siga(area: int) -> str:
    """
    Busca usuários responsáveis por OS SIGA de acordo com a área.

    Args:
        area (int): 1 = Sistemas, 2 = Infraestrutura

    Returns:
        str: XML com lista de usuários responsáveis
    """
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            "https://ava3.uniube.br/ava/api/usuarios/buscarUsuarioResponsavelOsSigaIA/",
            json={
                "apiKey": getenv("AVA_API_KEY"),
                "area": area,
            },
        )

        try:
            json_data = response.json()

            # Ajustar conforme retorno real da API PHP
            data = (
                json_data
                if isinstance(json_data, list)
                else json_data.get("result", json_data)
            )

            retorno = XMLBuilder().build_xml(
                data=data,
                root_element_name="usuarios_responsaveis",
                item_element_name="usuario_responsavel",
                root_attributes={
                    "area": str(area),
                    "tipo": "Sistemas" if area == 1 else "Infraestrutura",
                },
                custom_attributes={"sistema": "SIGA"},
            )

            return retorno

        except Exception:
            return f"Erro ao listar usuários responsáveis área {area}."


# Obter usuário responsável para criação de OS Sistemas e Infraestrutura.
# Usado para montar o Docstring e validação na função, caso o usuário informa matrícula que não está na lista
def obter_usuarios_responsavel(area: int) -> tuple[str, set]:
    """
    Busca usuários responsáveis por área.

    Args:
        area (int): 1 = Sistemas, 2 = Infraestrutura

    Returns:
        tuple: (docstring_formatada, set_ids_validacao)
    """
    # Determinar nome da área para mensagens de erro
    nome_area = "Sistemas" if area == 1 else "Infraestrutura"

    try:
        # Fazer requisição HTTP para buscar usuários responsáveis
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                "https://ava3.uniube.br/ava/api/usuarios/buscarUsuarioResponsavelOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "area": area,
                },
            )

            # Extrair dados JSON da resposta
            json_data = response.json()
            data = (
                json_data
                if isinstance(json_data, list)
                else json_data.get("result", [])
            )

            # Validar se recebeu dados válidos
            if not data or not isinstance(data, list):
                return (
                    f"        - Erro ao carregar usuários responsáveis de {nome_area}",
                    set(),
                )

            # Remover duplicatas usando dict (chave = ID do usuário)
            usuarios_unicos = {}
            for usuario in data:
                if (
                    isinstance(usuario, dict)
                    and "USUARIO" in usuario
                    and "NOME" in usuario
                ):
                    usuarios_unicos[usuario["USUARIO"]] = usuario

            # Verificar se encontrou usuários válidos
            if not usuarios_unicos:
                return (
                    f"        - Nenhum usuário responsável encontrado para {nome_area}",
                    set(),
                )

            # 📝 GERAR LISTA FORMATADA PARA DOCSTRING (ordenada alfabeticamente)
            usuarios_ordenados = sorted(
                usuarios_unicos.values(), key=lambda x: x["NOME"]
            )
            docstring = "\n".join(
                [
                    f'        - "{usuario["NOME"]}" (ID: {usuario["USUARIO"]})'
                    for usuario in usuarios_ordenados
                ]
            )

            # 🔍 GERAR SET DE IDS PARA VALIDAÇÃO RÁPIDA
            ids_validacao = {
                str(usuario["USUARIO"]) for usuario in usuarios_unicos.values()
            }

            # Retornar ambos os resultados em uma tupla
            return (docstring, ids_validacao)

    except Exception:
        # Retornar erro em caso de falha na requisição ou processamento
        return (
            f"        - Erro ao carregar usuários responsáveis de {nome_area}",
            set(),
        )


# ✅ CONSTANTES CACHED - Executam uma vez quando o módulo é carregado
# 📊 Buscar dados para Sistemas (área 1)
USUARIOS_SISTEMAS_DOCSTRING, USUARIOS_SISTEMAS_IDS = obter_usuarios_responsavel(1)
# 🔧 Buscar dados para Infraestrutura (área 2)
USUARIOS_INFRAESTRUTURA_DOCSTRING, USUARIOS_INFRAESTRUTURA_IDS = (
    obter_usuarios_responsavel(2)
)
