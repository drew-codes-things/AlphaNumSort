import argparse
import csv
import os
import re
import sys


def clean_path(path):
    return path.strip().strip('"').strip("'")


def natural_key(s):
    """Key for natural/human sort: 'file2' < 'file10'."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def list_supported_files(folder, extra_exts=()):
    base_exts = ('.txt', '.csv', '.log', '.md')
    supported = base_exts + tuple(
        (e if e.startswith('.') else '.' + e).lower() for e in extra_exts
    )
    return sorted(
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith(supported)
    )


def ask(prompt, valid):
    valid_lower = [v.lower() for v in valid]
    while True:
        ans = input(prompt).strip().lower()
        if ans == 'b':
            return None
        if ans in valid_lower:
            return ans
        print(f"  Please enter one of: {', '.join(valid)} (or 'b' to go back)")


def choose_file(files):
    print()
    for i, f in enumerate(files, 1):
        print(f"  {i:>2}. {f}")
    print()
    while True:
        raw = input("Select file number (or 'b' to quit): ").strip().lower()
        if raw == 'b':
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(files):
            return files[int(raw) - 1]
        print("  Invalid choice.")


def choose_folder():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n  Default folder: {script_dir}")
    use_custom = ask("  Use a different folder? y/n: ", ['y', 'n'])
    if use_custom is None:
        return None
    if use_custom == 'y':
        raw = input("  Enter folder path: ")
        folder = clean_path(raw)
        if not os.path.isdir(folder):
            print(f"  Folder not found: {folder}")
            return None
        return folder
    return script_dir


def sort_lines(lines, mode, reverse, skip_empty, dedupe, capitalise=False):
    if skip_empty:
        lines = [l for l in lines if l.strip()]
    if dedupe:
        seen = set()
        unique = []
        for l in lines:
            key = l.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(l)
        lines = unique

    if mode == 'alpha':
        lines = sorted(lines, key=lambda x: x.lower(), reverse=reverse)
        if capitalise:
            lines = [l[0].upper() + l[1:] if l.strip() else l for l in lines]

    elif mode == 'natural':
        lines = sorted(lines, key=lambda x: natural_key(x), reverse=reverse)

    elif mode == 'numeric':
        def num_key(line):
            """
            Sort key for numeric mode.

            Lines that contain no number are assigned float('inf') so they
            always sort to the END in ascending order and to the BEGINNING
            in descending order. This is intentional: numberless lines are
            treated as 'beyond the last numeric entry'. If you want them at
            the start instead, invert the sentinel to float('-inf').
            """
            m = re.search(r'-?\d+(\.\d+)?', line)
            return float(m.group()) if m else float('inf')
        lines = sorted(lines, key=num_key, reverse=reverse)

    elif mode == 'length':
        lines = sorted(lines, key=lambda x: len(x.rstrip()), reverse=reverse)

    return lines


def cell_key(mode):
    """Return a sort-key function for a single CSV cell value, matching the line modes."""
    def numeric(v):
        m = re.search(r'-?\d+(\.\d+)?', v)
        return float(m.group()) if m else float('inf')
    return {
        'alpha':   lambda v: v.lower(),
        'natural': natural_key,
        'numeric': numeric,
        'length':  lambda v: len(v.rstrip()),
    }[mode]


def sort_csv_by_column(input_path, output_path, column, mode, reverse,
                       skip_empty, dedupe, has_header=True):
    try:
        with open(input_path, 'r', encoding='utf-8', newline='') as f:
            rows = list(csv.reader(f))
        if not rows:
            print("  Error: CSV file is empty.")
            return False

        original_count = len(rows)
        header = rows.pop(0) if has_header else None
        idx = column - 1

        def cell(r):
            return r[idx] if idx < len(r) else ''

        if skip_empty:
            rows = [r for r in rows if cell(r).strip()]
        if dedupe:
            seen = set()
            unique = []
            for r in rows:
                key = tuple(r)
                if key not in seen:
                    seen.add(key)
                    unique.append(r)
            rows = unique

        keyf = cell_key(mode)
        rows.sort(key=lambda r: keyf(cell(r)), reverse=reverse)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if header is not None:
                writer.writerow(header)
            writer.writerows(rows)

        out_count = len(rows) + (1 if header is not None else 0)
        removed = original_count - out_count
        print(f"\n  Saved -> {output_path}")
        print(f"  Rows: {original_count} in, {out_count} out (sorted by column {column})", end="")
        if removed:
            print(f" ({removed} removed by dedup/empty filter)", end="")
        print()
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def sort_file(input_path, output_path, mode, reverse, skip_empty, dedupe, capitalise=False):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = [l.rstrip('\n') for l in f]

        original_count = len(lines)
        sorted_lines = sort_lines(lines, mode, reverse, skip_empty, dedupe, capitalise)

        with open(output_path, 'w', encoding='utf-8') as f:
            for l in sorted_lines:
                f.write(l + '\n')

        removed = original_count - len(sorted_lines)
        print(f"\n  Saved -> {output_path}")
        print(f"  Lines: {original_count} in, {len(sorted_lines)} out", end="")
        if removed:
            print(f" ({removed} removed by dedup/empty filter)", end="")
        print()
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


MODES = {
    'a': ('alpha',   'Alphabetical (A-Z)'),
    'n': ('natural', 'Natural / human sort  (file2 before file10)'),
    'u': ('numeric', 'Numeric  (by first number found in each line; lines with no numbers sort to end)'),
    'l': ('length',  'By line length'),
}

MODE_NAME_MAP = {
    'alpha': 'alpha', 'a': 'alpha',
    'natural': 'natural', 'n': 'natural',
    'numeric': 'numeric', 'u': 'numeric',
    'length': 'length', 'l': 'length',
}


def run_cli(args):
    """Non-interactive mode when --file is supplied."""
    input_path = clean_path(args.file)
    if not os.path.isfile(input_path):
        print(f"  Error: file not found: {input_path}")
        sys.exit(1)

    mode = MODE_NAME_MAP.get(args.mode)
    if not mode:
        print(f"  Error: unknown mode '{args.mode}'. Choose: alpha, natural, numeric, length")
        sys.exit(1)

    reverse = (args.order == 'd')

    if args.in_place:
        output_path = input_path
    elif args.output:
        output_path = clean_path(args.output)
    else:
        base, ext = os.path.splitext(input_path)
        output_path = base + '_sorted' + ext

    if args.column is not None:
        if args.column < 1:
            print("  Error: --column must be 1 or greater.")
            sys.exit(1)
        sort_csv_by_column(
            input_path, output_path, args.column, mode, reverse,
            args.remove_empty, args.remove_dupes, has_header=not args.no_header,
        )
        return

    sort_file(
        input_path, output_path, mode, reverse,
        args.remove_empty, args.remove_dupes, args.capitalise,
    )


def run_interactive(extra_exts=()):
    """Original interactive loop."""
    print("\n  Drew's Alpha-Numerical Sorter")
    print("  " + "-" * 30)
    print("  Tip: run with --file to skip the prompts. See --help for options.")

    try:
        while True:
            folder = choose_folder()
            if folder is None:
                break

            files = list_supported_files(folder, extra_exts=extra_exts)
            if not files:
                exts_shown = ".txt .csv .log .md"
                if extra_exts:
                    exts_shown += " " + " ".join(
                        (e if e.startswith(".") else "." + e) for e in extra_exts
                    )
                print(f"  No supported files found ({exts_shown}).")
                continue

            print(f"  Files in {folder}:")
            filename = choose_file(files)
            if filename is None:
                break
            input_path = os.path.join(folder, filename)

            print("\n  Sort mode:")
            for k, (_, label) in MODES.items():
                print(f"    ({k}) {label}")
            mode_key = ask("  Choose: ", list(MODES.keys()))
            if mode_key is None:
                continue
            mode, _ = MODES[mode_key]

            order = ask("  Order -- (a)scending or (d)escending: ", ['a', 'd'])
            if order is None:
                continue
            reverse = (order == 'd')

            skip_empty = ask("  Remove empty lines? y/n: ", ['y', 'n'])
            if skip_empty is None:
                continue
            skip_empty = (skip_empty == 'y')

            dedupe = ask("  Remove duplicate lines? y/n: ", ['y', 'n'])
            if dedupe is None:
                continue
            dedupe = (dedupe == 'y')

            if filename.lower().endswith('.csv'):
                col_ans = ask("  Sort by a specific CSV column? y/n: ", ['y', 'n'])
                if col_ans is None:
                    continue
                if col_ans == 'y':
                    raw = input("  Column number (1-based): ").strip()
                    if not raw.isdigit() or int(raw) < 1:
                        print("  Invalid column.")
                        continue
                    column = int(raw)
                    hdr = ask("  Keep the first row as a header on top? y/n: ", ['y', 'n'])
                    if hdr is None:
                        continue
                    has_header = (hdr == 'y')
                    in_place = ask("  Overwrite source file in-place? y/n: ", ['y', 'n'])
                    if in_place is None:
                        continue
                    if in_place == 'y':
                        output_path = input_path
                    else:
                        base, ext = os.path.splitext(input_path)
                        output_path = base + '_sorted' + ext
                    sort_csv_by_column(input_path, output_path, column, mode,
                                       reverse, skip_empty, dedupe, has_header)
                    again = ask("\n  Sort another file? y/n: ", ['y', 'n'])
                    if again != 'y':
                        break
                    continue

            capitalise = False
            if mode == 'alpha':
                cap_ans = ask("  Capitalise first letter of each line? y/n: ", ['y', 'n'])
                if cap_ans is None:
                    continue
                capitalise = (cap_ans == 'y')

            in_place = ask("  Overwrite source file in-place? y/n: ", ['y', 'n'])
            if in_place is None:
                continue
            if in_place == 'y':
                output_path = input_path
            else:
                base, ext = os.path.splitext(input_path)
                default_out = base + '_sorted' + ext
                print(f"  Output file: {default_out}")
                custom = ask("  Use a custom output path? y/n: ", ['y', 'n'])
                if custom is None:
                    continue
                if custom == 'y':
                    raw = input("  Output path: ")
                    output_path = clean_path(raw)
                else:
                    output_path = default_out

            sort_file(input_path, output_path, mode, reverse, skip_empty, dedupe, capitalise)

            again = ask("\n  Sort another file? y/n: ", ['y', 'n'])
            if again != 'y':
                break

    except KeyboardInterrupt:
        print("\n  Interrupted.")

    print("  Bye!")


def parse_args():
    p = argparse.ArgumentParser(
        description="Alpha-Numerical Sorter -- sort text files alphabetically, numerically, or naturally.",
        epilog="Omit --file to launch the interactive prompt-based interface.",
    )
    p.add_argument("--file",         metavar="PATH",  help="Input file to sort (enables non-interactive mode)")
    p.add_argument("--mode",         metavar="MODE",  default="natural",
                   help="Sort mode: alpha | natural | numeric | length (default: natural)")
    p.add_argument("--output",       metavar="PATH",  help="Output file path (default: <input>_sorted.<ext>)")
    p.add_argument("--order",        metavar="a|d",   default="a",
                   help="Sort order: a=ascending, d=descending (default: a)")
    p.add_argument("--remove-dupes", action="store_true", help="Remove duplicate lines")
    p.add_argument("--remove-empty", action="store_true", help="Remove empty lines")
    p.add_argument("--in-place",     action="store_true", help="Overwrite the source file instead of creating a new one")
    p.add_argument("--capitalise",   action="store_true", help="Capitalise the first letter of each line (alpha mode only)")
    p.add_argument("--ext",          metavar="EXT",   nargs="+",
                   help="Additional file extensions to include in the file browser (e.g. tsv list nfo). "
                        "Works in both CLI and interactive modes.")
    p.add_argument("--column",       metavar="N",     type=int,
                   help="Sort a CSV file by this 1-based column instead of by whole line")
    p.add_argument("--no-header",    action="store_true",
                   help="With --column: treat the first CSV row as data, not a header")
    return p.parse_args()


def main():
    args = parse_args()
    if args.file:
        run_cli(args)
    else:
        run_interactive(extra_exts=args.ext or ())


if __name__ == '__main__':
    main()
