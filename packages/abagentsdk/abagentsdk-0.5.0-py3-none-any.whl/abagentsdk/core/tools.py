# abagent/core/tools.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Callable, get_type_hints, Awaitable, Union
from pydantic import BaseModel, ValidationError, create_model, Field
import inspect
import json
import asyncio

# Optional docstring parsing (best-effort)
try:
    from griffe import Docstring
except Exception:  # pragma: no cover
    Docstring = None  # type: ignore


# ---------- Base Tool API ----------

class Tool(ABC):
    name: str = "tool"
    description: str = ""
    schema: Optional[Type[BaseModel]] = None  # pydantic model describing args

    @abstractmethod
    def run(self, **kwargs) -> str:
        ...

    def parse_args(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if self.schema is None:
            return data
        try:
            # pydantic v2
            return self.schema(**data).model_dump()
        except ValidationError as e:
            raise ValueError(f"Invalid arguments for tool {self.name}: {e}")


class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any] = {}


# ---------- Function → Tool (decorator) ----------

def _schema_model_from_signature(fn: Callable, *, include_ctx: bool) -> Type[BaseModel]:
    """
    Build a Pydantic model from a function signature.
    Supports primitives, TypedDict, Pydantic models, etc.
    If include_ctx=True and the first parameter is ctx, it is ignored in schema.
    """
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)
    fields: Dict[str, tuple] = {}

    params = list(sig.parameters.values())
    start_idx = 1 if (include_ctx and params and params[0].name in {"ctx", "context"} ) else 0

    for param in params[start_idx:]:
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            raise TypeError(f"Variadic parameter '{param.name}' not supported in tool '{fn.__name__}'")
        ann = hints.get(param.name, Any)
        if param.default is inspect._empty:
            fields[param.name] = (ann, Field(...))
        else:
            fields[param.name] = (ann, Field(default=param.default))

    model_name = f"{fn.__name__}Params"
    return create_model(model_name, **fields)  # type: ignore[arg-type]


def _docstring_title_and_param_descriptions(fn: Callable, *, docstring_format: Optional[str]) -> tuple[str, Dict[str, str]]:
    """
    Try to extract tool description + per-arg descriptions from the docstring.
    Best-effort; if griffe is missing, fall back to fn.__doc__.
    """
    doc = (fn.__doc__ or "").strip()
    if not doc:
        return "", {}
    if Docstring is None:
        # crude split: first paragraph only
        first_line = doc.splitlines()[0].strip()
        return first_line, {}
    try:
        ds = Docstring(doc, parser=docstring_format)
        # Title/summary
        title = (ds.parsed[0].value.strip() if ds.parsed else "").split("\n")[0]
        # Arg descriptions (best-effort)
        param_desc: Dict[str, str] = {}
        for el in ds.parsed:
            if getattr(el, "kind", None) == "parameters":
                for name, _, desc in getattr(el, "parameters", []):
                    param_desc[name] = (desc or "").strip()
        return title or doc, param_desc
    except Exception:
        first_line = doc.splitlines()[0].strip()
        return first_line, {}


class FunctionTool(Tool):
    """
    A tool built around a function (sync or async).
    Two construction modes:
      1) via @function_tool decorator (auto schema + docstrings)
      2) manual: provide params_json_schema + async handler (see .from_schema)
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
        fn: Optional[Callable[..., Any]] = None,
        params_model: Optional[Type[BaseModel]] = None,
        expects_ctx: bool = False,
    ) -> None:
        self.name = name
        self.description = description
        self._fn = fn
        self.schema = params_model
        self._expects_ctx = expects_ctx

    # --- Decorator path: call the original Python function ---

    def _invoke_function(self, ctx: Any, **kwargs) -> Union[str, Any]:
        if self._fn is None:
            raise RuntimeError("No function bound to this FunctionTool.")
        fn = self._fn
        try:
            if inspect.iscoroutinefunction(fn):
                # run async function
                if self._expects_ctx:
                    return asyncio.run(fn(ctx, **kwargs))
                return asyncio.run(fn(**kwargs))
            # sync function
            if self._expects_ctx:
                return fn(ctx, **kwargs)
            return fn(**kwargs)
        except RuntimeError as e:
            # handle "asyncio.run() cannot be called from a running event loop"
            import nest_asyncio  # type: ignore
            nest_asyncio.apply()
            if self._expects_ctx:
                return asyncio.get_event_loop().run_until_complete(self._fn(ctx, **kwargs))  # type: ignore
            return asyncio.get_event_loop().run_until_complete(self._fn(**kwargs))  # type: ignore

    def run(self, **kwargs) -> str:
        # No context provided here; Agent will route context-aware calls (see Agent._execute_tool)
        result = self._invoke_function(None, **kwargs)
        return result if isinstance(result, str) else json.dumps(result) if isinstance(result, (dict, list)) else str(result)

    # --- Agent will call this if a ctx is available (preferred) ---
    def _invoke_with_ctx(self, ctx: Any, **kwargs) -> str:
        result = self._invoke_function(ctx, **kwargs)
        return result if isinstance(result, str) else json.dumps(result) if isinstance(result, (dict, list)) else str(result)

    # --- Manual construction path (schema as JSON + async handler) ---

    @classmethod
    def from_schema(
        cls,
        *,
        name: str,
        description: str,
        params_json_schema: Dict[str, Any],
        on_invoke_tool: Callable[[Any, str], Awaitable[str]],
    ) -> "FunctionTool":
        """
        Build a FunctionTool when you already have a JSON schema and an async handler.
        Handler receives (ctx, args_json) and must return a string.
        """
        # Make a minimal pydantic model from json schema (v2 parse_raw)
        class _Schema(BaseModel):
            class Config:
                json_schema_extra = params_json_schema

            @classmethod
            def model_json_schema(cls):
                return params_json_schema

        tool = cls(name=name, description=description, params_model=_Schema, expects_ctx=True)

        async def _adapter(ctx: Any, **parsed_kwargs) -> str:
            args_json = json.dumps(parsed_kwargs)
            return await on_invoke_tool(ctx, args_json)

        tool._fn = _adapter  # type: ignore
        return tool


def function_tool(
    *,
    name_override: Optional[str] = None,
    description_override: Optional[str] = None,
    use_docstring_info: bool = True,
    docstring_format: Optional[str] = None,  # 'google' | 'numpy' | 'sphinx' (best-effort)
    expects_ctx: bool = False,
):
    """
    Decorator that converts a function into a FunctionTool.
    - If expects_ctx=True, the function may accept first param named 'ctx' or 'context'
    - Tool name defaults to function name; description from first docstring line
    - Input schema from function signature & type hints (ctx param is ignored)
    """
    def _wrap(fn: Callable[..., Any]):
        params_model = _schema_model_from_signature(fn, include_ctx=expects_ctx)
        title, _arg_desc = ("", {})
        if use_docstring_info:
            title, _arg_desc = _docstring_title_and_param_descriptions(fn, docstring_format=docstring_format)
        name = name_override or fn.__name__
        desc = (description_override or title or (fn.__doc__ or "")).strip()
        t = FunctionTool(name=name, description=desc, fn=fn, params_model=params_model, expects_ctx=expects_ctx)
        # attach the tool instance for registration
        setattr(fn, "as_tool", t)
        return fn
    return _wrap
