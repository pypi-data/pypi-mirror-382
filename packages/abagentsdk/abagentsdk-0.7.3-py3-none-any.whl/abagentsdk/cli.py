# abagent/cli.py
from __future__ import annotations

import argparse
import os
import runpy
import sys
from getpass import getpass
from typing import Optional

from rich.console import Console
from rich.panel import Panel

# import public API
from . import Agent, Memory

console = Console()

BANNER = "[bold cyan]ABZ Agent SDK CLI[/] — type 'q' to quit."


def _ensure_api_key(passed: Optional[str]) -> str:
    # Priority: --api-key flag > GEMINI_API_KEY env > prompt
    key = passed or os.getenv("GEMINI_API_KEY")
    if not key:
        key = getpass("Enter your Gemini API key: ").strip()
    if not key:
        raise SystemExit("No API key provided. Use --api-key or set GEMINI_API_KEY.")
    # make it available to user scripts as well
    os.environ["GEMINI_API_KEY"] = key
    return key


def _run_script(path: str, api_key: Optional[str]) -> int:
    _ensure_api_key(api_key)  # sets env so user code can read it
    if not os.path.exists(path):
        console.print(f"[red]File not found:[/] {path}")
        return 1
    # Execute the given Python file as __main__
    runpy.run_path(path, run_name="__main__")
    return 0


def _repl(name: str, instructions: str, model: str, api_key: Optional[str], verbose: bool, max_iter: int) -> int:
    key = _ensure_api_key(api_key)

    agent = Agent(
        name=name or "CLI Agent",
        instructions=instructions or "Be concise and helpful.",
        model=model or "auto",
        api_key=key,
        memory=Memory(),
        verbose=verbose,
        max_iterations=max_iter,
    )

    console.print(Panel(BANNER, expand=False))
    while True:
        try:
            msg = input(f"You ({agent.name}) > ").strip()
            if not msg:
                continue
            if msg.lower() in {"q", "quit", "exit"}:
                console.print("[green]Bye![/]")
                return 0
            res = agent.run(msg)
            console.print(Panel(res.content, title="Agent"))
        except KeyboardInterrupt:
            console.print("\n[green]Bye![/]")
            return 0
        except Exception as e:
            console.print(f"[red]Error:[/] {e}")
            if verbose:
                raise
    # unreachable
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="abagent",
        description="ABZ Agent SDK CLI — run a script or start a quick REPL.",
    )
    parser.add_argument("file", nargs="?", help="Python file to run (optional).")
    parser.add_argument("--api-key", help="Your Gemini API key (else reads GEMINI_API_KEY or prompts).")
    parser.add_argument("--repl", action="store_true", help="Start an interactive REPL instead of running a file.")
    parser.add_argument("--name", default="CLI Agent", help="Agent name for REPL mode.")
    parser.add_argument("--instructions", default="Be concise and helpful.", help="Agent instructions for REPL mode.")
    parser.add_argument("--model", default="auto", help="Gemini model id (or 'auto').")
    parser.add_argument("--max-iter", type=int, default=4, help="Max iterations per turn (REPL mode).")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging.")

    args = parser.parse_args(argv)

    # mode selection
    if args.repl or not args.file:
        return _repl(
            name=args.name,
            instructions=args.instructions,
            model=args.model,
            api_key=args.api_key,
            verbose=args.verbose,
            max_iter=args.max_iter,
        )
    else:
        return _run_script(args.file, api_key=args.api_key)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
