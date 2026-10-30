"""Tests for Token-Oriented Object Notation (TOON) serialization."""

from __future__ import annotations

from prism.toon import encode_toon, format_scalar


def test_format_scalar_primitives() -> None:
    assert format_scalar(None) == "null"
    assert format_scalar(True) == "true"
    assert format_scalar(False) == "false"
    assert format_scalar(42) == "42"
    assert format_scalar(3.14) == "3.14"


def test_format_scalar_strings() -> None:
    # Unquoted simple strings
    assert format_scalar("hello") == "hello"
    assert format_scalar("my_var") == "my_var"

    # Needs quotes: empty
    assert format_scalar("") == '""'

    # Needs quotes: booleans or null keywords
    assert format_scalar("true") == '"true"'
    assert format_scalar("null") == '"null"'

    # Needs quotes: numeric string
    assert format_scalar("123") == '"123"'

    # Needs quotes: delimiter or structural chars
    assert format_scalar("foo,bar") == '"foo,bar"'
    assert format_scalar("key:val") == '"key:val"'
    assert format_scalar("hello world") == "hello world"  # spaces inside are allowed if no leading/trailing
    assert format_scalar(" space ") == '" space "'


def test_tabular_array_encoding() -> None:
    tools = [
        {"name": "ls", "pack": "fs", "enabled": True},
        {"name": "cat", "pack": "fs", "enabled": True},
        {"name": "grep", "pack": "fs", "enabled": False},
    ]
    encoded = encode_toon(tools)
    expected = (
        "items[3]{name,pack,enabled}:\n"
        "  ls,fs,true\n"
        "  cat,fs,true\n"
        "  grep,fs,false"
    )
    assert encoded == expected


def test_dict_with_tabular_array() -> None:
    data = {
        "status": "ok",
        "count": 2,
        "tools": [
            {"name": "ls", "pack": "fs"},
            {"name": "cat", "pack": "fs"},
        ],
    }
    encoded = encode_toon(data)
    expected = (
        "status: ok\n"
        "count: 2\n"
        "tools[2]{name,pack}:\n"
        "  ls,fs\n"
        "  cat,fs"
    )
    assert encoded == expected


def test_inline_scalar_array() -> None:
    tags = ["python", "rust", "nix"]
    assert encode_toon(tags) == "items[3]: python,rust,nix"


def test_pipe_delimiter() -> None:
    rows = [
        {"a": "hello", "b": "world, with comma"},
    ]
    encoded = encode_toon(rows, delimiter="|")
    assert encoded == "items[1]{a|b}:\n  hello|world, with comma"
