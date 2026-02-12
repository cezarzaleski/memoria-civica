"""Pipeline ETL para o domínio de Votações.

Orquestra a leitura de CSVs, validação de dados com FK validation,
e persistência em banco de dados, com logging e tratamento de erros.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.database import get_db

from .models import Votacao
from .repository import OrientacaoRepository, VotacaoProposicaoRepository, VotacaoRepository, VotoRepository
from .schemas import OrientacaoCreate, VotacaoCreate, VotacaoProposicaoCreate, VotoCreate

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def extract_votacoes_csv(csv_path: str) -> list[dict]:
    """Extrai dados de votações do arquivo CSV.

    Lê o arquivo CSV usando o encoding UTF-8 e separador ';' (padrão da API Câmara).
    Retorna lista de dicionários com os dados brutos.

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        Lista de dicionários com os dados lidos do CSV

    Raises:
        FileNotFoundError: Se o arquivo CSV não existir
        Exception: Se houver erro na leitura do CSV

    Examples:
        >>> data = extract_votacoes_csv("data/votacoes.csv")
        >>> len(data) > 0
        True
        >>> "proposicao_id" in data[0]
        True
    """
    path = Path(csv_path)
    if not path.exists():
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            data = list(reader)
            logger.info(f"Extraído {len(data)} registros do CSV: {csv_path}")
            return data
    except Exception as e:
        logger.error(f"Erro ao ler CSV {csv_path}: {e}")
        raise


def extract_votos_csv(csv_path: str) -> list[dict]:
    """Extrai dados de votos do arquivo CSV.

    Lê o arquivo CSV usando o encoding UTF-8 e separador ';' (padrão da API Câmara).
    Retorna lista de dicionários com os dados brutos.

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        Lista de dicionários com os dados lidos do CSV

    Raises:
        FileNotFoundError: Se o arquivo CSV não existir
        Exception: Se houver erro na leitura do CSV

    Examples:
        >>> data = extract_votos_csv("data/votos.csv")
        >>> len(data) > 0
        True
        >>> "votacao_id" in data[0]
        True
    """
    path = Path(csv_path)
    if not path.exists():
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            data = list(reader)
            logger.info(f"Extraído {len(data)} registros do CSV: {csv_path}")
            return data
    except Exception as e:
        logger.error(f"Erro ao ler CSV {csv_path}: {e}")
        raise


def transform_votacoes(
    raw_data: list[dict],
    db: Session | None = None,
) -> list[VotacaoCreate]:
    """Transforma dados brutos de votações em schemas Pydantic validados.

    Valida cada registro usando VotacaoCreate schema, capturando
    erros de validação e logando warnings para dados inválidos.
    Também valida que proposicao_id existe no banco (FK validation).

    O CSV da Câmara usa os seguintes campos:
    - id: ID da votação (string como "2458405-38", extraímos parte numérica)
    - dataHoraRegistro: Data/hora no formato ISO 8601
    - ultimaApresentacaoProposicao_idProposicao: ID da proposição votada
    - aprovacao: 1 se aprovado, 0 se rejeitado
    - descricao: Descrição textual do resultado

    Args:
        raw_data: Lista de dicionários com dados brutos do CSV
        db: Sessão de banco para validação de FK

    Returns:
        Lista de schemas VotacaoCreate validados

    Examples:
        >>> raw = [
        ...     {
        ...         "id": "2458405-38",
        ...         "ultimaApresentacaoProposicao_idProposicao": "123",
        ...         "dataHoraRegistro": "2024-01-15T14:30:00",
        ...         "aprovacao": "1"
        ...     }
        ... ]
        >>> transformed = transform_votacoes(raw)
        >>> len(transformed) > 0
        True
    """
    validated = []
    skipped = 0

    for idx, record in enumerate(raw_data, 1):
        try:
            # Extrair ID da votação (formato "2458405-38" → extrair número antes do hífen)
            raw_id = record.get("id", "")
            if raw_id and "-" in raw_id:
                votacao_id = int(raw_id.split("-")[0])
            elif raw_id:
                votacao_id = int(raw_id)
            else:
                votacao_id = idx

            # Extrair proposicao_id do campo correto
            prop_id_str = record.get("ultimaApresentacaoProposicao_idProposicao", "")
            proposicao_id = int(prop_id_str) if prop_id_str and prop_id_str != "0" else 0

            # Data/hora do registro (fallbacks para variacoes do CSV)
            data_hora_str = record.get("dataHoraRegistro", "").strip()
            if not data_hora_str:
                data_hora_str = record.get("ultimaAberturaVotacao_dataHoraRegistro", "").strip()
            if not data_hora_str:
                data_hora_str = record.get("data", "").strip()

            # Resultado: usar aprovacao (1/0) ou derivar da descrição
            aprovacao = record.get("aprovacao", "")
            descricao_raw = record.get("descricao", "").strip()
            if aprovacao == "1":
                resultado = "APROVADO"
            elif aprovacao == "0":
                resultado = "REJEITADO"
            elif "aprovad" in descricao_raw.lower():
                resultado = "APROVADO"
            elif "rejeitad" in descricao_raw.lower():
                resultado = "REJEITADO"
            else:
                resultado = descricao_raw[:20] if descricao_raw else "INDEFINIDO"

            # Extrair novos campos do CSV
            votos_sim_str = record.get("quantidadeVotosSim", "") or record.get("votosSim", "")
            votos_nao_str = record.get("quantidadeVotosNao", "") or record.get("votosNao", "")
            votos_outros_str = record.get("quantidadeVotosOutros", "") or record.get("votosOutros", "")
            sigla_orgao_raw = record.get("siglaOrgao", "").strip()

            try:
                votos_sim = int(votos_sim_str) if votos_sim_str else 0
            except (ValueError, TypeError):
                votos_sim = 0

            try:
                votos_nao = int(votos_nao_str) if votos_nao_str else 0
            except (ValueError, TypeError):
                votos_nao = 0

            try:
                votos_outros = int(votos_outros_str) if votos_outros_str else 0
            except (ValueError, TypeError):
                votos_outros = 0

            eh_nominal = votos_sim > 0
            descricao = descricao_raw if descricao_raw else None
            sigla_orgao = sigla_orgao_raw if sigla_orgao_raw else None

            # Parse datetime
            if data_hora_str:
                try:
                    if len(data_hora_str) == 10:
                        data_hora_str = f"{data_hora_str}T00:00:00"
                    data_hora = datetime.fromisoformat(data_hora_str)
                except ValueError:
                    logger.warning(f"Votação {idx}: data_hora inválida '{data_hora_str}'")
                    skipped += 1
                    continue
            else:
                logger.warning(f"Votação {idx}: data_hora vazia")
                skipped += 1
                continue

            # Tratar proposicao_id nullable: votações sem proposição são aceitas com None
            if proposicao_id == 0:
                proposicao_id = None

            # Validar FK proposicao_id se db foi fornecido e proposicao_id não é None
            if db is not None and proposicao_id is not None and proposicao_id > 0:
                from src.proposicoes.models import Proposicao

                stmt = select(Proposicao).where(Proposicao.id == proposicao_id)
                prop_exists = db.execute(stmt).scalar_one_or_none()
                if not prop_exists:
                    logger.debug(f"Votação {idx}: proposicao_id {proposicao_id} não existe no banco")
                    skipped += 1
                    continue

            schema = VotacaoCreate(
                id=votacao_id,
                proposicao_id=proposicao_id,
                data_hora=data_hora,
                resultado=resultado,
                eh_nominal=eh_nominal,
                votos_sim=votos_sim,
                votos_nao=votos_nao,
                votos_outros=votos_outros,
                descricao=descricao,
                sigla_orgao=sigla_orgao,
            )
            validated.append(schema)

        except ValidationError as e:
            logger.warning(f"Validação falhou para votação {idx}: {e}")
            skipped += 1
        except Exception as e:
            logger.warning(f"Erro ao transformar votação {idx}: {e}")
            skipped += 1

    logger.info(f"Transformadas {len(validated)} votações (skipped: {skipped})")
    return validated


def transform_votos(
    raw_data: list[dict],
    db: Session | None = None,
) -> list[VotoCreate]:
    """Transforma dados brutos de votos em schemas Pydantic validados.

    Valida cada registro usando VotoCreate schema, capturando
    erros de validação e logando warnings para dados inválidos.
    Também valida que votacao_id e deputado_id existem no banco (FK validation).

    O CSV da Câmara usa os seguintes campos:
    - idVotacao: ID da votação (string como "106701-223", extraímos parte numérica)
    - deputado_id: ID do deputado
    - voto: Tipo de voto (Sim, Não, Abstenção, etc.)

    Args:
        raw_data: Lista de dicionários com dados brutos do CSV
        db: Sessão de banco para validação de FK

    Returns:
        Lista de schemas VotoCreate validados

    Examples:
        >>> raw = [
        ...     {
        ...         "idVotacao": "106701-223",
        ...         "deputado_id": "456",
        ...         "voto": "Sim"
        ...     }
        ... ]
        >>> transformed = transform_votos(raw)
        >>> len(transformed) > 0
        True
    """
    validated = []
    skipped = 0
    skipped_votacao = 0
    skipped_deputado = 0

    for idx, record in enumerate(raw_data, 1):
        try:
            # ID do voto: usar índice já que não existe coluna específica
            voto_id = idx

            # Extrair votacao_id do campo idVotacao (formato "106701-223" → parte numérica antes do hífen)
            raw_votacao_id = record.get("idVotacao", "") or record.get("votacao_id", "")
            if raw_votacao_id and "-" in str(raw_votacao_id):
                votacao_id = int(str(raw_votacao_id).split("-")[0])
            elif raw_votacao_id:
                votacao_id = int(raw_votacao_id)
            else:
                votacao_id = 0

            # deputado_id - campo existe no CSV
            deputado_id_str = record.get("deputado_id", "")
            deputado_id = int(deputado_id_str) if deputado_id_str else 0

            # Tipo de voto - normalizar para maiúsculas
            voto_tipo = record.get("voto", "").strip()
            # Normalizar: "Sim" → "SIM", "Não" → "NAO", etc.
            voto_mapping = {
                "sim": "SIM",
                "não": "NAO",
                "nao": "NAO",
                "abstenção": "ABSTENCAO",
                "abstencao": "ABSTENCAO",
                "obstrução": "OBSTRUCAO",
                "obstrucao": "OBSTRUCAO",
            }
            voto_normalizado = voto_mapping.get(voto_tipo.lower(), voto_tipo.upper())

            if votacao_id == 0:
                skipped += 1
                continue

            if deputado_id == 0:
                skipped += 1
                continue

            # Validar votacao_id existe no banco se db foi fornecido
            if db is not None and votacao_id > 0:
                stmt = select(Votacao).where(Votacao.id == votacao_id)
                votacao_exists = db.execute(stmt).scalar_one_or_none()
                if not votacao_exists:
                    skipped_votacao += 1
                    skipped += 1
                    continue

            # Validar deputado_id existe no banco se db foi fornecido
            if db is not None and deputado_id > 0:
                from src.deputados.models import Deputado

                stmt = select(Deputado).where(Deputado.id == deputado_id)
                deputado_exists = db.execute(stmt).scalar_one_or_none()
                if not deputado_exists:
                    skipped_deputado += 1
                    skipped += 1
                    continue

            schema = VotoCreate(
                id=voto_id,
                votacao_id=votacao_id,
                deputado_id=deputado_id,
                voto=voto_normalizado,
            )
            validated.append(schema)

        except ValidationError as e:
            logger.warning(f"Validação falhou para voto {idx}: {e}")
            skipped += 1
        except Exception as e:
            logger.warning(f"Erro ao transformar voto {idx}: {e}")
            skipped += 1

    logger.info(f"Transformados {len(validated)} votos (skipped: {skipped}, votacao_not_found: {skipped_votacao}, deputado_not_found: {skipped_deputado})")
    return validated


def load_votacoes(
    votacoes: list[VotacaoCreate],
    db: Session | None = None,
) -> int:
    """Carrega votações validadas no banco de dados.

    Usa bulk_upsert do repository para inserir/atualizar eficientemente,
    garantindo idempotência (pode ser chamado múltiplas vezes).

    Args:
        votacoes: Lista de schemas validados
        db: Sessão de banco opcional (se None, usa get_db())

    Returns:
        Quantidade de votações inseridas/atualizadas

    Examples:
        >>> from src.votacoes.schemas import VotacaoCreate
        >>> from datetime import datetime
        >>> votacoes = [
        ...     VotacaoCreate(
        ...         id=1, proposicao_id=123,
        ...         data_hora=datetime(2024, 1, 15, 14, 30, 0),
        ...         resultado="APROVADO"
        ...     ),
        ... ]
        >>> count = load_votacoes(votacoes)
        >>> count
        1
    """
    if not votacoes:
        logger.info("Nenhuma votação para carregar")
        return 0

    # Deduplicar por ID para evitar violação de PK quando o CSV traz repetidos
    unique_by_id: dict[int, VotacaoCreate] = {}
    duplicates = 0
    for votacao in votacoes:
        if votacao.id in unique_by_id:
            duplicates += 1
        unique_by_id[votacao.id] = votacao
    if duplicates:
        logger.warning(
            "Votações duplicadas no input: %s (mantendo último registro por id)",
            duplicates,
        )
    votacoes = list(unique_by_id.values())

    # Se db não foi fornecido, usar get_db()
    if db is None:
        with get_db() as db:
            repo = VotacaoRepository(db)
            count = repo.bulk_upsert(votacoes)
    else:
        repo = VotacaoRepository(db)
        count = repo.bulk_upsert(votacoes)

    logger.info(f"Carregadas {count} votações no banco de dados")
    return count


def load_votos(
    votos: list[VotoCreate],
    db: Session | None = None,
) -> int:
    """Carrega votos validados no banco de dados.

    Usa bulk_insert do repository para inserção em massa.

    Args:
        votos: Lista de schemas validados
        db: Sessão de banco opcional (se None, usa get_db())

    Returns:
        Quantidade de votos inseridos

    Examples:
        >>> from src.votacoes.schemas import VotoCreate
        >>> votos = [
        ...     VotoCreate(
        ...         id=1, votacao_id=123, deputado_id=456,
        ...         voto="SIM"
        ...     ),
        ... ]
        >>> count = load_votos(votos)
        >>> count
        1
    """
    if not votos:
        logger.info("Nenhum voto para carregar")
        return 0

    # Se db não foi fornecido, usar get_db()
    if db is None:
        with get_db() as db:
            repo = VotoRepository(db)
            count = repo.bulk_insert(votos)
    else:
        repo = VotoRepository(db)
        count = repo.bulk_insert(votos)

    logger.info(f"Carregados {count} votos no banco de dados")
    return count


def run_votacoes_etl(
    votacoes_csv: str,
    votos_csv: str,
    db: object | None = None,
) -> int:
    """Executa o pipeline ETL completo para votações.

    Orquestra extract → transform → load em uma única chamada.
    Persiste votações ANTES de votos para satisfazer FK constraints.
    Transforma e carrega votacoes ANTES de transformar votos para permitir FK validation.

    Args:
        votacoes_csv: Caminho para o arquivo CSV de votações
        votos_csv: Caminho para o arquivo CSV de votos
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Exit code (0 sucesso, 1 falha)

    Examples:
        >>> exit_code = run_votacoes_etl(
        ...     "data/votacoes.csv",
        ...     "data/votos.csv"
        ... )
        >>> exit_code
        0
    """
    try:
        logger.info(f"Iniciando ETL de votações: {votacoes_csv} e votos: {votos_csv}")

        # Garantir que temos db para validação de FK
        if db is None:
            db_context = get_db()
            db = db_context.__enter__()
        else:
            db_context = None

        try:
            # Extract ambos os CSVs
            raw_votacoes = extract_votacoes_csv(votacoes_csv)
            raw_votos = extract_votos_csv(votos_csv)

            # Transform e Load votações PRIMEIRO
            # (necessário para que votos possam validar FK votacao_id)
            validated_votacoes = transform_votacoes(raw_votacoes, db)
            votacoes_count = load_votacoes(validated_votacoes, db)
            logger.info(f"Carregadas {votacoes_count} votações")

            # Agora transform votos (com FK validation para votacao_id e deputado_id)
            validated_votos = transform_votos(raw_votos, db)

            # Load votos
            votos_count = load_votos(validated_votos, db)

            logger.info(
                f"ETL de votações concluído: {votacoes_count} votações + {votos_count} votos persistidos"
            )
            return 0

        finally:
            if db_context is not None:
                db_context.__exit__(None, None, None)

    except Exception as e:
        logger.error(f"ETL de votações falhou: {e}")
        return 1


# Prioridade de tipos legislativos para eleição de eh_principal
# Quanto menor o índice, maior a prioridade
_TIPO_PRIORIDADE = {
    "PEC": 0,
    "PLP": 1,
    "PL": 2,
    "MPV": 3,
    "PDL": 4,
    "PFC": 5,
    "TVR": 6,
    "REQ": 7,
}
_PRIORIDADE_DEFAULT = 99


def extract_votacoes_proposicoes_csv(csv_path: str) -> list[dict]:
    """Extrai dados de votações-proposições do arquivo CSV.

    Lê o CSV de vínculos votação↔proposição usando encoding UTF-8
    e separador ';' (padrão Dados Abertos da Câmara).

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        Lista de dicionários com os dados brutos do CSV

    Raises:
        FileNotFoundError: Se o arquivo CSV não existir
    """
    path = Path(csv_path)
    if not path.exists():
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            data = list(reader)
            logger.info(f"Extraídos {len(data)} registros do CSV: {csv_path}")
            return data
    except Exception as e:
        logger.error(f"Erro ao ler CSV {csv_path}: {e}")
        raise


def _parse_votacao_id(raw_id: str) -> tuple[int, str]:
    """Parseia o idVotacao do CSV para (votacao_id numérico, id_original).

    O formato do CSV é "NNNNNN-N" (ex: "2367548-7").
    A parte antes do hífen corresponde ao PK em votacoes.id.

    Args:
        raw_id: ID da votação no formato do CSV

    Returns:
        Tupla (votacao_id, votacao_id_original)

    Raises:
        ValueError: Se o formato é inválido
    """
    raw_id = raw_id.strip()
    if not raw_id:
        raise ValueError("idVotacao vazio")
    votacao_id = int(raw_id.split("-")[0]) if "-" in raw_id else int(raw_id)
    return votacao_id, raw_id


def _criar_proposicao_parcial(
    proposicao_id: int,
    record: dict,
    db: Session,
) -> bool:
    """Cria uma proposição parcial a partir dos dados do CSV de votações-proposições.

    Quando uma proposição referenciada no CSV não existe no banco,
    cria uma versão parcial com os dados disponíveis (título, tipo, número, ano).

    Args:
        proposicao_id: ID da proposição a criar
        record: Dicionário com dados brutos do CSV
        db: Sessão de banco de dados

    Returns:
        True se criada com sucesso, False em caso de erro
    """
    from src.proposicoes.models import Proposicao
    from src.proposicoes.schemas import ProposicaoCreate

    sigla_tipo = (record.get("proposicao_siglaTipo") or "").strip().upper()
    numero_str = record.get("proposicao_numero", "")
    ano_str = record.get("proposicao_ano", "")
    titulo = (record.get("proposicao_titulo") or "").strip()
    ementa = (record.get("proposicao_ementa") or "").strip()

    try:
        numero = int(numero_str) if numero_str else 0
        ano = int(ano_str) if ano_str else 0
    except (ValueError, TypeError):
        numero = 0
        ano = 0

    tipo = sigla_tipo if sigla_tipo else "ND"

    try:
        schema = ProposicaoCreate(
            id=proposicao_id,
            tipo=tipo,
            numero=numero,
            ano=ano,
            ementa=ementa or titulo or f"{tipo} {numero}/{ano}",
        )
        db_proposicao = Proposicao(
            id=schema.id,
            tipo=schema.tipo,
            numero=schema.numero,
            ano=schema.ano,
            ementa=schema.ementa,
            autor_id=None,
        )
        db.add(db_proposicao)
        db.flush()
        logger.info(
            f"Criada proposição parcial: id={proposicao_id}, "
            f"tipo={tipo}, num={numero}/{ano}"
        )
        return True
    except Exception as e:
        db.rollback()
        logger.warning(
            f"Erro ao criar proposição parcial {proposicao_id}: {e}"
        )
        return False


def _eleger_principal(records: list[VotacaoProposicaoCreate]) -> list[VotacaoProposicaoCreate]:
    """Elege a proposição principal para cada votação por prioridade de tipo.

    Agrupa os registros por votacao_id e marca eh_principal=True para
    a proposição com maior prioridade de tipo legislativo:
    PEC > PLP > PL > MPV > PDL > PFC > TVR > REQ > outros

    Em caso de empate de prioridade, mantém a primeira encontrada.

    Args:
        records: Lista de VotacaoProposicaoCreate

    Returns:
        Lista atualizada com eh_principal definido
    """
    from collections import defaultdict

    groups: dict[int, list[int]] = defaultdict(list)
    for i, r in enumerate(records):
        groups[r.votacao_id].append(i)

    for _votacao_id, indices in groups.items():
        best_idx = indices[0]
        best_prio = _TIPO_PRIORIDADE.get(
            (records[best_idx].sigla_tipo or "").upper(), _PRIORIDADE_DEFAULT
        )
        for idx in indices[1:]:
            prio = _TIPO_PRIORIDADE.get(
                (records[idx].sigla_tipo or "").upper(), _PRIORIDADE_DEFAULT
            )
            if prio < best_prio:
                best_prio = prio
                best_idx = idx

        # Marcar o principal
        for idx in indices:
            records[idx] = records[idx].model_copy(
                update={"eh_principal": idx == best_idx}
            )

    return records


def transform_votacoes_proposicoes(
    raw_data: list[dict],
    db: Session,
) -> list[VotacaoProposicaoCreate]:
    """Transforma dados brutos de votações-proposições em schemas validados.

    Realiza:
    1. Parse de idVotacao (split no hífen para obter votacao_id numérico)
    2. Validação de FK votacao_id contra tabela votacoes (skip se não existe)
    3. Validação de FK proposicao_id contra tabela proposicoes
       (cria proposição parcial se não existe)
    4. Eleição de eh_principal por prioridade de tipo legislativo

    Args:
        raw_data: Lista de dicionários com dados brutos do CSV
        db: Sessão de banco para validação de FK e criação de proposições parciais

    Returns:
        Lista de schemas VotacaoProposicaoCreate validados
    """
    from src.proposicoes.models import Proposicao

    validated = []
    skipped = 0
    proposicoes_parciais_criadas = 0

    # Cache de IDs existentes para evitar queries repetidas
    votacao_ids_cache: dict[int, bool] = {}
    proposicao_ids_cache: dict[int, bool] = {}

    for idx, record in enumerate(raw_data, 1):
        try:
            # 1. Parse idVotacao
            raw_id = record.get("idVotacao", "")
            try:
                votacao_id, votacao_id_original = _parse_votacao_id(raw_id)
            except (ValueError, TypeError):
                logger.warning(
                    f"Registro {idx}: idVotacao inválido '{raw_id}', skipado"
                )
                skipped += 1
                continue

            # 2. Validar FK votacao_id
            if votacao_id not in votacao_ids_cache:
                stmt = select(Votacao).where(Votacao.id == votacao_id)
                exists = db.execute(stmt).scalar_one_or_none() is not None
                votacao_ids_cache[votacao_id] = exists

            if not votacao_ids_cache[votacao_id]:
                logger.warning(
                    f"Registro {idx}: votacao_id {votacao_id} não encontrada "
                    f"em votacoes — registro skipado"
                )
                skipped += 1
                continue

            # 3. Parse proposicao_id
            prop_id_str = record.get("proposicao_id", "")
            try:
                proposicao_id = int(prop_id_str) if prop_id_str else 0
            except (ValueError, TypeError):
                logger.warning(
                    f"Registro {idx}: proposicao_id inválido '{prop_id_str}', skipado"
                )
                skipped += 1
                continue

            if proposicao_id <= 0:
                logger.warning(
                    f"Registro {idx}: proposicao_id inválido ({proposicao_id}), skipado"
                )
                skipped += 1
                continue

            # 4. Validar FK proposicao_id — criar proposição parcial se necessário
            if proposicao_id not in proposicao_ids_cache:
                stmt = select(Proposicao).where(Proposicao.id == proposicao_id)
                exists = db.execute(stmt).scalar_one_or_none() is not None
                proposicao_ids_cache[proposicao_id] = exists

            if not proposicao_ids_cache[proposicao_id]:
                created = _criar_proposicao_parcial(proposicao_id, record, db)
                if created:
                    proposicao_ids_cache[proposicao_id] = True
                    proposicoes_parciais_criadas += 1
                else:
                    logger.warning(
                        f"Registro {idx}: não foi possível criar proposição "
                        f"parcial {proposicao_id}, skipado"
                    )
                    skipped += 1
                    continue

            # 5. Extrair campos opcionais
            titulo = (record.get("proposicao_titulo") or "").strip() or None
            ementa = (record.get("proposicao_ementa") or "").strip() or None
            sigla_tipo = (record.get("proposicao_siglaTipo") or "").strip().upper() or None
            numero_str = record.get("proposicao_numero", "")
            ano_str = record.get("proposicao_ano", "")

            try:
                numero = int(numero_str) if numero_str else None
            except (ValueError, TypeError):
                numero = None

            try:
                ano = int(ano_str) if ano_str else None
            except (ValueError, TypeError):
                ano = None

            schema = VotacaoProposicaoCreate(
                votacao_id=votacao_id,
                votacao_id_original=votacao_id_original,
                proposicao_id=proposicao_id,
                titulo=titulo,
                ementa=ementa,
                sigla_tipo=sigla_tipo,
                numero=numero,
                ano=ano,
                eh_principal=False,  # Será eleito depois
            )
            validated.append(schema)

        except ValidationError as e:
            logger.warning(f"Validação falhou para registro {idx}: {e}")
            skipped += 1
        except Exception as e:
            logger.warning(f"Erro ao transformar registro {idx}: {e}")
            skipped += 1

    # 6. Eleger eh_principal por prioridade de tipo
    if validated:
        validated = _eleger_principal(validated)

    logger.info(
        f"Transform votacoes_proposicoes: {len(validated)} válidos, "
        f"{skipped} skipados, {proposicoes_parciais_criadas} proposições parciais criadas"
    )
    return validated


def load_votacoes_proposicoes(
    records: list[VotacaoProposicaoCreate],
    db: Session,
) -> int:
    """Carrega vínculos votação-proposição no banco de dados.

    Usa VotacaoProposicaoRepository.bulk_upsert para inserção/atualização
    idempotente via INSERT...ON CONFLICT.

    Args:
        records: Lista de schemas validados
        db: Sessão de banco de dados

    Returns:
        Quantidade de registros carregados
    """
    if not records:
        logger.info("Nenhum vínculo votação-proposição para carregar")
        return 0

    # Deduplicar por (votacao_id, proposicao_id) para evitar conflito no upsert
    unique_by_key: dict[tuple[int, int], VotacaoProposicaoCreate] = {}
    duplicates = 0
    for record in records:
        key = (record.votacao_id, record.proposicao_id)
        if key in unique_by_key:
            duplicates += 1
        unique_by_key[key] = record
    if duplicates:
        logger.warning(
            "Vínculos votacao-proposicao duplicados no input: %s (mantendo último por chave)",
            duplicates,
        )
    records = list(unique_by_key.values())

    repo = VotacaoProposicaoRepository(db)
    count = repo.bulk_upsert(records)

    logger.info(f"Carregados {count} vínculos votação-proposição no banco")
    return count


def run_votacoes_proposicoes_etl(
    csv_path: str,
    db: Session | None = None,
) -> int:
    """Executa o pipeline ETL para vínculos votação↔proposição.

    Orquestra extract → transform → load para o CSV votacoesProposicoes.
    Step CRÍTICO: falha interrompe o pipeline.

    Args:
        csv_path: Caminho para o arquivo CSV de votações-proposições
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Quantidade de registros carregados

    Raises:
        Exception: Se qualquer etapa falhar (step crítico)
    """
    logger.info(f"Iniciando ETL votacoes_proposicoes: {csv_path}")

    if db is None:
        with get_db() as db:
            return _run_votacoes_proposicoes_etl_impl(csv_path, db)
    else:
        return _run_votacoes_proposicoes_etl_impl(csv_path, db)


def _run_votacoes_proposicoes_etl_impl(csv_path: str, db: Session) -> int:
    """Implementação interna do ETL votacoes_proposicoes.

    Args:
        csv_path: Caminho para o arquivo CSV
        db: Sessão de banco de dados

    Returns:
        Quantidade de registros carregados
    """
    # Extract
    raw_data = extract_votacoes_proposicoes_csv(csv_path)

    # Transform
    validated = transform_votacoes_proposicoes(raw_data, db)

    # Load
    count = load_votacoes_proposicoes(validated, db)

    logger.info(f"ETL votacoes_proposicoes concluído: {count} registros carregados")
    return count


# ==============================================================================
# ETL Orientações de Bancada (Fase 2, step 2.2)
# ==============================================================================

# Mapeamento de normalização de orientações
_ORIENTACAO_NORMALIZADA = {
    "sim": "Sim",
    "não": "Não",
    "nao": "Não",
    "liberado": "Liberado",
    "liberada": "Liberado",
    "obstrução": "Obstrução",
    "obstrucao": "Obstrução",
    "não informado": "Não informado",
    "nao informado": "Não informado",
}


def extract_orientacoes_csv(csv_path: str) -> list[dict]:
    """Extrai dados de orientações de bancada do arquivo CSV.

    Lê o CSV de orientações usando encoding UTF-8 e separador ';'
    (padrão Dados Abertos da Câmara).

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        Lista de dicionários com os dados brutos do CSV

    Raises:
        FileNotFoundError: Se o arquivo CSV não existir
    """
    path = Path(csv_path)
    if not path.exists():
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            data = list(reader)
            logger.info(f"Extraídos {len(data)} registros do CSV: {csv_path}")
            return data
    except Exception as e:
        logger.error(f"Erro ao ler CSV {csv_path}: {e}")
        raise


def transform_orientacoes(
    raw_data: list[dict],
    db: Session,
) -> list[OrientacaoCreate]:
    """Transforma dados brutos de orientações em schemas validados.

    Realiza:
    1. Parse de idVotacao (split no hífen para obter votacao_id numérico)
    2. Validação de FK votacao_id contra tabela votacoes (skip se não existe)
    3. Normalização do campo orientacao ("Sim", "Não", "Liberado", "Obstrução")
    4. Filtragem de registros com orientacao ou siglaBancada vazia

    Args:
        raw_data: Lista de dicionários com dados brutos do CSV
        db: Sessão de banco para validação de FK

    Returns:
        Lista de schemas OrientacaoCreate validados
    """
    validated = []
    skipped = 0

    # Cache de IDs existentes para evitar queries repetidas
    votacao_ids_cache: dict[int, bool] = {}

    for idx, record in enumerate(raw_data, 1):
        try:
            # 1. Parse idVotacao
            raw_id = record.get("idVotacao", "")
            try:
                votacao_id, votacao_id_original = _parse_votacao_id(raw_id)
            except (ValueError, TypeError):
                logger.warning(
                    f"Orientação {idx}: idVotacao inválido '{raw_id}', skipado"
                )
                skipped += 1
                continue

            # 2. Validar FK votacao_id
            if votacao_id not in votacao_ids_cache:
                stmt = select(Votacao).where(Votacao.id == votacao_id)
                exists = db.execute(stmt).scalar_one_or_none() is not None
                votacao_ids_cache[votacao_id] = exists

            if not votacao_ids_cache[votacao_id]:
                logger.warning(
                    f"Orientação {idx}: votacao_id {votacao_id} não encontrada "
                    f"em votacoes — registro skipado"
                )
                skipped += 1
                continue

            # 3. Extrair e validar siglaBancada
            sigla_bancada = (record.get("siglaBancada") or "").strip()
            if not sigla_bancada:
                logger.warning(
                    f"Orientação {idx}: siglaBancada vazia, skipado"
                )
                skipped += 1
                continue

            # 4. Normalizar orientacao
            orientacao_raw = (record.get("orientacao") or "").strip()
            if not orientacao_raw:
                logger.warning(
                    f"Orientação {idx}: orientacao vazia para bancada "
                    f"'{sigla_bancada}', skipado"
                )
                skipped += 1
                continue

            orientacao = _ORIENTACAO_NORMALIZADA.get(
                orientacao_raw.lower(), orientacao_raw
            )

            schema = OrientacaoCreate(
                votacao_id=votacao_id,
                votacao_id_original=votacao_id_original,
                sigla_bancada=sigla_bancada,
                orientacao=orientacao,
            )
            validated.append(schema)

        except ValidationError as e:
            logger.warning(f"Validação falhou para orientação {idx}: {e}")
            skipped += 1
        except Exception as e:
            logger.warning(f"Erro ao transformar orientação {idx}: {e}")
            skipped += 1

    logger.info(
        f"Transform orientacoes: {len(validated)} válidos, {skipped} skipados"
    )
    return validated


def load_orientacoes(
    records: list[OrientacaoCreate],
    db: Session,
) -> int:
    """Carrega orientações de bancada no banco de dados.

    Usa OrientacaoRepository.bulk_upsert para inserção/atualização
    idempotente via INSERT...ON CONFLICT.

    Args:
        records: Lista de schemas validados
        db: Sessão de banco de dados

    Returns:
        Quantidade de registros carregados
    """
    if not records:
        logger.info("Nenhuma orientação para carregar")
        return 0

    repo = OrientacaoRepository(db)
    count = repo.bulk_upsert(records)

    logger.info(f"Carregadas {count} orientações no banco")
    return count


def run_orientacoes_etl(
    csv_path: str,
    db: Session | None = None,
) -> int:
    """Executa o pipeline ETL para orientações de bancada.

    Orquestra extract → transform → load para o CSV votacoesOrientacoes.
    Step NÃO-CRÍTICO: falha gera warning mas não interrompe o pipeline.

    Args:
        csv_path: Caminho para o arquivo CSV de orientações
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Quantidade de registros carregados
    """
    logger.info(f"Iniciando ETL orientacoes: {csv_path}")

    if db is None:
        with get_db() as db:
            return _run_orientacoes_etl_impl(csv_path, db)
    else:
        return _run_orientacoes_etl_impl(csv_path, db)


def _run_orientacoes_etl_impl(csv_path: str, db: Session) -> int:
    """Implementação interna do ETL orientacoes.

    Args:
        csv_path: Caminho para o arquivo CSV
        db: Sessão de banco de dados

    Returns:
        Quantidade de registros carregados
    """
    # Extract
    raw_data = extract_orientacoes_csv(csv_path)

    # Transform
    validated = transform_orientacoes(raw_data, db)

    # Load
    count = load_orientacoes(validated, db)

    logger.info(f"ETL orientacoes concluído: {count} registros carregados")
    return count
