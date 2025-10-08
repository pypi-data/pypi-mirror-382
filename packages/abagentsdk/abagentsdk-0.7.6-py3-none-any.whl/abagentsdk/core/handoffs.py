# abagentsdk/core/handoffs.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union, TYPE_CHECKING
import asyncio
import inspect
import re

from pydantic import BaseModel, Field, ValidationError

from .tools import Tool
from .memory import Memory

# 👉 IMPORTANT: avoid importing Agent at runtime to prevent circular import
if TYPE_CHECKING:
    from .agent import Agent  # only for type hints, not executed at runtime

# Marker used by REPLs to auto-switch active agent on handoff
HANDOFF_MARK_PREFIX = "<<<HANDOFF:"  # e.g. "<<<HANDOFF:Billing Agent>>>"

# ---------- Context wrapper ----------

T = TypeVar("T")

@dataclass
class RunContextWrapper(Generic[T]):
    """Context given to callbacks and dynamic instructions."""
    current_agent: "Agent"          # forward-ref string; no runtime import
    target_agent: "Agent"
    memory: Memory
    steps: List[str]
    context: Optional[T] = None     # user-defined context object

# ---------- Handoff payload ----------

class HandoffInputData(BaseModel):
    user_message: str = Field(default="Please take over from here.")
    history: List[Dict[str, str]] = Field(default_factory=list)  # [{role, content}, ...]
    metadata: Dict[str, Any] = Field(default_factory=dict)

def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return s.strip("_")

def _default_tool_name_for(agent_name: str) -> str:
    return f"transfer_to_{_slug(agent_name)}"

def _default_tool_desc_for(agent_name: str) -> str:
    return f"Handoff to the specialized agent '{agent_name}'. Use when this agent is better suited."

def _memory_to_history(memory: Memory) -> List[Dict[str, str]]:
    return [{"role": m.role, "content": m.content} for m in memory.load()]

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

    def to_tool(self, current_agent: "Agent") -> Tool:
        input_schema = self.input_type

        class _HandoffTool(Tool):
            name = self.tool_name
            description = self.description
            schema = input_schema

            def run(inner_self, **kwargs) -> str:
                enabled = self.is_enabled() if callable(self.is_enabled) else self.is_enabled
                if not enabled:
                    return f"[Handoff Disabled] {self.tool_name}"

                if self.input_type is not None:
                    try:
                        input_obj = self.input_type(**kwargs)
                    except ValidationError as e:
                        return f"[Handoff Input Error] {e}"
                else:
                    input_obj = None  # type: ignore

                hid = HandoffInputData(
                    user_message=(kwargs.get("message") if "message" in kwargs else "Please take over from here."),
                    history=_memory_to_history(current_agent.memory),
                    metadata={"from_agent": current_agent.name, "to_agent": self.agent.name},
                )

                if self.input_filter:
                    try:
                        hid = self.input_filter(hid)
                    except Exception as e:
                        return f"[Handoff Filter Error] {e}"

                if self.on_handoff:
                    ctx = RunContextWrapper(
                        current_agent=current_agent,
                        target_agent=self.agent,
                        memory=current_agent.memory,
                        steps=[],
                        context=None,
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
                        return f"[Handoff Callback Error] {e}"

                start = (
                    f"Takeover reason/data:\n{input_obj.model_dump_json(indent=2)}"
                    if input_obj is not None
                    else hid.user_message
                )
                result = self.agent.run(start)

                marker = f"{HANDOFF_MARK_PREFIX}{self.agent.name}>>>"
                return f"{marker}\n{result.content}"

        return _HandoffTool()

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
