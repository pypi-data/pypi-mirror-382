from __future__ import annotations

from typing import Iterable, List, Optional, Protocol


class ILLMClient(Protocol):
    """Interface agnóstica para clientes LLM.

    Implementações devem prover envio síncrono e opcionalmente streaming.
    O parâmetro `context` fica livre (lista de dicts) para permitir estratégias
    diversas de construção de prompt sem acoplamento.
    """

    @property
    def name(self) -> str:  # noqa: D401
        """Nome do provedor (ex.: 'openai', 'ollama')."""
        ...

    def set_api_key(self, key: str) -> bool:
        """Configura a credencial, retornando True se ficar pronto para uso."""
        ...

    def send_message(self, prompt: str, context: Optional[List[dict]] = None) -> str:
        """Envia um prompt e retorna o texto final."""
        ...

    def send_stream(self, prompt: str, context: Optional[List[dict]] = None) -> Iterable[str]:
        """Gera tokens/trechos de resposta em streaming."""
        ...


__all__ = ["ILLMClient"]

