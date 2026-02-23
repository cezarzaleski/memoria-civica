"""Pipeline ETL para o domínio de Gastos Parlamentares (CEAP)."""

import csv
import logging
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.deputados.models import Deputado
from src.shared.database import get_db
from src.shared.downloader import retry_with_backoff

from .repository import GastoRepository
from .schemas import GastoCreate

logger = logging.getLogger(__name__)

CANONICAL_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "idDeputado": ("idDeputado", "ideCadastro"),
    "ano": ("ano", "numAno"),
    "mes": ("mes", "numMes"),
    "tipoDespesa": ("tipoDespesa", "txtDescricao"),
    "tipoDocumento": ("tipoDocumento", "indTipoDocumento"),
    "dataDocumento": ("dataDocumento", "datEmissao"),
    "numDocumento": ("numDocumento", "txtNumero"),
    "valorDocumento": ("valorDocumento", "vlrDocumento"),
    "valorLiquido": ("valorLiquido", "vlrLiquido"),
    "valorGlosa": ("valorGlosa", "vlrGlosa"),
    "nomeFornecedor": ("nomeFornecedor", "txtFornecedor"),
    "cnpjCpfFornecedor": ("cnpjCpfFornecedor", "txtCNPJCPF"),
    "urlDocumento": ("urlDocumento",),
    "idDocumento": ("idDocumento", "ideDocumento"),
    "codLote": ("codLote", "numLote"),
    "parcela": ("parcela", "numParcela"),
}


def _normalize_text(value: object) -> str | None:
    """Converte valor textual para formato limpo (ou None)."""
    if value is None:
        return None

    normalized = str(value).strip()
    if normalized == "" or normalized.upper() == "NULL":
        return None
    return normalized


def safe_int(value: object) -> int | None:
    """Converte para inteiro quando possível; em caso contrário retorna None."""
    normalized = _normalize_text(value)
    if normalized is None:
        return None

    try:
        return int(normalized)
    except (TypeError, ValueError):
        return None


def parse_valor_brasileiro(value: object) -> Decimal:
    """Normaliza valores monetários em formato brasileiro para Decimal."""
    if value is None:
        return Decimal("0")

    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))

    normalized = str(value).strip()
    if normalized == "" or normalized.upper() == "NULL":
        return Decimal("0")

    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")

    try:
        return Decimal(normalized).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        logger.warning("Valor monetário inválido encontrado no CSV: %r. Será convertido para 0.", value)
        return Decimal("0")


def parse_data_documento(value: object) -> date | None:
    """Converte data textual para `date` aceitando formatos da CEAP."""
    normalized = _normalize_text(value)
    if normalized is None:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        logger.warning("Data de documento inválida encontrada no CSV: %r. Será convertida para None.", value)
        return None


def _resolve_column_mapping(headers: set[str]) -> dict[str, str]:
    """Resolve mapeamento de colunas CSV para o contrato canônico interno."""
    missing_columns: list[str] = []
    column_mapping: dict[str, str] = {}

    for canonical_name, aliases in CANONICAL_COLUMN_ALIASES.items():
        matched_column = next((column for column in aliases if column in headers), None)
        if matched_column is None:
            expected = " ou ".join(aliases)
            missing_columns.append(f"{canonical_name} ({expected})")
            continue
        column_mapping[canonical_name] = matched_column

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV de gastos inválido. Colunas obrigatórias ausentes: {missing}")

    return column_mapping


def _to_canonical_record(record: Mapping[str, object], mapping: Mapping[str, str]) -> dict[str, object]:
    """Converte linha do CSV para o dicionário canônico esperado no transform."""
    return {canonical_name: record.get(csv_column_name) for canonical_name, csv_column_name in mapping.items()}


def extract_gastos_csv(csv_path: str) -> list[dict]:
    """Extrai registros do CSV CEAP e valida contrato de colunas."""
    path = Path(csv_path)
    if not path.exists():
        logger.error("Arquivo CSV não encontrado: %s", csv_path)
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        with open(path, encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=";")
            fieldnames = [field.strip() for field in (reader.fieldnames or []) if field]
            reader.fieldnames = fieldnames
            headers = set(fieldnames)
            mapping = _resolve_column_mapping(headers)

            records = [_to_canonical_record(record, mapping) for record in reader]
            logger.info("Extraídos %d registros do CSV de gastos: %s", len(records), csv_path)
            return records
    except Exception as exc:
        logger.error("Erro ao ler CSV de gastos %s: %s", csv_path, exc)
        raise


def _load_valid_deputado_ids(db: Session | None) -> set[int]:
    """Retorna o conjunto de IDs de deputados disponíveis para validação de FK."""
    if db is None:
        return set()

    stmt = select(Deputado.id)
    return set(db.execute(stmt).scalars().all())


def transform_gastos(raw_data: list[dict], db: Session | None = None) -> list[GastoCreate]:
    """Transforma dados brutos CEAP em schemas `GastoCreate` validados."""
    validated: list[GastoCreate] = []
    skipped = 0

    valid_deputado_ids = _load_valid_deputado_ids(db)
    should_validate_fk = db is not None

    for index, record in enumerate(raw_data, 1):
        try:
            deputado_id = safe_int(record.get("idDeputado"))
            if should_validate_fk and deputado_id is not None and deputado_id not in valid_deputado_ids:
                logger.warning(
                    "Registro %d: deputado_id %s não existe na base de deputados; valor será definido como NULL.",
                    index,
                    deputado_id,
                )
                deputado_id = None

            schema = GastoCreate(
                deputado_id=deputado_id,
                ano=safe_int(record.get("ano")),
                mes=safe_int(record.get("mes")),
                tipo_despesa=_normalize_text(record.get("tipoDespesa")) or "",
                tipo_documento=_normalize_text(record.get("tipoDocumento")),
                data_documento=parse_data_documento(record.get("dataDocumento")),
                numero_documento=_normalize_text(record.get("numDocumento")),
                valor_documento=parse_valor_brasileiro(record.get("valorDocumento")),
                valor_liquido=parse_valor_brasileiro(record.get("valorLiquido")),
                valor_glosa=parse_valor_brasileiro(record.get("valorGlosa")),
                nome_fornecedor=_normalize_text(record.get("nomeFornecedor")),
                cnpj_cpf_fornecedor=_normalize_text(record.get("cnpjCpfFornecedor")),
                url_documento=_normalize_text(record.get("urlDocumento")),
                cod_documento=safe_int(record.get("idDocumento")),
                cod_lote=safe_int(record.get("codLote")),
                parcela=safe_int(record.get("parcela")) or 0,
            )
            validated.append(schema)
        except ValidationError as exc:
            logger.warning("Validação falhou para gasto %d: %s", index, exc)
            skipped += 1
        except Exception as exc:
            logger.warning("Erro ao transformar gasto %d: %s", index, exc)
            skipped += 1

    logger.info("Transformados %d gastos (skipped: %d)", len(validated), skipped)
    return validated


def load_gastos(gastos: list[GastoCreate], db: Session | None = None) -> int:
    """Carrega gastos validados no banco via `GastoRepository.bulk_upsert`."""
    if not gastos:
        logger.info("Nenhum gasto para carregar")
        return 0

    if db is None:
        with get_db() as db_session:
            repository = GastoRepository(db_session)
            count = repository.bulk_upsert(gastos)
    else:
        repository = GastoRepository(db)
        count = repository.bulk_upsert(gastos)

    logger.info("Carregados %d gastos no banco de dados", count)
    return count


@retry_with_backoff(max_retries=3)
def _run_gastos_etl_impl(csv_path: str, db: Session) -> int:
    """Implementação interna do pipeline ETL de gastos."""
    raw_data = extract_gastos_csv(csv_path)
    validated_gastos = transform_gastos(raw_data, db)
    return load_gastos(validated_gastos, db)


def run_gastos_etl(csv_path: str, db: Session | None = None) -> int:
    """Executa o pipeline ETL completo de gastos (extract → transform → load)."""
    if not Path(csv_path).exists():
        logger.error("Arquivo CSV não encontrado: %s", csv_path)
        return 1

    try:
        logger.info("Iniciando ETL de gastos: %s", csv_path)
        if db is None:
            with get_db() as db_session:
                count = _run_gastos_etl_impl(csv_path, db_session)
        else:
            count = _run_gastos_etl_impl(csv_path, db)

        logger.info("ETL de gastos concluído: %d registros processados", count)
        return 0
    except Exception as exc:
        logger.error("ETL de gastos falhou: %s", exc)
        return 1
