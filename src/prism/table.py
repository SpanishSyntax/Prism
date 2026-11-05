"""Zero-dependency tabular data rendering engine for terminal and agent environments."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, TextIO

from prism.terminal import get_terminal_columns, strip_ansi, visual_len

if TYPE_CHECKING:
    from prism.styling import Styler

TableStyle = Literal["rounded", "clean", "compact", "plain"]


def _format_cell(value: Any) -> str:
    """Convert any cell value to a safe display string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    widths: Sequence[int | None] | None = None,
    alignments: Sequence[Literal["left", "center", "right"]] | None = None,
    style: TableStyle = "rounded",
    max_width: int | None = None,
    title: str | None = None,
    border_color: str = "0;36",
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> str:
    """Renders a tabular layout into a formatted string.

    In interactive human terminal mode:
      Renders styled Unicode box-drawing or clean divider tables with proper ANSI styling.

    In AI / Agent mode:
      Emits a compact, borderless, token-efficient table with zero ANSI escape codes,
      zero decorative border characters, and no superfluous padding tokens.
    """
    from prism.engine import ui as default_ui

    st = styler or default_ui.styler
    out_stream = stream or st.stream
    agent_mode = st.is_agent

    num_cols = len(headers)
    if num_cols == 0:
        return ""

    # Normalize cells to strings
    string_rows: list[list[str]] = [
        [_format_cell(cell) for cell in row] for row in rows
    ]

    # Clean headers
    clean_headers = [str(h) for h in headers]

    # AI / Agent Mode: Token-efficient, borderless layout
    if agent_mode:
        lines: list[str] = []
        if title:
            lines.append(f"[{title.strip()}]")

        # In Agent mode, compute minimal column widths without decorative padding
        col_widths: list[int] = []
        for col_idx in range(num_cols):
            h_len = visual_len(clean_headers[col_idx])
            r_lens = [
                visual_len(row[col_idx])
                for row in string_rows
                if col_idx < len(row)
            ]
            col_widths.append(max([h_len] + r_lens, default=1))

        # Header line
        header_cells = [
            f"{clean_headers[i]:<{col_widths[i]}}" for i in range(num_cols)
        ]
        lines.append("  ".join(header_cells).rstrip())

        # Simple separator line
        lines.append("  ".join(["-" * w for w in col_widths]))

        # Data rows
        for row in string_rows:
            row_cells = []
            for col_idx in range(num_cols):
                val = row[col_idx] if col_idx < len(row) else ""
                row_cells.append(f"{val:<{col_widths[col_idx]}}")
            lines.append("  ".join(row_cells).rstrip())

        result = "\n".join(lines) + "\n"
        if stream:
            out_stream.write(result)
        return result

    # Human / Interactive Terminal Mode
    term_cols = get_terminal_columns(fallback=80)
    avail_width = max_width or min(term_cols - 2, 120)

    # Calculate optimal column widths
    computed_widths: list[int] = []
    for col_idx in range(num_cols):
        if widths and col_idx < len(widths) and widths[col_idx] is not None:
            computed_widths.append(widths[col_idx])  # type: ignore
        else:
            h_len = visual_len(clean_headers[col_idx])
            max_cell = max(
                (visual_len(r[col_idx]) for r in string_rows if col_idx < len(r)),
                default=0,
            )
            computed_widths.append(max(h_len, max_cell))

    # Determine alignment
    col_align: list[Literal["left", "center", "right"]] = []
    for col_idx in range(num_cols):
        if alignments and col_idx < len(alignments):
            col_align.append(alignments[col_idx])
        else:
            col_align.append("left")

    # Clamping and budget allocation if table exceeds available width
    # In 'rounded' style, spacing takes (3 * num_cols + 1) chars: '│ ' + ' │ ' * (n-1) + ' │'
    border_overhead = (3 * num_cols + 1) if style == "rounded" else (2 * (num_cols - 1))
    max_data_width = max(20, avail_width - border_overhead)

    total_data_w = sum(computed_widths)
    if total_data_w > max_data_width:
        # Scale down largest columns proportionally
        shrinkable = sorted(
            range(num_cols), key=lambda i: computed_widths[i], reverse=True
        )
        excess = total_data_w - max_data_width
        for idx in shrinkable:
            if excess <= 0:
                break
            min_w = max(6, visual_len(clean_headers[idx]))
            can_shrink = max(0, computed_widths[idx] - min_w)
            to_shrink = min(excess, can_shrink)
            computed_widths[idx] -= to_shrink
            excess -= to_shrink

    def _pad_cell(
        text: str, width: int, align: Literal["left", "center", "right"]
    ) -> str:
        v_len = visual_len(text)
        if v_len > width:
            plain = strip_ansi(text)
            clipped = plain[: max(0, width - 3)] + "..."
            v_len = len(clipped)
            text = clipped

        pad = max(0, width - v_len)
        if align == "right":
            return " " * pad + text
        if align == "center":
            left_pad = pad // 2
            right_pad = pad - left_pad
            return " " * left_pad + text + " " * right_pad
        return text + " " * pad

    lines = []

    # Box Drawing Characters
    if style == "rounded":
        bc = f"\033[{border_color}m" if st.use_color else ""
        reset = "\033[0m" if st.use_color else ""

        # Title
        if title:
            lines.append(f"{st.badge()} {st.bold(title)}")

        # Top border: ╭─────┬─────╮
        top_segs = [bc + "─" * (w + 2) + reset for w in computed_widths]
        lines.append(f"{bc}╭{reset}" + f"{bc}┬{reset}".join(top_segs) + f"{bc}╮{reset}")

        # Header row
        hdr_cells = [
            f" {st.bold(_pad_cell(clean_headers[i], computed_widths[i], col_align[i]))} "
            for i in range(num_cols)
        ]
        lines.append(f"{bc}│{reset}" + f"{bc}│{reset}".join(hdr_cells) + f"{bc}│{reset}")

        # Header separator: ├─────┼─────┤
        mid_segs = [bc + "─" * (w + 2) + reset for w in computed_widths]
        lines.append(f"{bc}├{reset}" + f"{bc}┼{reset}".join(mid_segs) + f"{bc}┤{reset}")

        # Data rows
        for row in string_rows:
            r_cells = [
                f" {_pad_cell(row[i] if i < len(row) else '', computed_widths[i], col_align[i])} "
                for i in range(num_cols)
            ]
            lines.append(f"{bc}│{reset}" + f"{bc}│{reset}".join(r_cells) + f"{bc}│{reset}")

        # Bottom border: ╰─────┴─────╯
        bot_segs = [bc + "─" * (w + 2) + reset for w in computed_widths]
        lines.append(f"{bc}╰{reset}" + f"{bc}┴{reset}".join(bot_segs) + f"{bc}╯{reset}")

    elif style == "clean":
        if title:
            lines.append(f"{st.badge()} {st.bold(title)}")
            lines.append("")

        hdr_cells = [
            st.bold(_pad_cell(clean_headers[i], computed_widths[i], col_align[i]))
            for i in range(num_cols)
        ]
        lines.append("  ".join(hdr_cells))
        lines.append("  ".join(st.dim("─" * w) for w in computed_widths))

        for row in string_rows:
            r_cells = [
                _pad_cell(
                    row[i] if i < len(row) else "", computed_widths[i], col_align[i]
                )
                for i in range(num_cols)
            ]
            lines.append("  ".join(r_cells))

    else:  # compact or plain
        if title:
            lines.append(st.bold(title))
        hdr_cells = [
            _pad_cell(clean_headers[i], computed_widths[i], col_align[i])
            for i in range(num_cols)
        ]
        lines.append(" ".join(hdr_cells))
        lines.append(" ".join("-" * w for w in computed_widths))
        for row in string_rows:
            r_cells = [
                _pad_cell(
                    row[i] if i < len(row) else "", computed_widths[i], col_align[i]
                )
                for i in range(num_cols)
            ]
            lines.append(" ".join(r_cells))

    result = "\n".join(lines) + "\n"
    if stream:
        out_stream.write(result)
    return result
