import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from main import first_number, natural_key, sort_csv_by_column, sort_file, sort_lines


@pytest.mark.parametrize("text, expected", [
    ("name-2", 2), ("-5 degrees", -5), ("temp is -3.5", -3.5), ("v1.10", 1.10), ("no digits", float("inf")),
    ("a 12 b 3", 12),
])
def test_first_number(text, expected):
    assert first_number(text) == expected


def test_natural_sort_puts_file2_before_file10():
    assert sort_lines(["file10", "File2", "file1"], "natural", False, False, False) == ["file1", "File2", "file10"]


def test_natural_sort_handles_versions_and_leading_numbers():
    lines = ["v1.10", "v1.9", "v1.2", "10 apples", "9 apples", "apples"]
    assert sorted(lines, key=natural_key) == ["9 apples", "10 apples", "apples", "v1.2", "v1.9", "v1.10"]


@pytest.mark.parametrize("reverse, expected", [
    (False, ["item-1", "item-2", "item-10", "untitled"]),
    (True, ["item-10", "item-2", "item-1", "untitled"]),
])
def test_lines_without_numbers_always_go_last(reverse, expected):
    assert sort_lines(["item-10", "untitled", "item-1", "item-2"], "numeric", reverse, False, False) == expected


def test_alpha_sort_is_case_insensitive_and_can_capitalise():
    assert sort_lines(["banana", "Apple", "cherry"], "alpha", False, False, False, capitalise=True) == ["Apple", "Banana", "Cherry"]


def test_length_sort_ignores_trailing_spaces():
    assert sort_lines(["ccc", "a   ", "bb"], "length", False, False, False) == ["a   ", "bb", "ccc"]


def test_skip_empty_and_dedupe_ignore_case_and_spacing():
    lines = ["Alpha", "", "alpha ", "  ", "beta"]
    assert sort_lines(lines, "alpha", False, True, True) == ["Alpha", "beta"]


def test_empty_input_stays_empty():
    assert sort_lines([], "natural", False, True, True) == []


def test_sort_file_round_trip(tmp_path):
    source = tmp_path / "in.txt"
    source.write_text("b\na\n\nc\n", encoding="utf-8")
    assert sort_file(str(source), str(tmp_path / "out.txt"), "alpha", False, True, False)
    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "a\nb\nc\n"


def test_csv_sort_keeps_the_header_and_short_rows(tmp_path):
    source = tmp_path / "in.csv"
    source.write_text("name,size\nfile10,3\nfile2\nfile1,9\n", encoding="utf-8")
    assert sort_csv_by_column(str(source), str(tmp_path / "out.csv"), 1, "natural", False, False, False)
    assert (tmp_path / "out.csv").read_text(encoding="utf-8").splitlines() == ["name,size", "file1,9", "file2", "file10,3"]


def test_missing_file_reports_failure(tmp_path, capsys):
    assert sort_file(str(tmp_path / "missing.txt"), str(tmp_path / "out.txt"), "alpha", False, False, False) is False
    assert "Error" in capsys.readouterr().out


def test_csv_numeric_reverse_keeps_blank_cells_last(tmp_path):
    source = tmp_path / "in.csv"
    source.write_text("a,1\nb,\nc,30\n", encoding="utf-8")
    assert sort_csv_by_column(str(source), str(tmp_path / "out.csv"), 2, "numeric", True, False, False, has_header=False)
    assert (tmp_path / "out.csv").read_text(encoding="utf-8").splitlines() == ["c,30", "a,1", "b,"]
