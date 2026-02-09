"""Models SQLAlchemy para o domínio de Proposições.

Define a tabela proposicoes com campos essenciais para persistência
e relacionamentos com outros domínios (Deputados como autores).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.shared.database import Base


class Proposicao(Base):
    """Model SQLAlchemy para representar uma proposição legislativa.

    Uma proposição representa um projeto de lei, PEC, MP ou outra matéria
    legislativa que é votada no Plenário. Pode ter um autor (deputado) ou
    ser orfã (autor_id NULL).

    Attributes:
        id: Identificador único da proposição (chave primária)
        tipo: Tipo da proposição (PL, PEC, MP, PLP, PDC, etc)
        numero: Número sequencial da proposição
        ano: Ano de apresentação da proposição
        ementa: Descrição/ementa da proposição
        autor_id: ID do deputado autor (FK para deputados.id, nullable)
        autor: Relacionamento com Deputado (lazy loading)
    """

    __tablename__ = "proposicoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False, index=True)
    numero = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    ementa = Column(Text, nullable=False)
    autor_id = Column(Integer, ForeignKey("deputados.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relacionamento com Deputado (back_populates requer mudança em Deputado)
    autor = relationship("Deputado", foreign_keys=[autor_id])

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return (
            f"<Proposicao(id={self.id}, tipo='{self.tipo}', "
            f"numero={self.numero}, ano={self.ano}, autor_id={self.autor_id})>"
        )
