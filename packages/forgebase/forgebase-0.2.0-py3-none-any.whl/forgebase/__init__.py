"""Forgebase core package."""

from importlib import metadata

from llm_client import (  # noqa: F401
    APIResponseError,
    ConfigurationError,
    ContentPart,
    LLMOpenAIClient,
    OpenAIProvider,
    OutputMessage,
    ResponseResult,
    TextFormat,
    TextOutputConfig,
    Tool,
)

from .commandbase import CustomCommandBase, guard_errors  # noqa: F401
from .controllerbase import CustomBaseController  # noqa: F401
from .exceptionbase import CommandException, ForgeBaseException  # noqa: F401
from .factories import PersistenceFactory  # noqa: F401
from .interfaces import (  # noqa: F401
    IBaseCommand,
    IBaseController,
    IBaseModel,
    IBasePersistence,
    IBaseView,
)
from .json_persistence import JSonPersistence as JsonPersistence  # noqa: F401
from .modelbase import BaseModelData, CustomBaseModel  # noqa: F401
from .viewbase import CustomBaseView  # noqa: F401

try:
    __version__ = metadata.version("forgebase")
except metadata.PackageNotFoundError:  # pragma: no cover - during dev
    __version__ = "0.0.dev0"

__all__ = [
    "__version__",
    "BaseModelData",
    "CommandException",
    "CustomBaseModel",
    "CustomCommandBase",
    "CustomBaseController",
    "PersistenceFactory",
    "ForgeBaseException",
    "guard_errors",
    "IBaseCommand",
    "IBaseController",
    "IBaseModel",
    "IBasePersistence",
    "IBaseView",
    "JsonPersistence",
    "CustomBaseView",
    "LLMOpenAIClient",
    "OpenAIProvider",
    "APIResponseError",
    "ConfigurationError",
    "ContentPart",
    "OutputMessage",
    "ResponseResult",
    "TextFormat",
    "TextOutputConfig",
    "Tool",
]
