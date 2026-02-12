"""Engine de classificação cívica de proposições legislativas.

Aplica padrões regex contra ementas de proposições para classificá-las
em categorias de impacto cívico. A engine é determinística (mesmo input
sempre produz mesmo output) e stateless após inicialização.
"""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CategoriaMatch:
    """Resultado de um match de classificação.

    Attributes:
        categoria_codigo: Código da categoria (ex: "GASTOS_PUBLICOS")
        padrao_matchado: O padrão regex original que deu match
        confianca: Nível de confiança do match (1.0 para regra)
    """

    categoria_codigo: str
    padrao_matchado: str
    confianca: float = 1.0


@dataclass
class _CompiledCategory:
    """Categoria com padrões pré-compilados para performance."""

    codigo: str
    patterns: list[tuple[re.Pattern[str], str]] = field(default_factory=list)


class ClassificadorCivico:
    """Engine de classificação de proposições por categorias cívicas.

    Recebe um dicionário de padrões regex por categoria e os pré-compila
    na inicialização para performance. A classificação é feita aplicando
    todos os padrões contra o texto (ementa + keywords) da proposição.

    Attributes:
        _compiled: Lista de categorias com padrões pré-compilados
    """

    def __init__(self, patterns: dict[str, list[str]]) -> None:
        """Inicializa o classificador com padrões regex por categoria.

        Args:
            patterns: Dicionário de categoria_codigo → lista de regex patterns
        """
        self._compiled = self._compile_patterns(patterns)

    def classificar(self, ementa: str, keywords: str = "") -> list[CategoriaMatch]:
        """Classifica uma proposição com base na ementa e keywords.

        Aplica todos os padrões compilados contra o texto combinado
        (ementa + keywords). Retorna todas as categorias que matcharam,
        após resolver desambiguações.

        Args:
            ementa: Ementa da proposição
            keywords: Palavras-chave adicionais (opcional)

        Returns:
            Lista de CategoriaMatch para cada categoria que matchou.
            Lista vazia se nenhum padrão matchou.
        """
        if not ementa:
            return []

        texto = ementa
        if keywords:
            texto = f"{ementa} {keywords}"

        matches: list[CategoriaMatch] = []
        seen_categorias: set[str] = set()

        for compiled_cat in self._compiled:
            for pattern, raw_pattern in compiled_cat.patterns:
                if pattern.search(texto):
                    if compiled_cat.codigo not in seen_categorias:
                        matches.append(
                            CategoriaMatch(
                                categoria_codigo=compiled_cat.codigo,
                                padrao_matchado=raw_pattern,
                            )
                        )
                        seen_categorias.add(compiled_cat.codigo)
                    break

        matches = self._resolver_desambiguacoes(matches, texto)
        return matches

    def _compile_patterns(self, patterns: dict[str, list[str]]) -> list[_CompiledCategory]:
        """Pré-compila regex para performance.

        Args:
            patterns: Dicionário de categoria → lista de regex strings

        Returns:
            Lista de _CompiledCategory com padrões compilados
        """
        compiled: list[_CompiledCategory] = []
        for codigo, raw_patterns in patterns.items():
            cat = _CompiledCategory(codigo=codigo)
            for raw in raw_patterns:
                try:
                    cat.patterns.append((re.compile(raw, re.IGNORECASE), raw))
                except re.error:
                    logger.warning("Padrão regex inválido para categoria %s: %s", codigo, raw)
            compiled.append(cat)
        return compiled

    def _resolver_desambiguacoes(self, matches: list[CategoriaMatch], texto: str) -> list[CategoriaMatch]:
        """Resolve conflitos de classificação com regras de desambiguação.

        Regras aplicadas:
        - Se BENEFICIOS_CATEGORIAS e DIREITOS_SOCIAIS matcham simultaneamente,
          verifica se o texto menciona categorias específicas (servidor, militar, etc.).
          Se sim, mantém BENEFICIOS_CATEGORIAS; se não, mantém DIREITOS_SOCIAIS.
        - Se TRIBUTACAO_AUMENTO e TRIBUTACAO_ISENCAO matcham simultaneamente,
          verifica se há termos explícitos de isenção/redução no texto.
          Se sim, mantém TRIBUTACAO_ISENCAO; se não, mantém TRIBUTACAO_AUMENTO.

        Args:
            matches: Lista de matches antes da desambiguação
            texto: Texto completo para análise contextual

        Returns:
            Lista de matches após desambiguação
        """
        codigos = {m.categoria_codigo for m in matches}

        # Desambiguação: BENEFICIOS_CATEGORIAS vs DIREITOS_SOCIAIS
        if "BENEFICIOS_CATEGORIAS" in codigos and "DIREITOS_SOCIAIS" in codigos:
            categorias_especificas = re.compile(
                r"(servidor|militar|policial|magistrad|membro|promotor|procurador)",
                re.IGNORECASE,
            )
            if categorias_especificas.search(texto):
                matches = [m for m in matches if m.categoria_codigo != "DIREITOS_SOCIAIS"]
            else:
                matches = [m for m in matches if m.categoria_codigo != "BENEFICIOS_CATEGORIAS"]

        # Desambiguação: TRIBUTACAO_AUMENTO vs TRIBUTACAO_ISENCAO
        if "TRIBUTACAO_AUMENTO" in codigos and "TRIBUTACAO_ISENCAO" in codigos:
            isencao_explicita = re.compile(
                r"(isen[çc][ãa]o|redu[çc][ãa]o|desonera|benef[ií]cio\s+fiscal|incentivo\s+fiscal|imunidade)",
                re.IGNORECASE,
            )
            if isencao_explicita.search(texto):
                matches = [m for m in matches if m.categoria_codigo != "TRIBUTACAO_AUMENTO"]
            else:
                matches = [m for m in matches if m.categoria_codigo != "TRIBUTACAO_ISENCAO"]

        return matches
