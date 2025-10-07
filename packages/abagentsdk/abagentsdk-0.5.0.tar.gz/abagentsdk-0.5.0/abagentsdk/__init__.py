# abagent/__init__.py
from __future__ import annotations
import os as _os

# --- Quiet native logs BEFORE importing anything that might pull in gRPC/absl ---
# Values: DEBUG=0, INFO=1, WARNING=2, ERROR=3, FATAL=4
_os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
_os.environ.setdefault("GRPC_LOG_SEVERITY_OVERRIDE", "ERROR")
_os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")  # ERROR
_os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")           # silence TF/LLVM noise if any
# Some stacks respect these:
_os.environ.setdefault("GLOG_minloglevel", "3")
_os.environ.setdefault("FLAGS_minloglevel", "3")

# Try to set absl logging programmatically too (safe if absl present)
try:
    from absl import logging as _absl_logging
    _absl_logging.set_verbosity(_absl_logging.ERROR)
    _absl_logging.set_stderrthreshold("error")
except Exception:
    pass

# ---- Public SDK imports (safe after silencing) ----
# Core runtime
from .core.agent import Agent, AgentResult
from .core.memory import Memory
from .core.tools import Tool, ToolCall, FunctionTool, function_tool
from .core.handoffs import Handoff, handoff, RunContextWrapper

# Providers (Gemini-only)
from .providers.base import ModelProvider
from .providers.gemini import GeminiProvider

# Optional model catalog helpers
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

# Version helper
try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError
    try:
        __version__ = _pkg_version("abagent")
    except PackageNotFoundError:
        __version__ = "0.0.0"
except Exception:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "Agent", "AgentResult", "Memory",
    "Tool", "ToolCall", "FunctionTool", "function_tool",
    "Handoff", "handoff", "RunContextWrapper",
    "ModelProvider", "GeminiProvider",
    "list_gemini_models", "best_default", "validate_or_suggest", "tag_model",
]
