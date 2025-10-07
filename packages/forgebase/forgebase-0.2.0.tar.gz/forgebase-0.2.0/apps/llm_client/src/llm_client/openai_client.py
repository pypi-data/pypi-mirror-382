import json
from collections import defaultdict
from typing import Any, Callable, Iterable, cast

from forge_utils import logger
from pydantic import HttpUrl

from .llm_exceptions import ConfigurationError
from .models import (
    InputAudio,
    InputImage,
    InputItem,
    InputText,
    InputToolResult,
    ResponseRequest,
    ResponseResult,
    TextFormat,
    TextOutputConfig,
    Tool,
)
from .response import OpenAIResponse


class LLMOpenAIClient:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int | None = None,
        temperature: float = 1.0,
        user: str | None = None,
        store_local: bool = False,
        response: Any | None = None,
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.user = user
        self.timeout = timeout
        self.response = response or OpenAIResponse(api_key, store_local=store_local, timeout=timeout)
        self._tools: list[Tool] | None = None
        self._tool_choice: str | dict | None = None
        self.last_request: ResponseRequest | None = None
        self._hooks: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self._tool_handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

    HOOK_EVENTS = {"before_request", "after_response", "on_error", "on_cache_hit"}

    def register_hook(self, event: str, callback: Callable[[dict[str, Any]], None]) -> None:
        if event not in self.HOOK_EVENTS:
            raise ValueError(f"Evento de hook desconhecido: {event}")
        self._hooks[event].append(callback)

    def clear_hooks(self, event: str | None = None) -> None:
        if event is None:
            self._hooks.clear()
        else:
            self._hooks.pop(event, None)

    def _emit_hook(self, event: str, payload: dict[str, Any]) -> None:
        for callback in list(self._hooks.get(event, [])):
            try:
                callback(payload)
            except Exception as hook_exc:  # pragma: no cover - hooks não devem quebrar o fluxo
                logger.error(
                    "Erro ao executar hook '%s'",
                    event,
                    exc_info=hook_exc,
                )

    def _build_input_sequence(
        self,
        prompt: str,
        *,
        input_override: list[InputItem | InputToolResult | dict[str, Any]] | str | None,
        images: list[str] | None,
        audio: str | dict[str, str] | None,
    ) -> list[InputItem | InputToolResult | dict[str, Any]] | str:
        if input_override is not None:
            return input_override
        require_sequence = bool(images) or audio is not None
        if not require_sequence:
            return prompt

        sequence: list[InputItem | InputToolResult | dict[str, Any]] = []
        if prompt:
            sequence.append(InputText(type="input_text", text=prompt))
        for url in images or []:
            image_url = cast(HttpUrl, url)
            sequence.append(InputImage(type="input_image", image_url=image_url))
        if audio is not None:
            if isinstance(audio, dict):
                data = audio.get("base64") or audio.get("data")
                if not data:
                    raise ConfigurationError("audio precisa de chave 'base64' ou 'data'.")
                sequence.append(
                    InputAudio(
                        type="input_audio",
                        audio_base64=data,
                        mime_type=audio.get("mime_type"),
                    )
                )
            else:
                sequence.append(InputAudio(type="input_audio", audio_base64=audio))
        return sequence

    def configure_tools(
        self,
        *,
        tools: list[Tool] | None = None,
        tool_choice: str | dict | None = None,
    ) -> None:
        self._tools = tools
        self._tool_choice = tool_choice

    def register_tool(self, name: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        """Registra um handler para uma tool específica.

        Args:
            name: Nome da tool
            handler: Função que recebe os argumentos e retorna o resultado
        """
        self._tool_handlers[name] = handler

    def _normalize_tool_choice(self, tool_choice: str | dict | None) -> str | dict | None:
        """Normalize tool_choice for compatibility across API variants.

        Accepts legacy shapes like {"type":"tool","name":"X"} or
        {"type":"function","function":{"name":"X"}} and adapts them to the
        Responses API contract {"type": "function", "name": "X"}.
        """
        if isinstance(tool_choice, dict):
            normalized: dict[str, Any] = dict(tool_choice)
            tool_type = normalized.get("type")
            name = normalized.get("name")
            func = (
                normalized.get("function")
                if isinstance(normalized.get("function"), dict)
                else None
            )

            if tool_type == "tool" and name:
                return {"type": "function", "name": name}

            if tool_type == "function":
                if func and func.get("name") and not name:
                    name = func["name"]
                if name:
                    return {"type": "function", "name": name}

            if func and func.get("name") and tool_type == "function":
                normalized.setdefault("name", func["name"])
                normalized.pop("function", None)
                return normalized
        return tool_choice

    def stream_events(
        self,
        prompt: str,
        *,
        tools: list[Tool] | None = None,
        tool_choice: str | dict | None = None,
        previous_response_id: str | None = None,
        input_override: list[InputItem | InputToolResult | dict[str, Any]] | str | None = None,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> Iterable[dict[str, Any]]:
        if not prompt or not isinstance(prompt, str):
            logger.warning("Prompt inválido recebido em send_prompt.")
            raise ConfigurationError("O prompt precisa ser uma string não vazia.")
        tools = tools if tools is not None else self._tools
        tool_choice = tool_choice if tool_choice is not None else self._tool_choice
        tool_choice = self._normalize_tool_choice(tool_choice)
        request_input = self._build_input_sequence(
            prompt,
            input_override=input_override,
            images=images,
            audio=audio,
        )
        request = ResponseRequest(
            model=self.model,
            input=request_input,
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            user=self.user,
            stream=True,
            text=TextOutputConfig(format=TextFormat(type="text")),
            tools=tools,
            tool_choice=tool_choice,
            previous_response_id=previous_response_id,
        )
        self.last_request = request
        payload: dict[str, Any] = {
            "prompt": prompt,
            "request": request,
            "streamed": True,
            "tools": tools,
            "tool_choice": tool_choice,
            "previous_response_id": previous_response_id,
            "images": images,
            "audio": audio,
        }
        self._emit_hook("before_request", payload)
        try:
            raw_stream = self.response.send_streaming_response(request)
        except Exception as exc:
            payload_err = dict(payload)
            payload_err["error"] = exc
            self._emit_hook("on_error", payload_err)
            raise

        def wrapper() -> Iterable[dict[str, Any]]:
            try:
                for item in raw_stream:
                    yield item
            except Exception as exc:
                payload_err = dict(payload)
                payload_err["error"] = exc
                self._emit_hook("on_error", payload_err)
                raise
            else:
                payload_after = dict(payload)
                payload_after["response"] = None
                self._emit_hook("after_response", payload_after)

        return wrapper()

    def send_prompt(
        self,
        prompt: str,
        streamed: bool = False,
        *,
        tools: list[Tool] | None = None,
        tool_choice: str | dict | None = None,
        previous_response_id: str | None = None,
        input_override: list[InputItem | InputToolResult | dict[str, Any]] | str | None = None,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> Any:
        if not prompt or not isinstance(prompt, str):
            logger.warning("Prompt inválido recebido em send_prompt.")
            raise ConfigurationError("O prompt precisa ser uma string não vazia.")
        tools = tools if tools is not None else self._tools
        tool_choice = tool_choice if tool_choice is not None else self._tool_choice
        tool_choice = self._normalize_tool_choice(tool_choice)

        if streamed:
            events = self.stream_events(
                prompt,
                tools=tools,
                tool_choice=tool_choice,
                previous_response_id=previous_response_id,
                input_override=input_override,
                images=images,
                audio=audio,
            )

            def stream_gen() -> Iterable[str]:
                logger.debug("Iniciando geração de resposta em modo streaming.")
                for event in events:
                    if event.get("type") == "response.output_text.delta":
                        delta = extract_text_delta(event)
                        if delta:
                            yield delta

            return stream_gen()

        logger.debug("Iniciando geração de resposta em modo direto.")
        request_input = self._build_input_sequence(
            prompt,
            input_override=input_override,
            images=images,
            audio=audio,
        )
        request = ResponseRequest(
            model=self.model,
            input=request_input,
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            user=self.user,
            stream=False,
            text=TextOutputConfig(format=TextFormat(type="text")),
            tools=tools,
            tool_choice=tool_choice,
            previous_response_id=previous_response_id,
        )
        self.last_request = request
        payload: dict[str, Any] = {
            "prompt": prompt,
            "request": request,
            "streamed": False,
            "tools": tools,
            "tool_choice": tool_choice,
            "previous_response_id": previous_response_id,
            "images": images,
            "audio": audio,
        }
        self._emit_hook("before_request", payload)
        try:
            response = self.response.send_response(request)
        except Exception as exc:
            payload_err = dict(payload)
            payload_err["error"] = exc
            self._emit_hook("on_error", payload_err)
            raise
        payload_after = dict(payload)
        payload_after["response"] = response
        self._emit_hook("after_response", payload_after)
        return response

    def list_models(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"operation": "list_models"}
        self._emit_hook("before_request", payload)
        try:
            data = self.response.list_models()
        except Exception as exc:
            payload_err = dict(payload)
            payload_err["error"] = exc
            self._emit_hook("on_error", payload_err)
            raise
        payload_after = dict(payload)
        payload_after["response"] = data
        self._emit_hook("after_response", payload_after)
        return data

    def send_with_tool_orchestration(
        self,
        prompt: str,
        *,
        tools: list[Tool] | None = None,
        tool_handlers: dict[str, Callable[[dict[str, Any]], Any]] | None = None,
        tool_choice: str | dict | None = None,
        max_rounds: int = 3,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> str:
        """
        Orquestra tool calling automaticamente até max_rounds.

        Args:
            prompt: Texto do prompt
            tools: Lista de tools disponíveis (usa self._tools se None)
            tool_handlers: Dict de handlers {name: function} (usa self._tool_handlers se None)
            tool_choice: Escolha de tool (usa self._tool_choice se None)
            max_rounds: Máximo de rodadas de tool calling
            images: URLs de imagens
            audio: Audio em base64 ou dict

        Returns:
            Texto final extraído da resposta
        """
        tools = tools if tools is not None else self._tools
        tool_handlers = tool_handlers if tool_handlers is not None else self._tool_handlers
        tool_choice = tool_choice if tool_choice is not None else self._tool_choice
        tool_choice = self._normalize_tool_choice(tool_choice)

        # Primeira chamada
        from typing import cast
        resp: ResponseResult = cast(
            ResponseResult,
            self.send_prompt(
                prompt,
                streamed=False,
                tools=tools,
                tool_choice=tool_choice,
                images=images,
                audio=audio,
            ),
        )

        # Itera até max_rounds executando tools
        for round_num in range(max_rounds):
            uses = self._collect_tool_uses(resp)
            if not uses:
                text = _extract_text_from_response(resp)
                if text:
                    return text
                break

            tool_results = self._eval_tools(uses, tool_handlers)
            if not tool_results:
                break

            # Constrói contexto para próxima rodada
            context_items: list[InputItem | InputToolResult | dict[str, Any]] = []
            is_real = isinstance(self.response, OpenAIResponse)

            for u in uses:
                raw = u.get("raw")
                if isinstance(raw, dict):
                    if is_real and raw.get("type") == "function_call":
                        context_items.append(raw)
                    elif not is_real:
                        context_items.append(raw)
            context_items.extend(tool_results)

            # Ajusta tool_choice para próxima rodada
            follow_tool_choice = (
                None if tool_choice == "required" else tool_choice
            )

            resp = cast(
                ResponseResult,
                self.send_prompt(
                    prompt,
                    streamed=False,
                    tools=tools,
                    tool_choice=follow_tool_choice or "auto",
                    previous_response_id=resp.id,
                    input_override=context_items,
                    images=images,
                    audio=audio,
                ),
            )

        return _extract_text_from_response(resp) or ""

    def _collect_tool_uses(self, resp: ResponseResult) -> list[dict]:
        """Coleta todos os tool uses da resposta."""
        uses: list[dict] = []
        for item in getattr(resp, "output", []) or []:
            # 1) function_call item (top-level)
            if getattr(item, "type", "") == "function_call":
                name = getattr(item, "name", "")
                call_id = getattr(item, "call_id", None) or getattr(item, "id", "")
                raw_args = getattr(item, "arguments", {})
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                else:
                    args = raw_args
                try:
                    raw_item = {
                        "type": "function_call",
                        "name": name,
                        "call_id": call_id,
                        "arguments": raw_args if isinstance(raw_args, str) else json.dumps(args),
                    }
                except Exception:
                    raw_item = {
                        "type": "function_call",
                        "name": name,
                        "call_id": call_id,
                        "arguments": "{}",
                    }
                if call_id:
                    uses.append({
                        "kind": "function",
                        "name": name,
                        "id": call_id,
                        "args": args,
                        "raw": raw_item,
                    })
                continue

            # 2) tool_use em mensagem ou top-level
            parts = getattr(item, "content", None)
            candidate_parts = parts if parts is not None else [item]
            for part in candidate_parts:
                if getattr(part, "type", "") != "tool_use":
                    continue
                name = getattr(part, "name", None) or ""
                tool_id = getattr(part, "id", None) or getattr(part, "tool_use_id", None) or ""
                raw_args = getattr(part, "input", None) or getattr(part, "arguments", None) or {}
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                else:
                    args = raw_args
                if tool_id:
                    raw_item = {
                        "type": "tool_use",
                        "id": tool_id,
                        "name": name,
                        "input": raw_args if isinstance(raw_args, str) else json.dumps(args),
                    }
                    uses.append({
                        "kind": "tool",
                        "name": name,
                        "id": tool_id,
                        "args": args,
                        "raw": raw_item,
                    })
        return uses

    def _eval_tools(
        self,
        uses: list[dict],
        tool_handlers: dict[str, Callable[[dict[str, Any]], Any]]
    ) -> list[dict]:
        """Executa os handlers das tools e retorna os resultados."""
        results: list[dict] = []
        is_real = isinstance(self.response, OpenAIResponse)

        for u in uses:
            fn = tool_handlers.get(u.get("name", ""))
            try:
                result = fn(u["args"]) if fn else "(tool not registered)"
            except Exception as exc:
                logger.error(f"Erro ao executar tool {u.get('name')}: {exc}")
                result = f"tool_error: {exc}"

            if u.get("kind") == "function":
                # Build output payload
                if isinstance(result, (dict, list)):
                    output = json.dumps(result)
                else:
                    output = json.dumps({"result": str(result)})
                call_identifier = u.get("id")
                if not call_identifier:
                    continue
                if is_real:
                    results.append({
                        "type": "function_call_output",
                        "call_id": str(call_identifier),
                        "output": output,
                    })
                else:
                    raw = u.get("raw")
                    if isinstance(raw, dict):
                        results.append(raw)
                    results.append({
                        "type": "function_call_output",
                        "call_id": call_identifier,
                        "output": output,
                    })
            else:
                call_identifier = u.get("id")
                if not call_identifier:
                    continue
                if isinstance(result, (dict, list)):
                    output = json.dumps(result)
                else:
                    output = str(result)
                if is_real:
                    results.append({
                        "type": "custom_tool_call_output",
                        "call_id": str(call_identifier),
                        "output": output,
                    })
                else:
                    results.append({
                        "type": "custom_tool_call_output",
                        "call_id": call_identifier,
                        "output": output,
                    })
        return results

def extract_text_delta(event: dict) -> str:
    return event.get("delta", "")


def _extract_text_from_response(resp: Any) -> str:
    """Extrai texto de ResponseResult suportando itens de mensagem ou partes diretas."""
    try:
        items = getattr(resp, "output", None) or []
        for item in items:
            parts = getattr(item, "content", None)
            if parts is None:
                # item pode ser um ContentPart direto
                if (
                    getattr(item, "type", "") in ("output_text", "text")
                    and getattr(item, "text", None)
                ):
                    return item.text.strip()
                continue
            for p in parts:
                if (
                    getattr(p, "type", "") in ("output_text", "text")
                    and getattr(p, "text", None)
                ):
                    return p.text.strip()
        return ""
    except Exception:
        return ""
