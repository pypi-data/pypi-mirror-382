# abagentsdk/cli.py
from __future__ import annotations

import argparse
import os
import runpy
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from .utils.silence import install_silence
install_silence()

from . import Agent, Memory

console = Console()
BANNER = "[bold cyan]ABZ Agent SDK CLI[/] — type 'q' to quit."

# ----------------------------
# Helpers
# ----------------------------

def _ensure_api_key() -> str:
    """
    Reads GEMINI_API_KEY from env; if missing, prompts.
    We DO NOT support --api-key flag.
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        console.print("[yellow]GEMINI_API_KEY not found in environment.[/]")
        key = getpass("Enter your Gemini API key: ").strip()
    if not key:
        raise SystemExit("No API key provided. Set GEMINI_API_KEY or run `abagent --setup`.")
    os.environ["GEMINI_API_KEY"] = key  # make available to child scripts
    return key


def _run_script(path: str) -> int:
    file = Path(path)
    if not file.exists():
        console.print(f"[red]File not found:[/] {path}")
        return 1
    _ensure_api_key()  # only prompt after we know the file exists
    runpy.run_path(str(file), run_name="__main__")
    return 0


def _repl(name: str, instructions: str, model: str, verbose: bool, max_iter: int) -> int:
    _ensure_api_key()
    agent = Agent(
        name=name or "CLI Agent",
        instructions=instructions or "Be concise and helpful.",
        model=model or "auto",
        memory=Memory(),
        verbose=verbose,          # only prints iterations/tools when True
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

# ----------------------------
# Project Scaffolding: abagent --setup
# ----------------------------
AGENT_FILE_TEMPLATE = """from dotenv import load_dotenv
import os
from abagentsdk import Agent, Memory

# Load .env to populate GEMINI_API_KEY
load_dotenv()

def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY missing. Add it to .env or your environment.")

    agent = Agent(
        name={agent_name!r},
        instructions={instructions!r},
        model={model!r},
        memory=Memory(),
        verbose=False,
    )

    print("==== {agent_name} (ABZ Agent SDK) ====")
    while True:
        user = input("You > ").strip()
        if not user:
            continue
        if user.lower() in {{'q', 'quit', 'exit'}}:
            print("Bye!")
            break
        res = agent.run(user)
        print("Agent >", res.content)

if __name__ == "__main__":
    main()
"""

README_SNIPPET = """# ABZ Agent SDK quickstart

## Setup

1) Ensure you have Python 3.10+ and a virtual environment.
2) Install the SDK:

```bash
pip install abagentsdk
```
"""


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="abagent")
    parser.add_argument("--setup", action="store_true", help="Create a starter agent file")
    parser.add_argument("--run", help="Run a user script (path)")
    parser.add_argument("--repl", action="store_true", help="Start an interactive REPL agent")
    parser.add_argument("--name", help="Agent name for REPL/setup")
    parser.add_argument("--instructions", help="Initial system instructions for the agent")
    parser.add_argument("--model", help="Model to use (provider-specific)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--max-iterations", type=int, default=4, help="Max agent iterations")

    args = parser.parse_args(argv)

    if args.setup:
        out = Path("abagent.py")
        if out.exists():
            console.print(f"[yellow]{out} already exists. Skipping.[/]")
            return 1
        content = AGENT_FILE_TEMPLATE.format(
            agent_name=args.name or "MyAgent",
            instructions=args.instructions or "Be concise and helpful.",
            model=args.model or "auto",
        )
        out.write_text(content)
        console.print(f"[green]Wrote {out}.[/]")
        return 0

    if args.run:
        return _run_script(args.run)

    if args.repl:
        return _repl(args.name or "CLI Agent", args.instructions or "Be concise.", args.model or "auto", args.verbose, args.max_iterations)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())