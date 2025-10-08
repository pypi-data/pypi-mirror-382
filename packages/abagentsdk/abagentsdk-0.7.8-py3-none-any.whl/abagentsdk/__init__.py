# abagentsdk/__init__.py
from __future__ import annotations
import os as _os

# Silence noisy logs early
_os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
_os.environ.setdefault("GRPC_LOG_SEVERITY_OVERRIDE", "ERROR")
_os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")
_os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
_os.environ.setdefault("GLOG_minloglevel", "3")
_os.environ.setdefault("FLAGS_minloglevel", "3")
try:
    from absl import logging as _absl_logging  # type: ignore
    _absl_logging.set_verbosity(_absl_logging.ERROR)
    _absl_logging.set_stderrthreshold("error")
except Exception:
    pass

# Public API
from .core.agent import Agent, AgentResult
from .core.memory import Memory
from .core.tools import Tool, ToolCall, FunctionTool, function_tool
from .core.handoffs import Handoff, handoff, RunContextWrapper
from .core.guardrails import (
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

# Version
try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError
    try:
        __version__ = _pkg_version("abagentsdk")
    except PackageNotFoundError:
        __version__ = "0.0.0"
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "Agent", "AgentResult", "Memory",
    "Tool", "ToolCall", "FunctionTool", "function_tool",
    "Handoff", "handoff", "RunContextWrapper",
    "input_guardrail", "output_guardrail",
    "GuardrailFunctionOutput",
    "InputGuardrailTripwireTriggered", "OutputGuardrailTripwireTriggered",
]
