"""Token-Oriented Object Notation (TOON) serialization engine for Prism.

Implements the official TOON specification (toonformat.dev) to serialize structured
data into compact, whitespace-aware, and tabular token-optimized notation for LLMs.
Zero dependencies.
"""

from __future__ import annotations

import math
from typing import Any, Sequence


def _is_scalar(val: Any) -> bool:
    """Returns True if val is a primitive scalar type (str, int, float, bool, None)."""
    return val is None or isinstance(val, (bool, int, float, str))


def _is_numeric_str(s: str) -> bool:
    """Checks if a string strictly looks like a number, requiring quoting in TOON."""
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def format_scalar(val: Any, delimiter: str = ",") -> str:
    """Formats a single scalar value according to TOON escaping and quoting rules."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return "null"
        # Canonical decimal representation
        if val.is_integer():
            return f"{val:.1f}"
        return f"{val:.6g}".rstrip("0").rstrip(".") if "." in f"{val:.6g}" else f"{val:.6g}"

    s = str(val)
    # String quoting rules:
    # 1. Empty string
    # 2. Leading or trailing whitespace
    # 3. Matches boolean/null keywords
    # 4. Resembles a numeric literal
    # 5. Contains structural characters: delimiter, colon, quote, newline, brackets, braces
    needs_quotes = (
        len(s) == 0
        or s != s.strip()
        or s in ("true", "false", "null")
        or _is_numeric_str(s)
        or delimiter in s
        or ":" in s
        or '"' in s
        or "\n" in s
        or "\r" in s
        or "\t" in s
        or "[" in s
        or "]" in s
        or "{" in s
        or "}" in s
    )

    if not needs_quotes:
        return s

    # Escape quotes and backslashes
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return f'"{escaped}"'


def _is_uniform_dict_list(items: Sequence[Any]) -> tuple[bool, list[str]]:
    """Checks if a sequence consists exclusively of dicts with a consistent key set.

    Returns (is_uniform, keys).
    """
    if not items or not all(isinstance(x, dict) for x in items):
        return False, []

    # Get ordered keys from first dict
    first_keys = list(items[0].keys())
    if not first_keys:
        return False, []

    # Ensure all items share keys and values in those keys are scalar or simple
    first_key_set = set(first_keys)
    for it in items[1:]:
        if set(it.keys()) != first_key_set:
            return False, []
        for v in it.values():
            if not _is_scalar(v):
                return False, []

    for v in items[0].values():
        if not _is_scalar(v):
            return False, []

    return True, [str(k) for k in first_keys]


def encode_toon(data: Any, delimiter: str = ",", indent_level: int = 0) -> str:
    """Serializes a Python object into Token-Oriented Object Notation (TOON).

    Args:
        data: Primitive, dict, list, or nested object.
        delimiter: Active array/tabular delimiter (default: ',').
        indent_level: Current indentation depth (multiples of 2 spaces).

    Returns:
        TOON formatted string.
    """
    indent = "  " * indent_level

    # 1. Scalar root
    if _is_scalar(data):
        return format_scalar(data, delimiter=delimiter)

    # 2. List root
    if isinstance(data, (list, tuple)):
        count = len(data)
        if count == 0:
            return "[]"

        # Tabular array of uniform dicts
        is_uniform, keys = _is_uniform_dict_list(data)
        if is_uniform:
            keys_header = delimiter.join(keys)
            lines = [f"items[{count}]{{{keys_header}}}:"]
            for row in data:
                row_vals = delimiter.join(format_scalar(row.get(k), delimiter=delimiter) for k in keys)
                lines.append(f"  {row_vals}")
            return "\n".join(lines)

        # Inline array of scalars
        if all(_is_scalar(x) for x in data):
            vals_str = delimiter.join(format_scalar(x, delimiter=delimiter) for x in data)
            return f"items[{count}]: {vals_str}"

        # General list
        lines = [f"items[{count}]:"]
        for it in data:
            if _is_scalar(it):
                lines.append(f"  - {format_scalar(it, delimiter=delimiter)}")
            elif isinstance(it, dict):
                sub = encode_toon(it, delimiter=delimiter, indent_level=indent_level + 1)
                lines.append(f"  -\n{sub}")
            else:
                sub = encode_toon(it, delimiter=delimiter, indent_level=indent_level + 1)
                lines.append(f"  - {sub}")
        return "\n".join(lines)

    # 3. Dict / Object root
    if isinstance(data, dict):
        if not data:
            return "{}"

        lines: list[str] = []
        for k, v in data.items():
            key_str = str(k)

            # Scalar value
            if _is_scalar(v):
                lines.append(f"{indent}{key_str}: {format_scalar(v, delimiter=delimiter)}")

            # List value
            elif isinstance(v, (list, tuple)):
                count = len(v)
                if count == 0:
                    lines.append(f"{indent}{key_str}[0]:")
                    continue

                is_uniform, col_keys = _is_uniform_dict_list(v)
                if is_uniform:
                    cols_header = delimiter.join(col_keys)
                    lines.append(f"{indent}{key_str}[{count}]{{{cols_header}}}:")
                    for row in v:
                        row_vals = delimiter.join(format_scalar(row.get(ck), delimiter=delimiter) for ck in col_keys)
                        lines.append(f"{indent}  {row_vals}")

                elif all(_is_scalar(x) for x in v):
                    vals_str = delimiter.join(format_scalar(x, delimiter=delimiter) for x in v)
                    lines.append(f"{indent}{key_str}[{count}]: {vals_str}")

                else:
                    lines.append(f"{indent}{key_str}[{count}]:")
                    for item in v:
                        if _is_scalar(item):
                            lines.append(f"{indent}  - {format_scalar(item, delimiter=delimiter)}")
                        elif isinstance(item, dict):
                            lines.append(f"{indent}  -")
                            nested_str = encode_toon(item, delimiter=delimiter, indent_level=indent_level + 2)
                            lines.append(nested_str)
                        else:
                            nested_str = encode_toon(item, delimiter=delimiter, indent_level=indent_level + 1)
                            lines.append(f"{indent}  - {nested_str}")

            # Nested dict value
            elif isinstance(v, dict):
                if not v:
                    lines.append(f"{indent}{key_str}: {{}}")
                else:
                    lines.append(f"{indent}{key_str}:")
                    nested_str = encode_toon(v, delimiter=delimiter, indent_level=indent_level + 1)
                    lines.append(nested_str)

            else:
                lines.append(f"{indent}{key_str}: {format_scalar(str(v), delimiter=delimiter)}")

        return "\n".join(lines)

    return format_scalar(str(data), delimiter=delimiter)
