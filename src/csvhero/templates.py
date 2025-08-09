from __future__ import annotations

from rich.console import Console
from rich.panel import Panel


def banner(console: Console) -> None:
    console.print(
        Panel.fit(
            "[b]csvhero[/b] — small tool, neat readmes.",
            border_style="green",
            padding=(0, 2),
        )
    )
