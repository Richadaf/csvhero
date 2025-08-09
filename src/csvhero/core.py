from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclass(slots=True, frozen=True)
class CSVProfile:
    """A small postcard from a CSV.

    rows:    number of data records (header not included)
    columns: ordered list of column names, exactly as found
    path:    absolute filesystem location to the CSV
    """

    path: Path
    rows: int
    columns: List[str]


def discover_csvs(root: Path, recursive: bool = False) -> Iterable[Path]:
    """Walk a folder and yield *.csv files.

    The function is quiet and careful: it ignores non-files and respects
    the user's wish for recursion.
    """
    pattern = "**/*.csv" if recursive else "*.csv"
    yield from (p for p in root.glob(pattern) if p.is_file())


def sniff_dialect(sample: str) -> Optional[csv.Dialect]:
    """Try to guess the dialect from a small sample; return None if uncertain."""
    try:
        return csv.Sniffer().sniff(sample)
    except Exception:
        return None


def analyze_csv(path: Path, encoding: str = "utf-8") -> CSVProfile:
    """Read just enough to understand the CSV's shape.

    We peek at a small sample to guess the dialect, then stream rows to count
    without ever loading the entire file into memory. Simple, steady, kind.
    """
    # First, take a small sip to sniff dialects.
    with path.open("r", encoding=encoding, errors="replace", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = sniff_dialect(sample) or csv.excel
        reader = csv.reader(f, dialect=dialect)

        # Header is our north star.
        try:
            header = next(reader)
        except StopIteration:
            # Empty file: no header, no rows.
            return CSVProfile(path=path.resolve(), rows=0, columns=[])

        # Count rows, gently.
        row_count = sum(1 for _ in reader)
        return CSVProfile(path=path.resolve(), rows=row_count, columns=list(header))


def readme_path_for(csv_path: Path) -> Path:
    """orders.csv -> orders.readme.md (sibling file)."""
    return csv_path.with_suffix("").with_suffix(".readme.md")


def format_shape_markdown(profile: CSVProfile, tool_version: str) -> str:
    """Render a uniform, friendly README with the CSV's shape."""
    filename = profile.path.name
    col_count = len(profile.columns)
    cols_inline = ", ".join(f"`{c}`" for c in profile.columns) if profile.columns else "_(none)_"

    return f"""# {filename} — CSV Shape

- **Rows (excluding header):** {profile.rows}
- **Columns ({col_count}):** {cols_inline}

---

_This file was sketched by **csvhero {tool_version}**.  
It looks only, never lingers; it counts, then quietly leaves a note._
"""


def write_readme(markdown: str, dest: Path, overwrite: bool = False) -> None:
    """Write the README, refusing to trample unless told otherwise."""
    if dest.exists() and not overwrite:
        raise FileExistsError(f"README already exists: {dest}")
    dest.write_text(markdown, encoding="utf-8")
