# abagentsdk/core/guardrails.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar, TYPE_CHECKING
import inspect
import asyncio
from pydantic import BaseModel

# ⚠️ IMPORTANT: Do NOT import Agent at runtime — this causes circular import with core/agent.py
if TYPE_CHECKING:
    from .agent import Agent  # only for type hints; not executed at import time

# =====================
# Data & Exceptions
# =====================

class GuardrailFunctionOutput(BaseModel):
    """
    Result returned by a guardrail function.
    - output_info: arbitrary info (e.g., sub-model output, labels)
    - tripwire_triggered: if True, the guardrail blocks the agent
    - reason: optional human-readable reason
    """
    output_info: Any
    tripwire_triggered: bool
    reason: Optional[str] = None

class InputGuardrailTripwireTriggered(RuntimeError):
    def __init__(self, message: str, output: GuardrailFunctionOutput):
        super().__init__(message)
        self.output = output

class OutputGuardrailTripwireTriggered(RuntimeError):
    def __init__(self, message: str, output: GuardrailFunctionOutput):
        super().__init__(message)
        self.output = output


TInput = TypeVar("TInput")

@dataclass
class _Guardrail(Generic[TInput]):
    """Wraps a guardrail function (sync or async)."""
    fn: Callable[..., Any]
    name: str

    def run(self, *args, **kwargs) -> GuardrailFunctionOutput:
        """
        Execute guardrail function. Supports sync/async (async via asyncio.run()).
        Must return GuardrailFunctionOutput.
        """
        try:
            if inspect.iscoroutinefunction(self.fn):
                try:
                    return asyncio.run(self.fn(*args, **kwargs))
                except RuntimeError:
                    # Already inside an event loop (e.g., notebooks)
                    # Use a minimal fallback to run the coroutine.
                    import nest_asyncio  # type: ignore
                    nest_asyncio.apply()
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(self.fn(*args, **kwargs))
            else:
                return self.fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Guardrail '{self.name}' raised an exception: {e}") from e


# =====================
# Decorators
# =====================

def input_guardrail(fn: Callable[..., Any]) -> _Guardrail[str]:
    """
    Decorator for input guardrails.

    Signature should be:
      def my_guardrail(ctx, agent, input: str | list[Any]) -> GuardrailFunctionOutput: ...
      # 'agent' is the running Agent instance (type only under TYPE_CHECKING)
    """
    return _Guardrail(fn=fn, name=fn.__name__)

def output_guardrail(fn: Callable[..., Any]) -> _Guardrail[Any]:
    """
    Decorator for output guardrails.

    Signature should be:
      def my_guardrail(ctx, agent, output: Any) -> GuardrailFunctionOutput: ...
    """
    return _Guardrail(fn=fn, name=fn.__name__)


# =====================
# Execution Helpers (no Agent import at runtime)
# =====================

def run_input_guardrails(
    *,
    guards: Sequence[_Guardrail[str]],
    ctx: Any,           # RunContextWrapper[None]; typed as Any to avoid importing it
    agent: Any,         # 'Agent' for type hints only; avoid runtime import
    user_input: str,
) -> None:
    for g in guards:
        out = g.run(ctx, agent, user_input)
        if not isinstance(out, GuardrailFunctionOutput):
            raise TypeError(
                f"Input guardrail '{g.name}' must return GuardrailFunctionOutput, got {type(out)}"
            )
        if out.tripwire_triggered:
            raise InputGuardrailTripwireTriggered(
                f"Input guardrail '{g.name}' tripwire triggered.", out
            )

def run_output_guardrails(
    *,
    guards: Sequence[_Guardrail[Any]],
    ctx: Any,           # RunContextWrapper[None]
    agent: Any,         # Agent
    final_output: Any,
) -> None:
    for g in guards:
        out = g.run(ctx, agent, final_output)
        if not isinstance(out, GuardrailFunctionOutput):
            raise TypeError(
                f"Output guardrail '{g.name}' must return GuardrailFunctionOutput, got {type(out)}"
            )
        if out.tripwire_triggered:
            raise OutputGuardrailTripwireTriggered(
                f"Output guardrail '{g.name}' tripwire triggered.", out
            )
