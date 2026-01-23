"""Pipeline ETL para o domínio de Proposições.

Orquestra a leitura de CSV, validação de dados e persistência
em banco de dados, com logging e tratamento de erros.
"""

import csv
import logging
from pathlib import Path

from pydantic import ValidationError

from src.shared.database import get_db

from .repository import ProposicaoRepository
from .schemas import ProposicaoCreate

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def extract_proposicoes_csv(csv_path: str) -> list[dict]:
    """Extrai dados de proposições do arquivo CSV.

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
        >>> data = extract_proposicoes_csv("data/proposicoes.csv")
        >>> len(data) > 0
        True
        >>> "tipo" in data[0]
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


def transform_proposicoes(raw_data: list[dict]) -> list[ProposicaoCreate]:
    """Transforma dados brutos em schemas Pydantic validados.

    Valida cada registro usando ProposicaoCreate schema, capturando
    erros de validação e logando warnings para dados inválidos.
    Proposições órfãs (sem autor válido) são aceitas com warning.

    Args:
        raw_data: Lista de dicionários com dados brutos do CSV

    Returns:
        Lista de schemas ProposicaoCreate validados

    Examples:
        >>> raw = [
        ...     {
        ...         "id": "1",
        ...         "tipo": "PL",
        ...         "numero": "123",
        ...         "ano": "2024",
        ...         "ementa": "Lei de educação",
        ...         "autor_id": "456"
        ...     }
        ... ]
        >>> transformed = transform_proposicoes(raw)
        >>> len(transformed) > 0
        True
    """
    validated = []
    skipped = 0

    for idx, record in enumerate(raw_data, 1):
        try:
            # Extrair e validar campos
            prop_id = int(record.get("id", idx)) if record.get("id") else idx
            tipo = record.get("tipo", "PL").upper().strip()
            numero = int(record.get("numero", 0)) if record.get("numero") else 0
            ano = int(record.get("ano", 2024)) if record.get("ano") else 2024
            ementa = record.get("ementa", "").strip()
            autor_id_str = record.get("autor_id", "").strip()

            # Se autor_id não é válido, logar warning mas aceitar a proposição
            if autor_id_str and autor_id_str != "NULL":
                if autor_id_str.isdigit():
                    autor_id = int(autor_id_str)
                else:
                    logger.warning(f"Proposição {idx}: autor_id inválido '{autor_id_str}', será NULL")
                    autor_id = None
            else:
                autor_id = None

            schema = ProposicaoCreate(
                id=prop_id,
                tipo=tipo,
                numero=numero,
                ano=ano,
                ementa=ementa,
                autor_id=autor_id,
            )
            validated.append(schema)

        except ValidationError as e:
            logger.warning(f"Validação falhou para proposição {idx}: {e}")
            skipped += 1
        except Exception as e:
            logger.warning(f"Erro ao transformar proposição {idx}: {e}")
            skipped += 1

    logger.info(f"Transformadas {len(validated)} proposições (skipped: {skipped})")
    return validated


def load_proposicoes(
    proposicoes: list[ProposicaoCreate],
    db=None,
) -> int:
    """Carrega proposições validadas no banco de dados.

    Usa bulk_upsert do repository para inserir/atualizar eficientemente,
    garantindo idempotência (pode ser chamado múltiplas vezes).

    Args:
        proposicoes: Lista de schemas validados
        db: Sessão de banco opcional (se None, usa get_db())

    Returns:
        Quantidade de proposições inseridas/atualizadas

    Examples:
        >>> from src.proposicoes.schemas import ProposicaoCreate, TipoProposicao
        >>> props = [
        ...     ProposicaoCreate(
        ...         id=1, tipo=TipoProposicao.PL, numero=123,
        ...         ano=2024, ementa="Lei de educação"
        ...     ),
        ... ]
        >>> count = load_proposicoes(props)
        >>> count
        1
    """
    if not proposicoes:
        logger.info("Nenhuma proposição para carregar")
        return 0

    # Se db não foi fornecido, usar get_db()
    if db is None:
        with get_db() as db:
            repo = ProposicaoRepository(db)
            count = repo.bulk_upsert(proposicoes)
    else:
        repo = ProposicaoRepository(db)
        count = repo.bulk_upsert(proposicoes)

    logger.info(f"Carregadas {count} proposições no banco de dados")
    return count


def run_proposicoes_etl(csv_path: str, db: object | None = None) -> int:
    """Executa o pipeline ETL completo para proposições.

    Orquestra extract → transform → load em uma única chamada.

    Args:
        csv_path: Caminho para o arquivo CSV
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Exit code (0 sucesso, 1 falha)

    Examples:
        >>> exit_code = run_proposicoes_etl("data/proposicoes.csv")
        >>> exit_code
        0
    """
    try:
        logger.info(f"Iniciando ETL de proposições: {csv_path}")

        # Extract
        raw_data = extract_proposicoes_csv(csv_path)

        # Transform
        validated_proposicoes = transform_proposicoes(raw_data)

        # Load
        count = load_proposicoes(validated_proposicoes, db)

        logger.info(f"ETL de proposições concluído: {count} registros persistidos")
        return 0

    except Exception as e:
        logger.error(f"ETL de proposições falhou: {e}")
        return 1
