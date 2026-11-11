# Primitives Reference

This document provides a comprehensive reference for all user interface primitives, widgets, and layout components available in Prism.

---

## Status Badges & Logging

Status messages output semantic log records tagged with appropriate symbols and ANSI color codes.

### API Methods

```python
ui.success(msg: str) -> None
ui.info(msg: str, symbol: str = "ℹ️") -> None
ui.warn(msg: str) -> None
ui.error(msg: str) -> None
ui.action(msg: str, symbol: str = "⚡") -> None
ui.status(symbol: str, message: str, code: str = "1") -> str
ui.badge() -> str
```

### Parameters

| Method | Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `success` | `msg` | `str` | *required* | Success message rendered in green. |
| `info` | `msg` | `str` | *required* | Informational message rendered in cyan. |
| `info` | `symbol` | `str` | `"ℹ️"` | Custom prefix symbol. |
| `warn` | `msg` | `str` | *required* | Warning message rendered in yellow. |
| `error` | `msg` | `str` | *required* | Error message rendered in red to `sys.stderr`. |
| `action` | `msg` | `str` | *required* | Action/event dispatch notice. |

---

## Bounding Panels & Diagnostic Boxes

Bounding panels render width-aware frames with rounded corners (`╭─╮│╰─╯`). Text exceeding the panel width is gracefully clipped to prevent wrap distortion.

### API Methods

```python
ui.panel(
    title: str,
    lines: Sequence[str] | str,
    border_color: str = "0;36",
    width: int = 76,
    stream: TextIO | None = None,
) -> None

ui.error_panel(
    title: str,
    lines: Sequence[str] | str,
) -> None
```

### Parameters

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | *required* | Header title embedded into the top border. |
| `lines` | `Sequence[str] \| str` | *required* | Text lines or multi-line string content. |
| `border_color` | `str` | `"0;36"` | ANSI color code for borders (cyan default). |
| `width` | `int` | `76` | Target width in columns (clamped to terminal width). |
| `stream` | `TextIO \| None` | `sys.stdout` | Target output stream. |

---

## Status Cards & Dashboards

Status cards display daemon states, background service endpoints, runtime metrics, and keyboard shortcuts.

### API Method

```python
ui.status_card(
    title: str,
    target: str | None = None,
    url: str | None = None,
    details: Sequence[tuple[str, str]] | dict[str, str] | None = None,
    controls: Sequence[tuple[str, str]] | None = None,
    warning: str | None = None,
    tip: str | None = None,
    border_color: str = "1;36",
    width: int = 76,
) -> None
```

### Parameters

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | *required* | Card title displayed in header border. |
| `target` | `str \| None` | `None` | Path or identifier being serviced. |
| `url` | `str \| None` | `None` | Network endpoint URL (highlighted in bold cyan). |
| `details` | `dict \| list[tuple]` | `None` | Key-value pairs displayed in tabular format. |
| `controls` | `list[tuple[str, str]]` | `None` | Keyboard controls (e.g. `[("r", "reload"), ("q", "quit")]`). |
| `warning` | `str \| None` | `None` | Warning notice rendered in yellow. |
| `tip` | `str \| None` | `None` | Informational tip rendered in dimmed text. |

---

## Threaded Braille Spinners

Spinners provide visual feedback during long-running tasks. They operate in a background daemon thread, keeping the main thread non-blocking.

### API Method

```python
with ui.spinner(message: str) as sp:
    # Perform blocking operation
    ...
```

### Methods on `Spinner`

| Method | Description |
| :--- | :--- |
| `sp.update(text: str)` | Update the spinner status label during execution. |
| `sp.stop(ok: bool = True)` | Stop the spinner, write final checkmark or cross, and restore cursor. |

---

## Interactive Selection Menus

Interactive menus operate in raw terminal mode (`cbreak`), capturing keypresses without requiring the user to press Enter.

### Single Selection

```python
choice = ui.select(
    title: str,
    options: Sequence[str | tuple[str, str] | tuple[str, str, str]],
    default_index: int = 0,
) -> str
```

Navigation:
- `Up` / `k`: Move selection up
- `Down` / `j`: Move selection down
- `Enter`: Confirm selection
- `Ctrl+C` / `q`: Cancel (returns default or empty)

### Multiple Selection

```python
selected = ui.multiselect(
    title: str,
    options: Sequence[Any],
    preselected: Sequence[str] | set[str] | None = None,
    searchable: bool = True,
) -> list[str]
```

Controls:
- `Space`: Toggle focused option
- `a`: Select or deselect all items
- `/`: Filter options dynamically
- `Enter`: Confirm selection

---

## Fuzzy Searchbox

The searchbox primitive provides an in-terminal interactive filtering widget matching queries against a list of candidates.

### API Method

```python
result = ui.searchbox(
    title: str = "Search",
    options: Sequence[Any] = (),
    prompt: str = "❯ ",
    placeholder: str = "Type to search...",
    limit: int = 10,
) -> str | None
```

---

## Data Tables & Encoders

Prism provides an auto-sizing table formatter with support for rounded borders, column alignments, and content clipping.

### API Method

```python
rendered_str = ui.table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    widths: Sequence[int | None] | None = None,
    alignments: Sequence[Literal["left", "center", "right"]] | None = None,
    style: Literal["rounded", "clean", "compact", "plain"] = "rounded",
    max_width: int | None = None,
    title: str | None = None,
    border_color: str = "0;36",
) -> str
```

### Polymorphic Emitter (`ui.data`)

Emits tabular or structured data automatically adapting to the active execution mode:

```python
ui.data(
    data: Any = None,
    title: str | None = None,
    headers: Sequence[str] | None = None,
    rows: Sequence[Sequence[Any]] | None = None,
    exit_code: int | None = None,
) -> None
```

---

## Terminal Utilities

Low-level terminal primitives exported by `prism.terminal`:

| Utility | Signature | Description |
| :--- | :--- | :--- |
| `visual_len` | `visual_len(text: str) -> int` | Computes visible character width ignoring ANSI escape codes. |
| `strip_ansi` | `strip_ansi(text: str) -> str` | Strips all ANSI escape sequences via regular expressions. |
| `strip_emojis` | `strip_emojis(text: str) -> str` | Strips Unicode emoji codepoints for token-conservative processing. |
| `get_terminal_columns` | `get_terminal_columns(fallback=80) -> int` | Returns terminal width in columns with fallback. |
| `cbreak_mode` | `cbreak_mode(stream)` | Context manager entering terminal raw/cbreak mode for interactive input. |
| `read_key` | `read_key(stream) -> str` | Reads a single key or ANSI escape sequence (arrows, function keys). |
