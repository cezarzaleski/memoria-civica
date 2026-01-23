"""Pipeline ETL para o domínio de Deputados.

Orquestra a leitura de CSV, validação de dados e persistência
em banco de dados, com logging e tratamento de erros.
"""

import csv
import logging
from pathlib import Path

from pydantic import ValidationError

from src.shared.database import get_db

from .repository import DeputadoRepository
from .schemas import DeputadoCreate

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def extract_deputados_csv(csv_path: str) -> list[dict]:
    """Extrai dados de deputados do arquivo CSV.

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
        >>> data = extract_deputados_csv("data/deputados.csv")
        >>> len(data) > 0
        True
        >>> "nome" in data[0]
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


def transform_deputados(raw_data: list[dict]) -> list[DeputadoCreate]:
    """Transforma dados brutos em schemas Pydantic validados.

    Valida cada registro usando DeputadoCreate schema, capturando
    erros de validação e logando warnings para dados inválidos.

    Args:
        raw_data: Lista de dicionários com dados brutos do CSV

    Returns:
        Lista de schemas DeputadoCreate validados

    Examples:
        >>> raw = [
        ...     {
        ...         "uri": "https://...",
        ...         "nome": "João Silva",
        ...         "idLegislaturaInicial": "57",
        ...         "ufNascimento": "SP"
        ...     }
        ... ]
        >>> transformed = transform_deputados(raw)
        >>> len(transformed) > 0
        True
    """
    validated = []
    skipped = 0

    for idx, record in enumerate(raw_data, 1):
        try:
            # Mapear campos CSV para o schema DeputadoCreate
            # O CSV pode ter campos diferentes, então extrair apenas necessários
            deputy_id = int(record.get("uri", "").split("/")[-1]) if record.get("uri") else idx

            # Tentar extrair partido de urlRedeSocial ou usar padrão
            # (no CSV original, partido vem do bio/history, aqui usar placeholder)
            partido = record.get("partido", "INDEP")
            uf = record.get("ufNascimento", "XX")

            schema = DeputadoCreate(
                id=deputy_id,
                nome=record.get("nome", "").strip(),
                partido=partido.strip() if partido else "INDEP",
                uf=uf.strip() if uf and len(uf) >= 2 else "XX",
                foto_url=record.get("foto_url"),
                email=record.get("email"),
            )
            validated.append(schema)

        except ValidationError as e:
            logger.warning(f"Validação falhou para registro {idx}: {e}")
            skipped += 1
        except Exception as e:
            logger.warning(f"Erro ao transformar registro {idx}: {e}")
            skipped += 1

    logger.info(f"Transformados {len(validated)} registros (skipped: {skipped})")
    return validated


def load_deputados(
    deputados: list[DeputadoCreate],
    db=None,
) -> int:
    """Carrega deputados validados no banco de dados.

    Usa bulk_upsert do repository para inserir/atualizar eficientemente,
    garantindo idempotência (pode ser chamado múltiplas vezes).

    Args:
        deputados: Lista de schemas validados
        db: Sessão de banco opcional (se None, usa get_db())

    Returns:
        Quantidade de deputados inseridos/atualizados

    Examples:
        >>> from src.deputados.schemas import DeputadoCreate
        >>> deps = [
        ...     DeputadoCreate(id=1, nome="João", partido="PT", uf="SP"),
        ... ]
        >>> count = load_deputados(deps)
        >>> count
        1
    """
    if not deputados:
        logger.info("Nenhum deputado para carregar")
        return 0

    # Se db não foi fornecido, usar get_db()
    if db is None:
        with get_db() as db:
            repo = DeputadoRepository(db)
            count = repo.bulk_upsert(deputados)
    else:
        repo = DeputadoRepository(db)
        count = repo.bulk_upsert(deputados)

    logger.info(f"Carregados {count} deputados no banco de dados")
    return count


def run_deputados_etl(csv_path: str, db: object | None = None) -> int:
    """Executa o pipeline ETL completo para deputados.

    Orquestra extract → transform → load em uma única chamada.

    Args:
        csv_path: Caminho para o arquivo CSV
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Exit code (0 sucesso, 1 falha)

    Examples:
        >>> exit_code = run_deputados_etl("data/deputados.csv")
        >>> exit_code
        0
    """
    try:
        logger.info(f"Iniciando ETL de deputados: {csv_path}")

        # Extract
        raw_data = extract_deputados_csv(csv_path)

        # Transform
        validated_deputados = transform_deputados(raw_data)

        # Load
        count = load_deputados(validated_deputados, db)

        logger.info(f"ETL de deputados concluído: {count} registros persistidos")
        return 0

    except Exception as e:
        logger.error(f"ETL de deputados falhou: {e}")
        return 1
