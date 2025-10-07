from rich.console import Console
from rich.panel import Panel


console = Console()


def log_step(title: str, body: str) -> None:
    console.print(Panel.fit(body, title=title))