# Architecture & Design

Prism serves as the foundational design system and terminal rendering engine for the SpanishSyntax Frost and Icebergs ecosystem. It is engineered to bridge human terminal interaction and autonomous agent tooling without introducing heavyweight runtime dependencies.

---

## Design Philosophy

CLI tooling in modern systems engineering typically suffers from one of two failure modes:
1. **Unformatted primitive text**: Scripts dump unformatted text, ANSI artifacts, or raw dumps that degrade readability and lack contextual structure.
2. **Heavyweight dependencies**: Frameworks like `rich`, `curses`, or `prompt_toolkit` introduce sprawling dependency trees, binary compilation requirements, and noticeable latency during startup.

Prism resolves this trade-off by operating with **zero runtime dependencies** beyond standard library POSIX primitives (`termios`, `tty`, `select`, `shutil`, `threading`, `sys`, `os`).

```
                    ┌─────────────────────────┐
                    │      Prism Facade       │
                    │       (prism.UI)        │
                    └────────────┬────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │                           │                           │
┌────┴────────────┐     ┌────────┴──────────┐     ┌──────────┴────────┐
│  Human Terminal │     │    Agent Mode     │     │ Structured Output │
│   (ANSI/TTY)    │     │   (Token Dense)   │     │    (JSON/TOON)    │
├─────────────────┤     ├───────────────────┤     ├───────────────────┤
│ • Rounded boxes │     │ • Stripped ANSI   │     │ • RFC-8259 JSON   │
│ • Braille spin  │     │ • Zero emojis     │     │ • TOON serialization│
│ • TrueColor     │     │ • Single-line KV  │     │ • Schema validation│
│ • Key menus     │     │ • Minimal tokens  │     │ • Exit code binding│
└─────────────────┘     └───────────────────┘     └───────────────────┘
```

---

## Why "Prism"? (The Lore)

> **ice prism** (`/ˈprɪz.əm/`) — *noun:* A microscopic, hexagonal ice crystal suspended in frozen polar air, refracting cold winter sunlight into sun dogs, luminous halos, and sharp spectral color pillars.

In polar meteorology, ice prisms are hexagonal micro-crystals that form under deep freeze. They refract scattered white sunlight into focused geometric pillars and halos with spectral precision.

Prism mirrors this natural mechanism by transforming scattered standard output streams into structured visual components or deterministic machine data streams.

---

## Subsystem Hierarchy

Prism is partitioned into decoupled layers within `src/prism/`:

| Module | Core Responsibility | Primitives / Functions Exposed |
| :--- | :--- | :--- |
| `terminal.py` | Low-level POSIX terminal control | `get_terminal_columns`, `get_terminal_size`, `visual_len`, `strip_ansi`, `strip_emojis`, `cbreak_mode`, `read_key` |
| `color.py` | Terminal color negotiation & CLI flags | `add_color_args`, `apply_color_args`, `add_agent_args`, `apply_agent_args`, `handle_version_arg` |
| `styling.py` | ANSI styling engine & mode state | `Styler`, `detect_color_support`, `check_agent_env`, `check_json_env`, `check_toon_env` |
| `panels.py` | Width-aware bounding boxes | `render_panel`, `render_error_panel` |
| `cards.py` | Standardized service status dashboards | `render_status_card` |
| `spinner.py` | Threaded braille animation | `Spinner`, `spinner_context` |
| `menus.py` | Keyboard-driven list selectors | `select_menu`, `multiselect_menu` |
| `searchbox.py` | Interactive live fuzzy searchbox | `searchbox` |
| `table.py` | Dynamic column auto-sizing tables | `render_table` |
| `toon.py` | Token-Oriented Object Notation | `encode_toon`, `format_scalar` |
| `help.py` | Standardized help screen renderer | `HelpBuilder`, `render_help` |
| `engine.py` | High-level facade aggregating all modules | `UI`, `ui` |

---

## Execution Modes

Prism dynamically negotiates its output stream based on environment variables and command-line flags.

### 1. Interactive Human Mode (TTY)

When connected to an interactive TTY (`sys.stdout.isatty() == True`):
- ANSI styling and 24-bit TrueColor / 256-color palettes are activated.
- Panels are framed with rounded corner box characters (`╭─╮│╰─╯`).
- Long text lines are measured according to visual length (accounting for wide unicode characters and stripping ANSI escape bytes) and clipped with `...`.
- Spinners spin using a background thread and braille glyphs (`⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`).

### 2. Agent Mode (`-A` / `--agent`)

When invoked with `-A`, `--agent`, or `PRISM_AGENT=1` / `ICEBERG_AGENT=1`:
- All ANSI escapes and decorative box drawings are suppressed.
- Emojis are stripped to prevent token waste in language model context windows.
- Status cards are flattened into single-line key-value declarations:
  ```
  STATUS_ACTIVE: title="Prism Service" endpoint="http://127.0.0.1:8080" uptime="4h"
  ```
- Errors are emitted as `ERROR: <message>`.

### 3. Structured Machine Mode (`--json` / `--toon`)

- **JSON Mode (`--json` or `PRISM_JSON=1`)**: Emits structured RFC-8259 JSON payloads directly to `stdout`.
- **TOON Mode (`--toon` or `PRISM_TOON=1`)**: Emits Token-Oriented Object Notation, designed for LLM prompts to achieve 40–60% token reduction compared to verbose JSON.
