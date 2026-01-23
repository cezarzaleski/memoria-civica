"""Models SQLAlchemy para o domínio de Deputados.

Define a tabela deputados com campos essenciais para persistência
e relacionamentos com outros domínios.
"""

from sqlalchemy import Column, Integer, String

from src.shared.database import Base


class Deputado(Base):
    """Model SQLAlchemy para representar um deputado.

    Attributes:
        id: Identificador único do deputado (chave primária)
        nome: Nome completo do deputado
        partido: Sigla do partido político
        uf: Unidade federativa (estado) - 2 caracteres
        foto_url: URL para foto/avatar do deputado (opcional)
        email: Endereço de email do deputado (opcional)
    """

    __tablename__ = "deputados"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    partido = Column(String(50), nullable=False)
    uf = Column(String(2), nullable=False, index=True)
    foto_url = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return f"<Deputado(id={self.id}, nome='{self.nome}', partido='{self.partido}', uf='{self.uf}')>"
