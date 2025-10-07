# abagent/__init__.py
from __future__ import annotations

# Core runtime
from .core.agent import Agent, AgentResult
from .core.memory import Memory
from .core.tools import Tool, ToolCall, FunctionTool, function_tool
from .core.handoffs import Handoff, handoff, RunContextWrapper

# Providers (Gemini-only)
from .providers.base import ModelProvider
from .providers.gemini import GeminiProvider

# Optional model catalog helpers (sdk should still import if missing)
try:
    from .providers.gemini_catalog import (
        list_gemini_models,
        best_default,
        validate_or_suggest,
        tag_model,
    )
except Exception:  # pragma: no cover
    list_gemini_models = None  # type: ignore
    best_default = None        # type: ignore
    validate_or_suggest = None # type: ignore
    tag_model = None           # type: ignore

# Version helper (doesn't crash in editable installs)
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("abagent")
    except PackageNotFoundError:
        __version__ = "0.0.0"
except Exception:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    # version
    "__version__",
    # core
    "Agent", "AgentResult", "Memory",
    "Tool", "ToolCall", "FunctionTool", "function_tool",
    "Handoff", "handoff", "RunContextWrapper",
    # providers
    "ModelProvider", "GeminiProvider",
    # optional helpers
    "list_gemini_models", "best_default", "validate_or_suggest", "tag_model",
]
