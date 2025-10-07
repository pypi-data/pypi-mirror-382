# abagent/core/guardrails.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Optional, Sequence, Tuple, Type, TypeVar, Union
import inspect
import asyncio
from abagentsdk.core.agent import Agent
from pydantic import BaseModel, ValidationError

from .handoffs import RunContextWrapper

# =====================
# Data & Exceptions
# =====================

class GuardrailFunctionOutput(BaseModel):
    """
    The result returned by a guardrail function.
    - output_info: arbitrary info you want to keep (e.g., model output, labels)
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
TOutput = TypeVar("TOutput")

@dataclass
class _Guardrail(Generic[TInput]):
    """Container for an input/output guardrail function and its metadata."""
    fn: Callable[..., Any]  # may be sync or async
    # The function signature should be:
    #   input guardrail:  (ctx: RunContextWrapper[None], agent: Agent, input: str) -> GuardrailFunctionOutput
    #   output guardrail: (ctx: RunContextWrapper[None], agent: Agent, output: Any) -> GuardrailFunctionOutput
    name: str

    def run(self, *args, **kwargs) -> GuardrailFunctionOutput:
        """
        Execute guardrail function (supports sync/async; runs async via asyncio.run).
        Returns GuardrailFunctionOutput or raises ValueError/TypeError on bad return type.
        """
        try:
            if inspect.iscoroutinefunction(self.fn):
                try:
                    ret = asyncio.run(self.fn(*args, **kwargs))
                except RuntimeError:
                    # already in a running loop (e.g., notebooks) -> fallback
                    import nest_asyncio  # type: ignore
                    nest_asyncio.apply()
                    loop = asyncio.get_event_loop()
                    ret = loop.run_until_complete(self.fn(*args, **kwargs))
            else:
                ret = self.fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Guardrail '{self.name}' raised an exception: {e}") from e

        if not isinstance(ret, GuardrailFunctionOutput):
            raise TypeError(
                f"Guardrail '{self.name}' must return GuardrailFunctionOutput, got {type(ret)}"
            )
        return ret


# =====================
# Decorators
# =====================

def input_guardrail(fn: Callable[..., Any]) -> _Guardrail[str]:
    """
    Decorator for input guardrails.

    A function like:
        def my_guardrail(ctx: RunContextWrapper[None], agent: Agent, input: str) -> GuardrailFunctionOutput:
            ...
    or async def ...

    Returns a _Guardrail object you can pass into Agent(..., input_guardrails=[...]).
    """
    return _Guardrail(fn=fn, name=fn.__name__)

def output_guardrail(fn: Callable[..., Any]) -> _Guardrail[Any]:
    """
    Decorator for output guardrails.

    A function like:
        def my_guardrail(ctx: RunContextWrapper[None], agent: Agent, output: Any) -> GuardrailFunctionOutput:
            ...
    or async def ...
    """
    return _Guardrail(fn=fn, name=fn.__name__)


# =====================
# Execution Helpers
# =====================

def run_input_guardrails(
    *,
    guards: Sequence[_Guardrail[str]],
    ctx: RunContextWrapper[None],
    agent: "Agent",
    user_input: str,
) -> None:
    for g in guards:
        out = g.run(ctx, agent, user_input)
        if out.tripwire_triggered:
            raise InputGuardrailTripwireTriggered(
                f"Input guardrail '{g.name}' tripwire triggered.", out
            )

def run_output_guardrails(
    *,
    guards: Sequence[_Guardrail[Any]],
    ctx: RunContextWrapper[None],
    agent: "Agent",
    final_output: Any,
) -> None:
    for g in guards:
        out = g.run(ctx, agent, final_output)
        if out.tripwire_triggered:
            raise OutputGuardrailTripwireTriggered(
                f"Output guardrail '{g.name}' tripwire triggered.", out
            )
