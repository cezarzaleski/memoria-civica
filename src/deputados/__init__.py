"""Domínio de Deputados.

Módulo que encapsula toda a lógica de negócio relacionada a deputados,
incluindo models, schemas, repository e ETL.
"""

from .models import Deputado
from .repository import DeputadoRepository
from .schemas import DeputadoCreate, DeputadoRead

__all__ = [
    "Deputado",
    "DeputadoCreate",
    "DeputadoRead",
    "DeputadoRepository",
]
