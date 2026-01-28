"""Testes para schemas Pydantic do domínio de Deputados.

Validam a criação de instâncias de DeputadoCreate e DeputadoRead,
incluindo validação de constraints e campo opcionais.
"""

import pytest
from pydantic import ValidationError

from src.deputados.schemas import DeputadoCreate, DeputadoRead


class TestDeputadoCreate:
    """Testes para schema DeputadoCreate."""

    def test_create_valid_deputado(self):
        """Test: DeputadoCreate aceita dados válidos."""
        deputado = DeputadoCreate(
            id=123,
            nome="João Silva",
            partido="PT",
            uf="SP",
        )
        assert deputado.id == 123
        assert deputado.nome == "João Silva"
        assert deputado.partido == "PT"
        assert deputado.uf == "SP"
        assert deputado.foto_url is None
        assert deputado.email is None

    def test_create_with_optional_fields(self):
        """Test: DeputadoCreate aceita campos opcionais."""
        deputado = DeputadoCreate(
            id=456,
            nome="Maria Santos",
            partido="PDT",
            uf="RJ",
            foto_url="https://example.com/maria.jpg",
            email="maria@camara.leg.br",
        )
        assert deputado.foto_url == "https://example.com/maria.jpg"
        assert deputado.email == "maria@camara.leg.br"

    def test_create_rejects_invalid_uf_length(self):
        """Test: DeputadoCreate rejeita UF inválida (!=2 chars)."""
        # UF muito curta
        with pytest.raises(ValidationError) as exc_info:
            DeputadoCreate(
                id=789,
                nome="Pedro",
                partido="PSDB",
                uf="S",  # Deve ter 2 caracteres
            )
        assert "at least 2 characters" in str(exc_info.value).lower()

        # UF muito longa
        with pytest.raises(ValidationError) as exc_info:
            DeputadoCreate(
                id=790,
                nome="Pedro",
                partido="PSDB",
                uf="SPP",  # Deve ter exatamente 2 caracteres
            )
        assert "at most 2 characters" in str(exc_info.value).lower()

    def test_create_rejects_empty_nome(self):
        """Test: DeputadoCreate rejeita nome vazio."""
        with pytest.raises(ValidationError):
            DeputadoCreate(
                id=800,
                nome="",  # Nome não pode ser vazio
                partido="PT",
                uf="SP",
            )

    def test_create_rejects_empty_partido(self):
        """Test: DeputadoCreate rejeita partido vazio."""
        with pytest.raises(ValidationError):
            DeputadoCreate(
                id=801,
                nome="Ana",
                partido="",  # Partido não pode ser vazio
                uf="SP",
            )

    def test_create_with_missing_required_fields(self):
        """Test: DeputadoCreate rejeita quando faltam campos obrigatórios."""
        with pytest.raises(ValidationError):
            DeputadoCreate(
                id=802,
                nome="Carlos",
                partido="PMDB",
                # Falta uf
            )

    def test_create_accepts_optional_fields_as_none(self):
        """Test: DeputadoCreate aceita campos opcionais como None."""
        deputado = DeputadoCreate(
            id=803,
            nome="Bruno",
            partido="PP",
            uf="BA",
            foto_url=None,
            email=None,
        )
        assert deputado.foto_url is None
        assert deputado.email is None

    def test_create_validates_email_format(self):
        """Test: DeputadoCreate com email válido."""
        deputado = DeputadoCreate(
            id=804,
            nome="Fernanda",
            partido="PODEMOS",
            uf="MG",
            email="fernanda@camara.leg.br",
        )
        assert deputado.email == "fernanda@camara.leg.br"

    def test_create_from_attributes(self):
        """Test: DeputadoCreate pode ser criado de model com from_attributes."""
        # Simular um modelo ORM
        class MockDeputado:
            id = 805
            nome = "Gustavo"
            partido = "PRB"
            uf = "RS"
            foto_url = None
            email = None

        mock = MockDeputado()
        deputado = DeputadoCreate.model_validate(mock)
        assert deputado.id == 805
        assert deputado.nome == "Gustavo"


class TestDeputadoRead:
    """Testes para schema DeputadoRead."""

    def test_read_valid_deputado(self):
        """Test: DeputadoRead aceita dados válidos."""
        deputado = DeputadoRead(
            id=900,
            nome="Hélio Costa",
            partido="MDB",
            uf="ES",
        )
        assert deputado.id == 900
        assert deputado.nome == "Hélio Costa"
        assert deputado.partido == "MDB"
        assert deputado.uf == "ES"

    def test_read_with_optional_fields(self):
        """Test: DeputadoRead com campos opcionais."""
        deputado = DeputadoRead(
            id=901,
            nome="Iris Silva",
            partido="União",
            uf="SC",
            foto_url="https://example.com/iris.jpg",
            email="iris@camara.leg.br",
        )
        assert deputado.foto_url == "https://example.com/iris.jpg"
        assert deputado.email == "iris@camara.leg.br"

    def test_read_from_attributes(self):
        """Test: DeputadoRead pode ser criado de model com from_attributes."""
        # Simular um modelo ORM
        class MockDeputado:
            id = 902
            nome = "João Neves"
            partido = "AVANTE"
            uf = "GO"
            foto_url = None
            email = None

        mock = MockDeputado()
        deputado = DeputadoRead.model_validate(mock)
        assert deputado.id == 902
        assert deputado.nome == "João Neves"
