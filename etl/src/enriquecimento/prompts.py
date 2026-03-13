"""Templates versionados de prompts para enriquecimento LLM.

Define os prompts (system e user) usados pelo pipeline de enriquecimento
para transformar ementas legislativas em linguagem acessível. O versionamento
permite re-geração seletiva quando prompts são melhorados.
"""

PROMPT_VERSION = "v1.0"
"""Versão atual dos templates de prompt. Max 10 caracteres (varchar(10))."""

SYSTEM_PROMPT = (
    "Você é um assistente especializado em legislação brasileira. "
    "Sua tarefa é transformar ementas legislativas em linguagem acessível ao cidadão comum. "
    "Responda SEMPRE em português brasileiro e em formato JSON com os campos: "
    "headline (string, máx 120 caracteres), resumo_simples (string), "
    "impacto_cidadao (array de strings com impactos concretos), "
    "confianca (float entre 0.0 e 1.0, indicando sua confiança no resumo)."
)
"""System prompt instruindo o LLM sobre formato e idioma de resposta."""


def build_user_prompt(
    tipo: str,
    numero: int,
    ano: int,
    ementa: str,
    categorias: list[str] | None = None,
) -> str:
    """Constrói o user prompt formatado com os dados da proposição.

    Args:
        tipo: Tipo da proposição (ex: "PL", "PEC", "REQ").
        numero: Número da proposição.
        ano: Ano da proposição.
        ementa: Texto da ementa da proposição.
        categorias: Categorias já atribuídas por regex (opcional).

    Returns:
        String formatada do user prompt pronta para envio ao LLM.
    """
    categorias_text = ""
    if categorias:
        categorias_text = f"\nCategorias já atribuídas: {', '.join(categorias)}"

    return (
        f"Proposição: {tipo} {numero}/{ano}\n"
        f"Ementa: {ementa}"
        f"{categorias_text}\n\n"
        "Gere um JSON com headline, resumo_simples, impacto_cidadao e confianca."
    )
