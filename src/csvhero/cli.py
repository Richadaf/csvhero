from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn
from rich.table import Table

from . import __version__
from .core import (
    CSVProfile,
    analyze_csv,
    discover_csvs,
    format_shape_markdown,
    readme_path_for,
    write_readme,
)
from .templates import banner

app = typer.Typer(add_completion=False, help="Write shape readmes for your CSV files.")
console = Console()


@app.command("scan")
def scan(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Recurse into subfolders."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing readmes."),
    encoding: str = typer.Option("utf-8", help="File encoding to use when reading CSVs."),
) -> None:
    """Walk a folder, greet every CSV, and leave a small README calling card."""
    banner(console)

    csvs = list(discover_csvs(folder, recursive=recursive))
    if not csvs:
        console.print(":magnifying_glass_tilted_right: No CSV files found.", style="yellow")
        raise typer.Exit(code=0)

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )

    profiles: list[CSVProfile] = []
    skipped = 0
    written = 0
    with progress:
        task_id = progress.add_task("Scanning CSVs", total=len(csvs))
        for csv_path in csvs:
            try:
                profile = analyze_csv(csv_path, encoding=encoding)
                profiles.append(profile)

                md = format_shape_markdown(profile, __version__)
                dest = readme_path_for(csv_path)
                try:
                    write_readme(md, dest, overwrite=overwrite)
                    written += 1
                except FileExistsError:
                    skipped += 1
            except Exception as exc:  # keep the parade moving
                console.print(f"[red]Failed:[/red] {csv_path.name} — {exc}")
            finally:
                progress.advance(task_id)

    # summary table
    table = Table(title="csvhero summary", expand=False)
    table.add_column("stat", justify="left", style="cyan")
    table.add_column("value", justify="right", style="white")
    table.add_row("csv files seen", str(len(csvs)))
    table.add_row("rows across all csvs", str(sum(p.rows for p in profiles)))
    table.add_row("readmes written", str(written))
    table.add_row("readmes skipped (exists)", str(skipped))
    console.print(table)

    console.print("[green]Done.[/green] Carry on. :check_mark_button:")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
