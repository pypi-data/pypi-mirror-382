# abagentsdk/__init__.py
from __future__ import annotations

# Install silence BEFORE any provider/grpc imports
from .utils.silence import install_silence
install_silence()

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
]
