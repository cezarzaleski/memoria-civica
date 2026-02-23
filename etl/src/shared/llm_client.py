"""Client LLM abstrato e implementação OpenAI com structured output.

Fornece a camada de abstração para chamadas LLM utilizada pelo pipeline de
enriquecimento ETL. O client abstrato permite trocar de provider (OpenAI,
Google, etc.) sem modificar o pipeline.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from openai import APITimeoutError, OpenAI, RateLimitError
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EnriquecimentoOutput(BaseModel):
    """Output estruturado do enriquecimento LLM de uma proposição.

    Attributes:
        headline: Título acessível da proposição (max 120 chars recomendado).
        resumo_simples: Resumo em linguagem simples para o cidadão.
        impacto_cidadao: Lista de impactos concretos ao cidadão.
        confianca: Score de confiança do LLM (0.0 a 1.0).
    """

    headline: str = Field(description="Título acessível da proposição")
    resumo_simples: str = Field(description="Resumo em linguagem simples")
    impacto_cidadao: list[str] = Field(description="Lista de impactos concretos ao cidadão")
    confianca: float = Field(ge=0.0, le=1.0, description="Score de confiança do LLM (0.0 a 1.0)")


@dataclass
class LLMResult:
    """Resultado completo de uma chamada LLM, incluindo output e metadados de uso.

    Attributes:
        output: Output estruturado do enriquecimento.
        tokens_input: Número de tokens de entrada consumidos.
        tokens_output: Número de tokens de saída consumidos.
    """

    output: EnriquecimentoOutput
    tokens_input: int
    tokens_output: int


class LLMClient(ABC):
    """Interface abstrata para providers LLM.

    Define o contrato que qualquer implementação de client LLM deve seguir.
    Permite trocar de provider sem modificar o pipeline de enriquecimento.
    """

    @abstractmethod
    def enriquecer_proposicao(
        self,
        tipo: str,
        numero: int,
        ano: int,
        ementa: str,
        categorias: list[str] | None = None,
    ) -> LLMResult:
        """Enriquece uma proposição legislativa via LLM.

        Args:
            tipo: Tipo da proposição (ex: "PL", "PEC", "REQ").
            numero: Número da proposição.
            ano: Ano da proposição.
            ementa: Texto da ementa da proposição.
            categorias: Categorias já atribuídas por regex (opcional).

        Returns:
            LLMResult com output estruturado e metadados de uso de tokens.
        """
        ...


class OpenAIClient(LLMClient):
    """Implementação concreta do LLMClient usando OpenAI API.

    Utiliza o SDK `openai` com structured JSON output para garantir
    respostas parseáveis. Inclui retry com exponential backoff para
    erros de rate limit e timeout.

    Args:
        api_key: Chave de API da OpenAI (nunca hardcodada).
        model: Modelo a usar (padrão: gpt-4o-mini).
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @property
    def model(self) -> str:
        """Retorna o modelo configurado."""
        return self._model

    def enriquecer_proposicao(
        self,
        tipo: str,
        numero: int,
        ano: int,
        ementa: str,
        categorias: list[str] | None = None,
    ) -> LLMResult:
        """Enriquece uma proposição legislativa via OpenAI API.

        Monta o prompt com os dados da proposição, chama a API com
        structured JSON output e valida a resposta via Pydantic.

        Args:
            tipo: Tipo da proposição (ex: "PL", "PEC", "REQ").
            numero: Número da proposição.
            ano: Ano da proposição.
            ementa: Texto da ementa da proposição.
            categorias: Categorias já atribuídas por regex (opcional).

        Returns:
            LLMResult com output estruturado e metadados de uso de tokens.

        Raises:
            ValueError: Se a resposta do LLM não for JSON válido ou falhar
                na validação Pydantic.
            openai.RateLimitError: Se retries forem esgotados para rate limit.
            openai.APITimeoutError: Se retries forem esgotados para timeout.
            openai.APIError: Para outros erros de API.
        """
        categorias_text = ""
        if categorias:
            categorias_text = f"\nCategorias já atribuídas: {', '.join(categorias)}"

        system_prompt = (
            "Você é um assistente especializado em legislação brasileira. "
            "Sua tarefa é transformar ementas legislativas em linguagem acessível ao cidadão comum. "
            "Responda SEMPRE em português brasileiro e em formato JSON com os campos: "
            "headline (string, máx 120 caracteres), resumo_simples (string), "
            "impacto_cidadao (array de strings com impactos concretos), "
            "confianca (float entre 0.0 e 1.0, indicando sua confiança no resumo)."
        )

        user_prompt = (
            f"Proposição: {tipo} {numero}/{ano}\n"
            f"Ementa: {ementa}"
            f"{categorias_text}\n\n"
            "Gere um JSON com headline, resumo_simples, impacto_cidadao e confianca."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._call_with_retry(messages)

        content = response.choices[0].message.content
        tokens_input = response.usage.prompt_tokens
        tokens_output = response.usage.completion_tokens

        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error("JSON inválido do LLM: %s", content)
            raise ValueError(f"Resposta do LLM não é JSON válido: {e}") from e

        try:
            output = EnriquecimentoOutput.model_validate(data)
        except (ValueError, TypeError) as e:
            logger.error("Falha na validação Pydantic: %s | dados: %s", e, data)
            raise ValueError(f"Falha na validação do output do LLM: {e}") from e

        return LLMResult(
            output=output,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
        )

    def _call_with_retry(self, messages: list[dict], max_retries: int = 3):
        """Chama a API OpenAI com retry exponencial para erros transientes.

        Args:
            messages: Lista de mensagens para o chat completion.
            max_retries: Número máximo de tentativas (padrão: 3).

        Returns:
            Resposta da API OpenAI.

        Raises:
            RateLimitError: Se todas as tentativas falharem por rate limit.
            APITimeoutError: Se todas as tentativas falharem por timeout.
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                return self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=800,
                )
            except (RateLimitError, APITimeoutError) as e:
                last_exception = e
                wait_time = 2**attempt
                logger.warning(
                    "Tentativa %d/%d falhou (%s). Aguardando %ds...",
                    attempt + 1,
                    max_retries,
                    type(e).__name__,
                    wait_time,
                )
                time.sleep(wait_time)

        raise last_exception
