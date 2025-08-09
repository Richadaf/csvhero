# csvhero

A tiny, beautiful CLI that scans a folder for `*.csv` and writes a sibling `filename.readme.md`
describing the CSV’s shape (row count, columns). Uniform format, friendly output.

## install (editable)

```bash
pip install -e .
````

## usage

```bash
csvhero scan /path/to/folder
csvhero scan data/ --recursive
csvhero scan data/ --overwrite
csvhero scan data/ --encoding utf-8
```

Each `*.csv` gets a `./<name>.readme.md` next to it.
Rows are counted excluding the header; columns are taken from the first row.

### notes on consistency & “shape”
- “Rows” means **data rows only** (header excluded) for intuitive shapes.
- README format is fixed via `format_shape_markdown(...)` so every file matches exactly.
- We detect CSV dialects lightly; if sniffing fails, we fall back to Excel dialect (commas).

If you want me to add unit tests, CI, or a `--format table|bullets` option, say the word and I’ll layer it in.
