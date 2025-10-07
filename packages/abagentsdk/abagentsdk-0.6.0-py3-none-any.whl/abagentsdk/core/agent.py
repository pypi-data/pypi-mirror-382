# abagent/core/agent.py
from __future__ import annotations

import json
import sys
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from .memory import Memory
from .tools import Tool, ToolCall
from .handoffs import Handoff, handoff as handoff_factory, RunContextWrapper
from ..config import SDKConfig
from ..providers.gemini import GeminiProvider
from ..utils.logging import log_step

# Optional model catalog helpers (SDK still works if missing)
try:
    from ..providers.gemini_catalog import (
        list_gemini_models,
        best_default,
        validate_or_suggest,
        tag_model,
    )
except Exception:  # pragma: no cover
    def list_gemini_models(include_experimental: bool = True) -> List[str]:
        return ["models/gemini-1.5-pro", "models/gemini-1.5-flash"]

    def best_default(goal: str = "balanced") -> str:
        return "models/gemini-1.5-pro"

    def validate_or_suggest(chosen: str, include_experimental: bool = True):
        avail = list_gemini_models(include_experimental=include_experimental)
        return (chosen in avail), (avail[0] if avail else None), avail

    def tag_model(name: str):
        return {"family": "gemini", "speed": "balanced", "quality": "balanced", "size": "standard"}


BASE_SYSTEM_PROMPT = (
    "You are the ABZ Agent SDK runtime.\n"
    "Reason step-by-step. If a TOOL is needed, respond ONLY with a JSON object of the form "
    '{"tool":"<name>","args":{...}}. Do not add any extra text with the JSON.\n'
    "If no tool is needed, reply with the final answer in concise natural language.\n"
    "When calling a tool, use ONLY the exact names from the tools manifest provided below."
)


class AgentResult:
    def __init__(self, content: str, steps: List[str]):
        self.content = content
        self.steps = steps


class Agent:
    """
    Gemini-only Agent.

    Required:
      - name: str
      - instructions: str

    Model parameter behavior:
      - model='auto' (default): list models & auto-pick a sensible default.
      - model in {'list','choose','?'}: list models & prompt (if TTY), else default.
      - model='<exact name>': use that model; with validate_model=True, verify & suggest on typos.

    IMPORTANT: A USER-PROVIDED API KEY IS REQUIRED (env/.env or Agent(api_key="...")).
    """

    def __init__(
        self,
        *,
        name: str,
        instructions: str,
        model: Optional[str] = "auto",
        tools: Optional[List[Tool]] = None,
        handoffs: Optional[List[Union["Agent", Handoff]]] = None,
        memory: Optional[Memory] = None,
        verbose: bool = True,
        max_iterations: int = 4,
        api_key: Optional[str] = None,      # USER must supply via env/.env or here
        validate_model: bool = False,
        include_experimental: bool = True,
    ) -> None:
        if not name:
            raise ValueError("Agent 'name' is required.")
        if not instructions:
            raise ValueError("Agent 'instructions' is required.")

        self.name = name
        self.instructions = instructions
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.memory = memory or Memory()

        # Resolve model (string only)
        self.model = self._resolve_model_param(
            model=model,
            include_experimental=include_experimental,
            validate_model=validate_model,
        )

        # Tools & handoffs
        self.tools: Dict[str, Tool] = {t.name: t for t in (tools or [])}
        self._handoffs: List[Handoff] = []
        for item in (handoffs or []):
            if isinstance(item, Handoff):
                self._handoffs.append(item)
            else:
                self._handoffs.append(handoff_factory(agent=item))
        for h in self._handoffs:
            ht = h.to_tool(self)
            self.tools[ht.name] = ht

        # --- STRICT API KEY ENFORCEMENT ---
        cfg_env = SDKConfig()
        resolved_key = api_key or cfg_env.api_key
        if not resolved_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required. Provide YOUR OWN key via environment/.env, "
                "or pass Agent(api_key='...')."
            )

        cfg = SDKConfig(
            model=self.model,
            api_key=resolved_key,
            temperature=cfg_env.temperature,
            max_iterations=self.max_iterations,
            verbose=self.verbose,
        )
        self.provider = GeminiProvider(cfg)  # Provider re-checks via require_key()

    # ---------- Public API ----------

    def register_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    class _AgentInvokeSchema(BaseModel):
        message: str

    def as_tool(self, *, tool_name: str, tool_description: str) -> Tool:
        outer = self

        class _AgentTool(Tool):
            name = tool_name
            description = tool_description
            schema = Agent._AgentInvokeSchema
            def run(self, **kwargs) -> str:
                msg = kwargs.get("message", "Please take over from here.")
                return outer.run(msg).content

        return _AgentTool()

    def run(self, user_message: str) -> AgentResult:
        steps: List[str] = []
        self.memory.remember("user", user_message)

        for i in range(self.max_iterations):
            prompt = self._build_prompt(user_message if i == 0 else "Continue.")
            model_out = self.provider.generate(prompt)
            steps.append(model_out)
            if self.verbose:
                log_step(f"LLM iteration {i + 1}", model_out)

            tool_call = self._maybe_parse_toolcall(model_out)
            if tool_call:
                observation = self._execute_tool(tool_call)
                self.memory.remember("assistant", model_out)
                self.memory.remember("tool", observation)
                if self.verbose:
                    log_step(f"Tool: {tool_call.tool}", observation)
                continue

            self.memory.remember("assistant", model_out)
            return AgentResult(content=model_out, steps=steps)

        fallback = "Reached iteration limit without final answer.\n\n" + (steps[-1] if steps else "")
        return AgentResult(content=fallback, steps=steps)

    # ---------- Internals: model selection ----------

    def _resolve_model_param(
        self,
        *,
        model: Optional[str],
        include_experimental: bool,
        validate_model: bool,
    ) -> str:
        available = list_gemini_models(include_experimental=include_experimental)

        def _print_models(av: List[str]) -> None:
            if not av:
                print("[Agent] No Gemini models available; falling back to 'models/gemini-1.5-pro'.")
                return
            print("\n[Agent] Available Gemini models:")
            for i, m in enumerate(av, 1):
                t = tag_model(m)
                meta = f"{t.get('family','')}, {t.get('speed','')}, {t.get('quality','')}"
                print(f"  {i:2d}. {m}   [{meta}]")
            print()

        if model is None or model == "" or str(model).lower() == "auto":
            _print_models(available)
            choice = best_default("balanced")
            print(f"[Agent] Using default model: {choice}")
            return choice

        lower = str(model).lower()
        if lower in {"list", "choose", "?"}:
            _print_models(available)
            if sys.stdin and sys.stdin.isatty():
                raw = input("[Agent] Select a model by number or paste a model name: ").strip()
                if raw.isdigit():
                    idx = int(raw)
                    if 1 <= idx <= len(available):
                        choice = available[idx - 1]
                        print(f"[Agent] Using: {choice}")
                        return choice
                    else:
                        print("[Agent] Invalid index; falling back to default.")
                elif raw:
                    candidate = raw
                    ok, suggestion, _ = validate_or_suggest(candidate, include_experimental=include_experimental)
                    if ok:
                        print(f"[Agent] Using: {candidate}")
                        return candidate
                    print(f"[Agent] '{candidate}' not found. Using suggestion: {suggestion}")
                    return suggestion or best_default("balanced")
            choice = best_default("balanced")
            print(f"[Agent] Non-interactive session. Using default: {choice}")
            return choice

        exact = str(model)
        if validate_model:
            ok, suggestion, avail = validate_or_suggest(exact, include_experimental=include_experimental)
            if not ok:
                hint = f" Did you mean '{suggestion}'?" if suggestion else ""
                raise ValueError(f"Model '{exact}' not available.{hint}\nAvailable: {avail}")
        return exact

    # ---------- Internals: runtime loop ----------

    def _execute_tool(self, call: ToolCall) -> str:
        tool = self.tools.get(call.tool)
        if not tool:
            return f"[Tool Error] Unknown tool: {call.tool}"
        try:
            kwargs = tool.parse_args(call.args)
            if hasattr(tool, "_invoke_with_ctx"):
                ctx = RunContextWrapper(current_agent=self, target_agent=self, memory=self.memory, steps=[])
                return tool._invoke_with_ctx(ctx, **kwargs)  # type: ignore[attr-defined]
            return tool.run(**kwargs)
        except Exception as e:
            return f"[Tool Error] {e}"

    def _build_prompt(self, user_message: str) -> str:
        system = (
            f"{BASE_SYSTEM_PROMPT}\n\n"
            f"[AGENT NAME]: {self.name}\n"
            f"[INSTRUCTIONS]: {self.instructions}\n"
            f"[MODEL]: {self.model}\n"
        )
        if self.tools:
            manifest_lines = ["Available TOOLS (use JSON with these exact names):"]
            for name, tool in self.tools.items():
                desc = (tool.description or "").strip().replace("\n", " ")
                manifest_lines.append(f"- {name}: {desc}")
            system += "\n" + "\n".join(manifest_lines)

        prefix = f"[SYSTEM]: {system}\n\n"
        history = self.memory.to_prompt()
        return prefix + history + ("\n\n[USER]: " + user_message)

    def _maybe_parse_toolcall(self, text: str) -> Optional[ToolCall]:
        tx = text.strip()
        if not (tx.startswith("{") and tx.endswith("}")):
            return None
        try:
            data = json.loads(tx)
            if isinstance(data, dict) and "tool" in data:
                return ToolCall(**data)
        except Exception:
            return None
        return None
