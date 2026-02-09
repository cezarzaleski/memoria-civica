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
from .repository import VotacaoRepository, VotoRepository
from .schemas import VotacaoCreate, VotoCreate

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
        with open(path, encoding="utf-8") as f:
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
        with open(path, encoding="utf-8") as f:
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

            # Data/hora do registro
            data_hora_str = record.get("dataHoraRegistro", "").strip()

            # Resultado: usar aprovacao (1/0) ou derivar da descrição
            aprovacao = record.get("aprovacao", "")
            descricao = record.get("descricao", "").strip()
            if aprovacao == "1":
                resultado = "APROVADO"
            elif aprovacao == "0":
                resultado = "REJEITADO"
            elif "aprovad" in descricao.lower():
                resultado = "APROVADO"
            elif "rejeitad" in descricao.lower():
                resultado = "REJEITADO"
            else:
                resultado = descricao[:20] if descricao else "INDEFINIDO"

            # Parse datetime
            if data_hora_str:
                try:
                    data_hora = datetime.fromisoformat(data_hora_str)
                except ValueError:
                    logger.warning(f"Votação {idx}: data_hora inválida '{data_hora_str}'")
                    skipped += 1
                    continue
            else:
                logger.warning(f"Votação {idx}: data_hora vazia")
                skipped += 1
                continue

            # Skip votações sem proposição associada
            if proposicao_id == 0:
                logger.debug(f"Votação {idx}: sem proposicao_id associada, pulando")
                skipped += 1
                continue

            # Validar FK proposicao_id se db foi fornecido
            if db is not None and proposicao_id > 0:
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
