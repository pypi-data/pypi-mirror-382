import json
from typing import Any, Dict, Generator, Optional

import httpx
from forge_utils import logger

from .llm_exceptions import APIResponseError, ConfigurationError
from .llm_utils import retry_with_backoff
from .models import ResponseRequest, ResponseResult

OPENAI_API_URL = "https://api.openai.com/v1/responses"

class OpenAIResponse:
    def __init__(
        self,
        api_key: str,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        store_local: bool = False,
        timeout: int = 120
    ):
        self.api_key = api_key
        self.organization = organization
        self.project = project
        self.store_local = store_local
        self.timeout = timeout

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if organization:
            self.headers["OpenAI-Organization"] = organization
        if project:
            self.headers["OpenAI-Project"] = project

    def send_response(self, request: ResponseRequest) -> ResponseResult:
        """Envia requisição com retry e timeout configurado."""
        return self._send_response_with_retry(request)

    @retry_with_backoff()
    def _send_response_with_retry(self, request: ResponseRequest) -> ResponseResult:
        payload = request.dict(exclude_none=True)
        logger.debug("Payload enviado à OpenAI:")
        logger.debug(json.dumps(payload, indent=2))

        try:
            response = httpx.post(
                OPENAI_API_URL,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIResponseError(f"Erro HTTP {e.response.status_code}: {e.response.text}") from e

        data = response.json()
        logger.debug("Resposta recebida da OpenAI:")
        logger.debug(json.dumps(data, indent=2))

        return ResponseResult(**data)

    def get_response(self, response_id: str) -> ResponseResult:
        url = f"{OPENAI_API_URL}/{response_id}"
        response = httpx.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return ResponseResult(**response.json())

    def delete_response(self, response_id: str) -> bool:
        url = f"{OPENAI_API_URL}/{response_id}"
        response = httpx.delete(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json().get("deleted", False)

    def list_input_items(self, response_id: str) -> dict:
        url = f"{OPENAI_API_URL}/{response_id}/input_items"
        response = httpx.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def send_streaming_response(self, request: ResponseRequest) -> Generator[Dict[str, Any], None, None]:
        """Envia requisição streaming com retry e timeout configurado."""
        return self._send_streaming_response_with_retry(request)

    @retry_with_backoff()
    def _send_streaming_response_with_retry(self, request: ResponseRequest) -> Generator[Dict[str, Any], None, None]:
        if not request.stream:
            raise ConfigurationError("O campo 'stream' deve ser True para uso do streaming.")

        payload = request.dict(exclude_none=True)
        logger.debug("Streaming Payload enviado à OpenAI:")
        logger.debug(json.dumps(payload, indent=2))

        with httpx.stream(
            "POST",
            OPENAI_API_URL,
            headers=self.headers,
            json=payload,
            timeout=self.timeout
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line if isinstance(line, str) else line.decode("utf-8")
                if decoded.startswith("data: "):
                    content = decoded[len("data: "):]
                    if content.strip() != "[DONE]":
                        try:
                            yield json.loads(content)
                        except json.JSONDecodeError:
                            continue

    def list_models(self) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/models"
        response = httpx.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
