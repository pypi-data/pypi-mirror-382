from __future__ import annotations
import os as _os

# Silence gRPC/absl noise *before* any heavy imports
_os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
_os.environ.setdefault("GRPC_LOG_SEVERITY_OVERRIDE", "ERROR")
_os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")
_os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
_os.environ.setdefault("GLOG_minloglevel", "3")
_os.environ.setdefault("FLAGS_minloglevel", "3")
try:
    from absl import logging as _absl_logging
    _absl_logging.set_verbosity(_absl_logging.ERROR)
    _absl_logging.set_stderrthreshold("error")
except Exception:
    pass

# Core runtime
from .core.agent import Agent, AgentResult
from .core.memory import Memory
from .core.tools import Tool, ToolCall, FunctionTool, function_tool
from .core.handoffs import Handoff, handoff, RunContextWrapper
# 🔥 Guardrails — export the decorators, result type, and exceptions
from .core.guardrails import (
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

# Providers (Gemini-only)
from .providers.base import ModelProvider
from .providers.gemini import GeminiProvider

# Optional helpers
try:
    from .providers.gemini_catalog import (
        list_gemini_models,
        best_default,
        validate_or_suggest,
        tag_model,
    )
except Exception:
    list_gemini_models = None  # type: ignore
    best_default = None        # type: ignore
    validate_or_suggest = None # type: ignore
    tag_model = None           # type: ignore

# Version
try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError
    try:
        __version__ = _pkg_version("abagentsdk")  # match your PyPI name
    except PackageNotFoundError:
        __version__ = "0.0.0"
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    # Core
    "Agent", "AgentResult", "Memory",
    # Tools
    "Tool", "ToolCall", "FunctionTool", "function_tool",
    # Handoffs
    "Handoff", "handoff", "RunContextWrapper",
    # Guardrails
    "input_guardrail", "output_guardrail",
    "GuardrailFunctionOutput",
    "InputGuardrailTripwireTriggered", "OutputGuardrailTripwireTriggered",
    # Providers
    "ModelProvider", "GeminiProvider",
    # Optional helpers
    "list_gemini_models", "best_default", "validate_or_suggest", "tag_model",

]