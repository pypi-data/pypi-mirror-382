# Forgebase

Forgebase reúne três blocos principais usados neste monorepo:

- **forge_utils** – logging estruturado e utilidades de paths/configuração.
- **forgebase** – framework MVC-C enxuto baseado em Pydantic v2 (modelos, commands,
  controllers, views e persistência).
- **llm_client** – cliente agnóstico para a OpenAI Responses API com suporte a streaming,
  tool calling e replays offline.

A biblioteca está disponível em [PyPI](https://pypi.org/project/forgebase/) e também no
TestPyPI para validação prévia.

## Instalação rápida

```bash
pip install forgebase
```

Crie um ambiente virtual limpo antes de instalar (`python -m venv .venv && source .venv/bin/activate`).

## Pacote por pacote

### forge_utils

- `forge_utils.log_service.LogService` configura logging com console/arquivo rotativo e filtros.
- `forge_utils.log_service.logger` é a instância global pronta para uso.
- `forge_utils.paths` oferece helpers (`build_app_paths`, `ensure_dirs`) para organizar arquivos
  de configuração, histórico e cache.

### forgebase

Reexporta o framework MVC-C básico. Os pontos de entrada mais usados são:

- `CustomBaseModel` / `BaseModelData`: modelos Pydantic com suporte a *dirty tracking* e observers.
- `CustomCommandBase` + `guard_errors`: encapsulam regras de negócio, padronizando
  o tratamento de exceções (`CommandException`).
- `CustomBaseController` / `CustomBaseView`: composição MVC-C mínima.
- `PersistenceFactory` + `JsonPersistence`: persistência compatível com Pydantic v2.

Todos estes nomes estão disponíveis diretamente com `from forgebase import ...`.

### llm_client

O cliente LLM também é reexportado por `forgebase` para facilitar o consumo:

- `LLMOpenAIClient`: wrapper para chamadas síncronas e streaming na OpenAI Responses API.
- `OpenAIProvider`: implementação da interface `ILLMClient` com orquestração de tool calling.
- `Tool`: modelo Pydantic que representa o schema JSON das ferramentas.
- `APIResponseError` / `ConfigurationError`: exceções específicas do cliente.
- `ContentPart`, `OutputMessage`, `ResponseResult`, `TextFormat`, `TextOutputConfig`: modelos
  retornados pelo Responses API.
- Pronto para múltiplos LLMs: hoje o pacote vem com o provider OpenAI, mas a camada
  (`ILLMClient`) e os hooks de eventos foram pensados para suportar conectores adicionais
  (ex.: Llama, OpenRouter) sem alterar o código que consome o cliente.

## Guia rápido de uso

### Core MVC-C

```python
from forgebase import CustomBaseModel, CustomCommandBase, JsonPersistence, guard_errors

class User(CustomBaseModel):
    id: int
    name: str

class CreateUserCommand(CustomCommandBase):
    @guard_errors
    def execute(self, payload: dict) -> User:
        model = User(**payload)
        # ... lógica de negócio ...
        return model

storage = JsonPersistence("users.json")
```

### Cliente LLM – configuração e chamadas

Crie um arquivo `.env` na raiz do projeto (ou exporte no shell) com:

```
OPENAI_API_KEY=sk-...
```

Todos os exemplos abaixo carregam essa chave automaticamente via `python-dotenv`.

#### Chamada síncrona

```python
import os
from dotenv import load_dotenv
from forgebase import APIResponseError, ConfigurationError, LLMOpenAIClient

load_dotenv()
client = LLMOpenAIClient(api_key=os.environ["OPENAI_API_KEY"], model="gpt-4o-mini")

try:
    response = client.send_prompt("Por que o céu é azul?")
    answer = "\n".join(
        part.text.strip()
        for item in response.output
        for part in getattr(item, "content", [item])
        if getattr(part, "text", None)
    )
    print(answer)
except (APIResponseError, ConfigurationError) as exc:
    print(f"Falha na chamada: {exc}")
```

#### Configurando timeout (⭐ novo na v0.2.0)

Por padrão, as chamadas HTTP usam timeout de 120 segundos. Você pode customizar:

```python
# Timeout de 45 segundos
client = LLMOpenAIClient(
    api_key=os.environ["OPENAI_API_KEY"],
    timeout=45  # segundos
)

# Ou via OpenAIProvider
from forgebase import OpenAIProvider

provider = OpenAIProvider(timeout=45)
provider.set_api_key(os.environ["OPENAI_API_KEY"])
result = provider.send_message("Hello")
```

**Importante:** O timeout se aplica ao tempo total incluindo retries. Com `timeout=45` e `max_tries=4`, o sistema não ultrapassará 45 segundos mesmo com múltiplas tentativas.

#### Chamada com streaming

```python
import os
from dotenv import load_dotenv
from forgebase import LLMOpenAIClient

load_dotenv()
client = LLMOpenAIClient(api_key=os.environ["OPENAI_API_KEY"], model="gpt-4o-mini")

stream = client.send_prompt("Conte uma história curta sobre um robô e uma criança.", streamed=True)
for delta in stream:
    print(delta, end="", flush=True)
print()
```

#### Chamada multimodal (imagem + áudio)

```python
import os
from dotenv import load_dotenv
from forgebase import LLMOpenAIClient

load_dotenv()
client = LLMOpenAIClient(api_key=os.environ["OPENAI_API_KEY"], model="gpt-4o")

response = client.send_prompt(
    "Descreva a imagem e comente o áudio anexado.",
    images=["https://upload.wikimedia.org/wikipedia/commons/9/99/Colorful_sunset.jpg"],
    audio={"base64": "ZGF0YQ==", "mime_type": "audio/wav"},
)
print(response)
```

#### Listar modelos disponíveis

```python
import os
from dotenv import load_dotenv
from forgebase import LLMOpenAIClient

load_dotenv()
client = LLMOpenAIClient(api_key=os.environ["OPENAI_API_KEY"])
models = client.list_models()
print(models["data"][0])
```

#### Tool calling síncrono

```python
import os
from dotenv import load_dotenv
from forgebase import OpenAIProvider, Tool

load_dotenv()
provider = OpenAIProvider()
provider.set_api_key(os.environ["OPENAI_API_KEY"])

tool = Tool(
    type="function",
    name="say_hello",
    parameters={"type": "object", "properties": {"who": {"type": "string"}}, "required": ["who"]},
)
provider.configure_tools([tool], tool_choice="required")
provider.register_tool("say_hello", lambda args: f"Olá, {args['who']}!")

print(provider.send_message("Cumprimente Forgebase."))
```

#### Tool calling com streaming

```python
import os
from dotenv import load_dotenv
from forgebase import OpenAIProvider, Tool

load_dotenv()
provider = OpenAIProvider()
provider.set_api_key(os.environ["OPENAI_API_KEY"])

tool = Tool(
    type="function",
    name="summarize_numbers",
    parameters={"type": "object", "properties": {"nums": {"type": "array", "items": {"type": "number"}}}},
)
provider.configure_tools([tool], tool_choice="auto")
provider.register_tool("summarize_numbers", lambda args: sum(args.get("nums", [])))

for chunk in provider.send_stream("Considere os números 2, 4, 6 e mostre a soma."):
    print(chunk, end="", flush=True)
print()
```

#### Hooks de eventos

Tanto o `LLMOpenAIClient` quanto o `OpenAIProvider` expõem um sistema simples de
hooks para instrumentar o fluxo:

```python
from forgebase import LLMOpenAIClient, OpenAIProvider

client = LLMOpenAIClient(api_key=os.environ["OPENAI_API_KEY"])
client.register_hook("before_request", lambda ctx: print("▶", ctx["prompt"]))
client.register_hook("after_response", lambda ctx: print("◀", ctx.get("response")))

provider = OpenAIProvider(client=client)
provider.register_hook("before_tool_call", lambda ctx: print("tool", ctx["tool"]))
provider.register_hook("after_tool_call", lambda ctx: print("tool result", ctx["result"]))
```

Eventos disponíveis:

- `before_request`, `after_response`, `on_error`, `on_cache_hit` (cliente LLM)
- `before_send`, `after_send`, `on_error`, `before_tool_call`, `after_tool_call`, `tool_error`, `cache_hit` (provider)

### Demo completo

O projeto inclui uma demo mais abrangente que cobre respostas diretas, streaming,
(tool calling) e replays offline:

```bash
PYTHONPATH=shared/src:apps/llm_client/src python -m llm_client.example_full_usage
```

No Windows (PowerShell):

```powershell
$env:PYTHONPATH = "shared/src;apps/llm_client/src"
python -m llm_client.example_full_usage
```

O arquivo `apps/llm_client/src/llm_client/example_full_usage.py` comenta cada etapa
(passos para configurar `OPENAI_API_KEY`, habilitar tool calling real com
`DEMO_TOOL_CALLING=1`, e como funciona o replay offline).

## Configuração do ambiente

### Opção 1 – Poetry (recomendada)

O `pyproject.toml` já descreve todos os pacotes via `path`. Basta executar na raiz:

```bash
poetry install
poetry run pytest -q
poetry run python -m llm_client.example_full_usage
```

O Poetry cria e gerencia o ambiente virtual automaticamente; não é necessário ajustar o
`PYTHONPATH` manualmente.

### Opção 2 – pip + requirements

Se preferir `pip`, gere um virtualenv e instale as dependências de desenvolvimento com
o arquivo `requirements-dev.txt` gerado a partir do `pyproject`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements-dev.txt
```

O arquivo pode ser sincronizado com o `pyproject.toml` executando `python requirements-dev.py`.
Depois disso, exporte `PYTHONPATH=shared/src:framework/src:apps/llm_client/src:cli/src` (ou
use `python -m` para os módulos) e rode `pytest -q` normalmente.

## Desenvolvimento local

- Testes: `pytest -q` (ou `poetry run pytest -q`).
- Linters: `ruff check .` e `mypy --config-file mypy.ini` (com `poetry run` se estiver usando Poetry).
- Build: `python -m build` gera wheel/sdist para publicar em TestPyPI/PyPI.

## Onde continuar

- `docs/api/openai_responses.md`: detalhes da Responses API e eventos de streaming.
- `docs/api/openai_responses_tool_calling.md`: guia de tool calling, payloads e replays.
- `docs/architecture/forgebase-architecture.md`: visão completa da arquitetura e fluxos.
- `docs/release-guide.md`: processo recomendado de versionamento e publicação.
- `docs/testing-strategy.md`: abordagem de testes e boas práticas.
- `docs/configuration.md`: variáveis de ambiente e diretórios importantes.
- `docs/providers/adding-new-provider.md`: instruções para suportar novos LLMs.
- `docs/cli/usage.md`: comandos expostos pela CLI.
- `docs/CONTRIBUTING.md`: convenções de contribuição.
- `docs/adr/README.md`: decisões arquiteturais registradas.
- `docs/tech-debts/TD-001-Robustez-Tool-Calling-Responses.md`: backlog de melhorias planejadas.

Sinta-se à vontade para abrir issues ou PRs com sugestões e correções.
