# abagent/core/agent.py
from __future__ import annotations

import asyncio
import inspect
import json
import re
import sys
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Type, Union

from pydantic import BaseModel, TypeAdapter, ValidationError

from .memory import Memory
from .tools import Tool, ToolCall
from .handoffs import Handoff, handoff as handoff_factory, RunContextWrapper
from .guardrails import (
    run_input_guardrails,
    run_output_guardrails,
)
from ..config import SDKConfig
from ..providers.gemini import GeminiProvider
from ..utils.logging import log_step

# Optional model catalog helpers (SDK still works if this module isn't present)
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
    "If no tool is needed, reply with the final answer.\n"
    "When calling a tool, use ONLY the exact names from the tools manifest provided below."
)

# ---- Dynamic instructions type ----
InstructionsFn = Callable[[RunContextWrapper[Any], "Agent"], Union[str, Awaitable[str]]]


class AgentResult:
    def __init__(self, content: str, steps: List[str], parsed: Any = None):
        self.content = content          # raw LLM text
        self.steps = steps              # intermediate outputs
        self.parsed = parsed            # optional structured object (when output_type is set)


class Agent:
    """
    Gemini-only Agent with tools, handoffs, memory,
    **structured outputs** (output_type), **guardrails**, and **dynamic instructions**.

    Required:
      - name: str
      - instructions: str | (ctx, agent) -> str | awaitable str

    Optional:
      - model: str | 'auto' | 'choose' | '?'
      - tools: list[Tool]
      - handoffs: list[Agent | Handoff]
      - memory: Memory
      - verbose: bool
      - max_iterations: int
      - api_key: Optional[str]
      - validate_model: bool
      - include_experimental: bool
      - output_type: Optional[Type]
      - input_guardrails: Sequence[_Guardrail[str]]
      - output_guardrails: Sequence[_Guardrail[Any]]
    """

    def __init__(
        self,
        *,
        name: str,
        instructions: Union[str, InstructionsFn],   # 👈 dynamic-capable
        model: Optional[str] = "auto",
        tools: Optional[List[Tool]] = None,
        handoffs: Optional[List[Union["Agent", Handoff]]] = None,
        memory: Optional[Memory] = None,
        verbose: bool = True,
        max_iterations: int = 4,
        api_key: Optional[str] = None,      # USER must supply via env/.env or here
        validate_model: bool = False,
        include_experimental: bool = True,
        output_type: Optional[Type[Any]] = None,
        input_guardrails: Optional[Sequence[Any]] = None,
        output_guardrails: Optional[Sequence[Any]] = None,
    ) -> None:
        if not name:
            raise ValueError("Agent 'name' is required.")
        if instructions is None or (isinstance(instructions, str) and instructions.strip() == ""):
            raise ValueError("Agent 'instructions' is required (string or function).")

        self.name = name
        self._instructions_src: Union[str, InstructionsFn] = instructions  # store source
        self.instructions: str = ""   # effective string resolved per-run
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.memory = memory or Memory()
        self.output_type: Optional[Type[Any]] = output_type
        self._type_adapter: Optional[TypeAdapter[Any]] = (
            TypeAdapter(output_type) if output_type is not None else None
        )
        self.input_guardrails = list(input_guardrails or [])
        self.output_guardrails = list(output_guardrails or [])

        # Resolve model string (provider built later)
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

    def run(self, user_message: str, *, context: Any = None) -> AgentResult:
        steps: List[str] = []

        # Build a context wrapper (for guardrails + dynamic instructions)
        ctx_for_run = RunContextWrapper(
            current_agent=self,
            target_agent=self,
            memory=self.memory,
            steps=steps,
            context=context,
        )

        # --- INPUT GUARDRAILS (only when this agent is the entry point) ---
        if self.input_guardrails:
            run_input_guardrails(
                guards=self.input_guardrails,
                ctx=ctx_for_run,
                agent=self,
                user_input=user_message,
            )

        # Remember the user input
        self.memory.remember("user", user_message)

        for i in range(self.max_iterations):
            # resolve instructions dynamically each iteration (so context updates can reflect)
            effective_instructions = self._resolve_instructions(ctx_for_run)
            prompt = self._build_prompt(
                user_message if i == 0 else "Continue.",
                effective_instructions=effective_instructions,
            )

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

            # Final answer text
            self.memory.remember("assistant", model_out)

            if self._type_adapter is None:
                # --- OUTPUT GUARDRAILS on plain text ---
                if self.output_guardrails:
                    run_output_guardrails(
                        guards=self.output_guardrails,
                        ctx=ctx_for_run,
                        agent=self,
                        final_output=model_out,
                    )
                return AgentResult(content=model_out, steps=steps)

            # structured output mode: parse & validate into output_type
            parsed = self._coerce_to_output_type(model_out)

            # --- OUTPUT GUARDRAILS on structured output ---
            if self.output_guardrails:
                run_output_guardrails(
                    guards=self.output_guardrails,
                    ctx=ctx_for_run,
                    agent=self,
                    final_output=parsed,
                )
            return AgentResult(content=model_out, steps=steps, parsed=parsed)

        fallback = (
            "Reached iteration limit without final answer. Here's the latest output:\n\n"
            + (steps[-1] if steps else "")
        )
        return AgentResult(content=fallback, steps=steps)

    # ---------- Dynamic instructions ----------

    def _resolve_instructions(self, ctx: RunContextWrapper[Any]) -> str:
        """
        Resolve dynamic instructions. Supports:
          - static string
          - sync function: (ctx, agent) -> str
          - async function: async (ctx, agent) -> str
        """
        src = self._instructions_src
        if isinstance(src, str):
            self.instructions = src
            return src

        fn = src
        try:
            if inspect.iscoroutinefunction(fn):
                try:
                    text = asyncio.run(fn(ctx, self))
                except RuntimeError:
                    # already in a loop (e.g., notebook) -> use nest_asyncio
                    import nest_asyncio  # type: ignore
                    nest_asyncio.apply()
                    loop = asyncio.get_event_loop()
                    text = loop.run_until_complete(fn(ctx, self))
            else:
                text = fn(ctx, self)
            if not isinstance(text, str) or text.strip() == "":
                raise ValueError("Dynamic instructions function must return a non-empty string.")
            self.instructions = text
            return text
        except Exception as e:
            raise RuntimeError(f"Dynamic instructions function raised: {e}") from e

    # ---------- Internals: output typing ----------

    def _output_schema_json(self) -> Optional[str]:
        if self._type_adapter is None:
            return None
        try:
            schema = self._type_adapter.json_schema()
            return json.dumps(schema, ensure_ascii=False)
        except Exception:
            return None

    def _coerce_to_output_type(self, text: str) -> Any:
        assert self._type_adapter is not None
        # 1) try direct JSON
        try:
            return self._type_adapter.validate_json(text)
        except Exception:
            pass
        # 2) try extracting JSON blob
        blob = _extract_json_blob(text)
        if blob is not None:
            try:
                return self._type_adapter.validate_json(blob)
            except ValidationError as ve:
                preview = blob[:400]
                raise ValueError(
                    f"Structured output validation failed.\n"
                    f"Expected schema: {self._short_schema_hint()}\n"
                    f"Got (truncated): {preview}\n\n{ve}"
                ) from ve
        # 3) fail
        preview = text[:400]
        raise ValueError(
            "Model did not return valid JSON for the requested output_type.\n"
            f"Expected schema: {self._short_schema_hint()}\n"
            f"Raw (truncated): {preview}"
        )

    def _short_schema_hint(self) -> str:
        js = self._output_schema_json()
        return (js[:240] + "…") if js and len(js) > 240 else (js or "<unknown>")

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

    def _build_prompt(self, user_message: str, *, effective_instructions: str) -> str:
        """
        Compile a chat-style prompt with:
        - system + dynamic/ static agent instructions
        - tools manifest (including handoffs)
        - optional structured output schema + strict JSON return instruction
        """
        system = (
            f"{BASE_SYSTEM_PROMPT}\n\n"
            f"[AGENT NAME]: {self.name}\n"
            f"[INSTRUCTIONS]: {effective_instructions}\n"
            f"[MODEL]: {self.model}\n"
        )

        if self.tools:
            manifest_lines = ["Available TOOLS (use JSON with these exact names):"]
            for name, tool in self.tools.items():
                desc = (tool.description or "").strip().replace("\n", " ")
                manifest_lines.append(f"- {name}: {desc}")
            system += "\n" + "\n".join(manifest_lines)

        # Structured output guidance
        if self._type_adapter is not None:
            schema_json = self._output_schema_json()
            system += (
                "\n\n[STRUCTURED OUTPUT]:\n"
                "Return ONLY valid JSON for the final answer (no markdown, no prose).\n"
            )
            if schema_json:
                system += f"Target JSON schema (informative):\n{schema_json}\n"
            system += "If you cannot fully satisfy the schema, return your best-effort JSON matching the schema keys.\n"

        prefix = f"[SYSTEM]: {system}\n\n"
        history = self.memory.to_prompt()
        user_tail = user_message if self._type_adapter is None else (user_message + "\n\nReturn ONLY the final JSON.")
        return prefix + history + ("\n\n[USER]: " + user_tail)

    def _maybe_parse_toolcall(self, text: str) -> Optional[ToolCall]:
        tx = text.strip()
        if not (tx.startswith("{") and tx.endswith("}")):
            return None
        try:
            data = json.loads(tx)
            if isinstance(data, dict) and "tool" in data:
                return ToolCall(**data)  # pydantic validation
        except Exception:
            return None
        return None


# --------- small helper (module level) ---------

_JSON_OBJECT_OR_ARRAY = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)

def _extract_json_blob(text: str) -> Optional[str]:
    m = _JSON_OBJECT_OR_ARRAY.search(text.strip())
    if not m:
        return None
    return m.group(1)
