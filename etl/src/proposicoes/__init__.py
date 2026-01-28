"""Domínio de Proposições.

Módulo que encapsula modelos, schemas, repositório e ETL
para o domínio de proposições legislativas.
"""

from .models import Proposicao
from .repository import ProposicaoRepository
from .schemas import ProposicaoCreate, ProposicaoRead, TipoProposicao

__all__ = [
    "Proposicao",
    "ProposicaoCreate",
    "ProposicaoRead",
    "ProposicaoRepository",
    "TipoProposicao",
]
