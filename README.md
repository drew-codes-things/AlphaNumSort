<div align="center">

# Alpha-Numerical-Sorter

**A Python CLI tool for sorting text files alphabetically, numerically, naturally, or by line length.**

[![Python](https://img.shields.io/badge/python-3.8+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

</div>

---

## Overview

Alpha-Numerical-Sorter reads a plain-text file line by line, applies one of four sort modes with optional filters, and writes the result to a new file or back in-place. It runs in two modes: an interactive prompt-driven interface for everyday use, and a non-interactive `--file` CLI mode for scripting and automation. Supported file types in the browser are `.txt`, `.csv`, `.log`, `.md`, plus any additional extensions passed via `--ext`.

---

## Sort Modes

| Mode | Flag | Behaviour |
|---|---|---|
| Alphabetical | `a` / `alpha` | Case-insensitive A-Z sort. Optionally capitalises the first letter of each line. |
| Natural | `n` / `natural` | Human sort: `file2` sorts before `file10`. Default mode. |
| Numeric | `u` / `numeric` | Sorts by the first number found in each line. Lines with no number sort to the end. |
| Length | `l` / `length` | Sorts by the character length of each line (trailing whitespace ignored). |

All modes support ascending (`a`) and descending (`d`) order.

---

## Options

| Option | Description |
|---|---|
| `--file PATH` | Input file path. Enables non-interactive CLI mode. |
| `--mode MODE` | Sort mode: `alpha`, `natural`, `numeric`, `length` (default: `natural`) |
| `--order a\|d` | Sort order: `a` = ascending, `d` = descending (default: `a`) |
| `--output PATH` | Output file path (default: `<input>_sorted.<ext>`) |
| `--in-place` | Overwrite the source file instead of creating a new output file |
| `--remove-dupes` | Remove duplicate lines (case-insensitive comparison) |
| `--remove-empty` | Remove blank lines before sorting |
| `--capitalise` | Capitalise the first letter of each line (alpha mode only) |
| `--ext EXT [...]` | Additional file extensions to show in the interactive file browser |
| `--column N` | Sort a CSV file by this 1-based column instead of by the whole line |
| `--no-header` | With `--column`: treat the first CSV row as data, not a header to keep on top |

---

## Usage

### Interactive mode

Run without `--file` to launch the prompt-driven interface:

```bash
python main.py
```

The tool will ask you to select a folder, choose a file, pick a sort mode, set order, and configure filters step by step. Enter `b` at any prompt to go back.

### CLI mode

Pass `--file` to sort non-interactively:

```bash
python main.py --file my_list.txt --mode alpha --order a --remove-dupes
```

Sort a file numerically in descending order, overwriting in-place:

```bash
python main.py --file scores.txt --mode numeric --order d --in-place
```

Sort with a custom output path and extra extensions in the browser:

```bash
python main.py --file data.tsv --mode natural --output sorted_data.tsv --ext tsv nfo
```

Sort a CSV by its second column numerically, descending (the header row is kept on top):

```bash
python main.py --file scores.csv --column 2 --mode numeric --order d
```

---

## Output

After sorting, the tool reports the line count before and after, and how many lines were removed by deduplication or empty-line filtering:

```
  Saved -> my_list_sorted.txt
  Lines: 120 in, 97 out (23 removed by dedup/empty filter)
```

---

## Notes

- Numeric mode assigns `float('inf')` to lines containing no number, so they always appear at the end in ascending order and at the start in descending order.
- Natural sort splits each line on digit boundaries so `file2` < `file10` < `file100`.
- Deduplication is case-insensitive and strip-based: `Apple` and `apple ` are treated as the same line.
- The `test-file-gen/` directory contains scripts for generating test files.

---

---

## Install as a command (pipx)

Install this folder as a CLI so it is available on your PATH:

```bash
pipx install .
alpha-numerical-sorter
```


## Get the Code

Clone with git:

```bash
git clone https://github.com/drew-codes-things/AlphaNumSort.git
```

Or with the [GitHub CLI](https://cli.github.com/):

```bash
gh repo clone drew-codes-things/AlphaNumSort
```

## License

MIT - made by [Drew](https://github.com/drew-codes-things)
