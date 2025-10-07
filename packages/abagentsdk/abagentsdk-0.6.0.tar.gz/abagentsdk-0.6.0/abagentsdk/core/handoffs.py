# abagent/core/handoffs.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, Generic, TypeVar, Union, TYPE_CHECKING
from pydantic import BaseModel, Field, ValidationError
import inspect
import asyncio
import re

from .tools import Tool
from .memory import Memory
from .messages import Message

if TYPE_CHECKING:
    from .agent import Agent  # forward ref


# ---------- Data Types ----------

class HandoffInputData(BaseModel):
    """Payload passed to the target agent when a handoff happens."""
    user_message: str = Field(default="Please take over from here.")
    history: List[Dict[str, str]] = Field(default_factory=list)  # [{role, content}, ...]
    metadata: Dict[str, Any] = Field(default_factory=dict)


T = TypeVar("T", bound=BaseModel)  # input schema typing for callbacks


@dataclass
class RunContextWrapper(Generic[T]):
    """Context given to on_handoff callbacks so you can observe/augment runs."""
    current_agent: "Agent"
    target_agent: "Agent"
    memory: Memory
    steps: List[str]


# ---------- Helpers ----------

def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return s.strip("_")

def _default_tool_name_for(agent_name: str) -> str:
    return f"transfer_to_{_slug(agent_name)}"

def _default_tool_desc_for(agent_name: str) -> str:
    return f"Handoff to the specialized agent '{agent_name}'. Use when this agent is better suited for the task."


def _memory_to_history(memory: Memory) -> List[Dict[str, str]]:
    return [{"role": m.role, "content": m.content} for m in memory.load()]


# ---------- Handoff Definition ----------

class Handoff:
    """
    Configures a 'handoff tool' that, when called, transfers control to another Agent.
    """
    def __init__(
        self,
        *,
        agent: "Agent",
        tool_name_override: Optional[str] = None,
        tool_description_override: Optional[str] = None,
        on_handoff: Optional[Callable[..., Any]] = None,   # (ctx[, input_data])
        input_type: Optional[Type[BaseModel]] = None,       # pydantic schema of tool args
        input_filter: Optional[Callable[[HandoffInputData], HandoffInputData]] = None,
        is_enabled: Union[bool, Callable[[], bool]] = True,
    ) -> None:
        self.agent = agent
        self.tool_name = tool_name_override or _default_tool_name_for(agent.name)
        self.description = tool_description_override or _default_tool_desc_for(agent.name)
        self.on_handoff = on_handoff
        self.input_type = input_type
        self.input_filter = input_filter
        self.is_enabled = is_enabled

    # Factory helper to build a Tool instance bound to the CURRENT agent at runtime
    def to_tool(self, current_agent: "Agent") -> Tool:
        input_schema = self.input_type  # may be None

        class _HandoffTool(Tool):
            name = self.tool_name
            description = self.description
            schema = input_schema  # lets the LLM send structured args

            def run(inner_self, **kwargs) -> str:
                # is_enabled gate (supports bool or callable)
                enabled = self.is_enabled() if callable(self.is_enabled) else self.is_enabled
                if not enabled:
                    return f"[Handoff Disabled] {self.tool_name}"

                # Validate/shape args into input_data (if schema provided)
                if self.input_type is not None:
                    try:
                        input_obj = self.input_type(**kwargs)
                    except ValidationError as e:
                        return f"[Handoff Input Error] {e}"
                else:
                    input_obj = None  # type: ignore

                # Compose input data with current conversation history
                hid = HandoffInputData(
                    user_message=(kwargs.get("message") if "message" in kwargs else "Please take over from here."),
                    history=_memory_to_history(current_agent.memory),
                    metadata={"from_agent": current_agent.name, "to_agent": self.agent.name},
                )

                # Apply optional filter
                if self.input_filter:
                    try:
                        hid = self.input_filter(hid)
                    except Exception as e:
                        return f"[Handoff Filter Error] {e}"

                # on_handoff callback
                if self.on_handoff:
                    ctx = RunContextWrapper(
                        current_agent=current_agent,
                        target_agent=self.agent,
                        memory=current_agent.memory,
                        steps=[],
                    )
                    try:
                        if input_obj is not None:
                            if inspect.iscoroutinefunction(self.on_handoff):
                                asyncio.run(self.on_handoff(ctx, input_obj))
                            else:
                                self.on_handoff(ctx, input_obj)
                        else:
                            if inspect.iscoroutinefunction(self.on_handoff):
                                asyncio.run(self.on_handoff(ctx))
                            else:
                                self.on_handoff(ctx)
                    except Exception as e:
                        # Non-fatal: report but continue
                        return f"[Handoff Callback Error] {e}"

                # Build a starting prompt for target agent
                # Use input_obj if it exists (pretty-print), else hid.user_message
                if input_obj is not None:
                    start = f"Takeover reason/data:\n{input_obj.model_dump_json(indent=2)}"
                else:
                    start = hid.user_message

                # Delegate to target agent
                result = self.agent.run(start)
                return result.content

        return _HandoffTool()


# Convenient factory function
def handoff(
    agent: "Agent",
    *,
    tool_name_override: Optional[str] = None,
    tool_description_override: Optional[str] = None,
    on_handoff: Optional[Callable[..., Any]] = None,
    input_type: Optional[Type[BaseModel]] = None,
    input_filter: Optional[Callable[[HandoffInputData], HandoffInputData]] = None,
    is_enabled: Union[bool, Callable[[], bool]] = True,
) -> Handoff:
    return Handoff(
        agent=agent,
        tool_name_override=tool_name_override,
        tool_description_override=tool_description_override,
        on_handoff=on_handoff,
        input_type=input_type,
        input_filter=input_filter,
        is_enabled=is_enabled,
    )
