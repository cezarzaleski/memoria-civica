"""Testes para ETL de classificação cívica de proposições.

Valida o pipeline completo de classificação: seed de categorias,
busca de proposições, classificação via regex, e persistência.
Testes unitários usam SQLite in-memory com inserção ORM direta.
Testes de integração (bulk_upsert/seed) requerem PostgreSQL.
"""

import pytest
from sqlalchemy.exc import OperationalError

from src.classificacao.engine import ClassificadorCivico
from src.classificacao.etl import _run_classificacao_etl_impl, run_classificacao_etl
from src.classificacao.models import CategoriaCivica, ProposicaoCategoria
from src.classificacao.patterns import CIVIC_PATTERNS
from src.classificacao.repository import CATEGORIAS_SEED
from src.proposicoes.models import Proposicao


def _seed_categorias_orm(db_session) -> dict[str, int]:
    """Helper: insere categorias via ORM (compatível com SQLite).

    Returns:
        Mapa de codigo → id das categorias inseridas
    """
    codigo_para_id = {}
    for cat_data in CATEGORIAS_SEED:
        cat = CategoriaCivica(
            codigo=cat_data["codigo"],
            nome=cat_data["nome"],
            descricao=cat_data.get("descricao"),
            icone=cat_data.get("icone"),
        )
        db_session.add(cat)
    db_session.flush()

    for cat in db_session.query(CategoriaCivica).all():
        codigo_para_id[cat.codigo] = cat.id
    db_session.commit()

    return codigo_para_id


def _create_proposicao(db_session, prop_id: int, ementa: str, tipo: str = "PL") -> Proposicao:
    """Helper: cria uma proposição no banco via ORM."""
    prop = Proposicao(
        id=prop_id,
        tipo=tipo,
        numero=prop_id,
        ano=2024,
        ementa=ementa,
    )
    db_session.add(prop)
    db_session.flush()
    return prop


class TestRunClassificacaoEtlLogic:
    """Testes da lógica de classificação (sem pg_insert, compatível com SQLite)."""

    def test_classifica_proposicao_gastos_publicos(self, db_session):
        """Test: proposição com ementa sobre crédito suplementar é classificada como GASTOS_PUBLICOS."""
        _seed_categorias_orm(db_session)
        _create_proposicao(db_session, 1, "Abre crédito suplementar ao Orçamento Geral da União")
        db_session.commit()

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar("Abre crédito suplementar ao Orçamento Geral da União")

        assert len(matches) >= 1
        codigos = {m.categoria_codigo for m in matches}
        assert "GASTOS_PUBLICOS" in codigos

    def test_classifica_proposicao_direitos_sociais(self, db_session):
        """Test: proposição sobre saúde pública é classificada como DIREITOS_SOCIAIS."""
        _seed_categorias_orm(db_session)
        _create_proposicao(db_session, 2, "Dispõe sobre o fortalecimento da saúde pública no Brasil")
        db_session.commit()

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar("Dispõe sobre o fortalecimento da saúde pública no Brasil")

        assert len(matches) >= 1
        codigos = {m.categoria_codigo for m in matches}
        assert "DIREITOS_SOCIAIS" in codigos

    def test_classifica_proposicao_meio_ambiente(self, db_session):
        """Test: proposição sobre licenciamento ambiental é classificada como MEIO_AMBIENTE."""
        _seed_categorias_orm(db_session)
        _create_proposicao(db_session, 3, "Altera regras de licenciamento ambiental para obras de infraestrutura")
        db_session.commit()

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar(
            "Altera regras de licenciamento ambiental para obras de infraestrutura"
        )

        assert len(matches) >= 1
        codigos = {m.categoria_codigo for m in matches}
        assert "MEIO_AMBIENTE" in codigos

    def test_proposicao_sem_ementa_nao_gera_match(self, db_session):
        """Test: proposição sem ementa não gera classificação."""
        _seed_categorias_orm(db_session)

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar("")

        assert matches == []

    def test_proposicao_sem_match_nao_gera_classificacao(self, db_session):
        """Test: proposição com ementa genérica não gera classificação."""
        _seed_categorias_orm(db_session)

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar("Homenageia o Dia Nacional do Xadrez")

        assert matches == []

    def test_proposicao_com_multiplas_categorias(self, db_session):
        """Test: proposição com ementa que matcha múltiplas categorias retorna todas."""
        _seed_categorias_orm(db_session)

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        # Ementa que menciona crédito suplementar E meio ambiente
        matches = classificador.classificar(
            "Abre crédito suplementar para programa de proteção ambiental"
        )

        codigos = {m.categoria_codigo for m in matches}
        assert "GASTOS_PUBLICOS" in codigos
        assert "MEIO_AMBIENTE" in codigos

    def test_delete_by_origem_preserva_llm(self, db_session):
        """Test: delete_by_origem('regra') preserva classificações 'llm'."""
        _seed_categorias_orm(db_session)
        _create_proposicao(db_session, 10, "Ementa teste")

        # Inserir classificações de ambas origens via ORM
        cat_id = db_session.query(CategoriaCivica).first().id
        pcs = [
            ProposicaoCategoria(proposicao_id=10, categoria_id=cat_id, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=10, categoria_id=cat_id + 1, origem="llm", confianca=0.85),
        ]
        db_session.add_all(pcs)
        db_session.commit()

        from src.classificacao.repository import ProposicaoCategoriaRepository

        pc_repo = ProposicaoCategoriaRepository(db_session)
        deleted = pc_repo.delete_by_origem("regra")

        assert deleted == 1
        restantes = pc_repo.get_by_proposicao(10)
        assert len(restantes) == 1
        assert restantes[0].origem == "llm"


class TestRunClassificacaoEtlIntegration:
    """Testes de integração do ETL completo (requerem PostgreSQL para ON CONFLICT)."""

    @pytest.mark.integration
    def test_run_classificacao_etl_end_to_end(self, db_session):
        """Test: ETL completo classifica proposições e persiste resultados."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        # Criar proposições com ementas classificáveis
        _create_proposicao(db_session, 1, "Abre crédito suplementar ao Orçamento da União")
        _create_proposicao(db_session, 2, "Dispõe sobre o fortalecimento da saúde pública")
        _create_proposicao(db_session, 3, "Homenageia o Dia Nacional do Xadrez")  # Sem match
        db_session.commit()

        count = _run_classificacao_etl_impl(db_session)

        # Pelo menos 2 proposições devem gerar classificações
        assert count >= 2

        # Verificar persistência
        all_pcs = db_session.query(ProposicaoCategoria).all()
        assert len(all_pcs) >= 2
        assert all(pc.origem == "regra" for pc in all_pcs)
        assert all(pc.confianca == 1.0 for pc in all_pcs)

    @pytest.mark.integration
    def test_run_classificacao_etl_idempotente(self, db_session):
        """Test: executar ETL 2x não duplica classificações."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        _create_proposicao(db_session, 1, "Abre crédito suplementar ao Orçamento da União")
        db_session.commit()

        count1 = _run_classificacao_etl_impl(db_session)
        count2 = _run_classificacao_etl_impl(db_session)

        assert count1 == count2

        all_pcs = db_session.query(ProposicaoCategoria).all()
        assert len(all_pcs) == count1

    @pytest.mark.integration
    def test_run_classificacao_etl_sem_proposicoes(self, db_session):
        """Test: ETL retorna 0 quando não há proposições."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        count = _run_classificacao_etl_impl(db_session)
        assert count == 0

    @pytest.mark.integration
    def test_run_classificacao_etl_preserva_llm(self, db_session):
        """Test: ETL limpa classificações 'regra' mas preserva 'llm'."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        _create_proposicao(db_session, 1, "Abre crédito suplementar ao Orçamento da União")
        db_session.commit()

        # Primeira execução
        _run_classificacao_etl_impl(db_session)

        # Inserir classificação LLM manualmente
        cat = db_session.query(CategoriaCivica).first()
        llm_pc = ProposicaoCategoria(
            proposicao_id=1,
            categoria_id=cat.id,
            origem="llm",
            confianca=0.9,
        )
        db_session.add(llm_pc)
        db_session.commit()

        # Segunda execução do ETL
        _run_classificacao_etl_impl(db_session)

        # Verificar que LLM foi preservada
        llm_records = (
            db_session.query(ProposicaoCategoria)
            .filter(ProposicaoCategoria.origem == "llm")
            .all()
        )
        assert len(llm_records) == 1
        assert llm_records[0].confianca == 0.9


class TestRunClassificacaoEtlEdgeCases:
    """Testes de casos extremos para o ETL de classificação."""

    def test_classificacao_deterministica(self, db_session):
        """Test: mesma ementa sempre produz mesmo resultado de classificação."""
        _seed_categorias_orm(db_session)

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        ementa = "Altera a legislação sobre segurança pública e crimes hediondos"

        matches1 = classificador.classificar(ementa)
        matches2 = classificador.classificar(ementa)

        assert len(matches1) == len(matches2)
        codigos1 = [m.categoria_codigo for m in matches1]
        codigos2 = [m.categoria_codigo for m in matches2]
        assert codigos1 == codigos2

    def test_proposicao_com_ementa_none_skipada(self, db_session):
        """Test: proposição com ementa None não é classificada."""
        _seed_categorias_orm(db_session)

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar(None)

        assert matches == []

    def test_cada_categoria_tem_pelo_menos_um_match(self):
        """Test: cada categoria em CIVIC_PATTERNS tem padrões que matcham alguma ementa."""
        classificador = ClassificadorCivico(CIVIC_PATTERNS)

        ementas_por_categoria = {
            "GASTOS_PUBLICOS": "Abre crédito suplementar ao Orçamento",
            "TRIBUTACAO_AUMENTO": "Aumenta a alíquota do imposto sobre renda",
            "TRIBUTACAO_ISENCAO": "Concede isenção tributária para pequenas empresas",
            "BENEFICIOS_CATEGORIAS": "Reajuste salarial para servidores públicos federais",
            "DIREITOS_SOCIAIS": "Ampliação do programa Bolsa Família",
            "SEGURANCA_JUSTICA": "Altera o código penal sobre crimes hediondos",
            "MEIO_AMBIENTE": "Regulamenta o licenciamento ambiental",
            "REGULACAO_ECONOMICA": "Regula o mercado financeiro e taxa de juros",
            "POLITICA_INSTITUCIONAL": "Dispõe sobre reforma eleitoral e fundo eleitoral",
        }

        for categoria, ementa in ementas_por_categoria.items():
            matches = classificador.classificar(ementa)
            codigos = {m.categoria_codigo for m in matches}
            assert categoria in codigos, (
                f"Categoria {categoria} não matchou ementa: {ementa}"
            )

    def test_confianca_sempre_1_para_regra(self, db_session):
        """Test: classificações por regra sempre têm confiança 1.0."""
        _seed_categorias_orm(db_session)

        classificador = ClassificadorCivico(CIVIC_PATTERNS)
        matches = classificador.classificar("Abre crédito suplementar ao Orçamento da União")

        assert len(matches) >= 1
        for match in matches:
            assert match.confianca == 1.0

    def test_run_classificacao_etl_com_db_none_usa_get_db(self):
        """Test: run_classificacao_etl(db=None) tenta usar get_db()."""
        # Sem um banco real configurado via get_db(), deve levantar exceção
        # do SQLAlchemy (tabelas não existem no banco default)
        with pytest.raises(OperationalError):
            run_classificacao_etl(db=None)
