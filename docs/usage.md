# Integration & Usage Guide

This guide details best practices and recipes for integrating Prism into CLI applications, Nix packages, and automated agent workflows.

---

## CLI Argument Integration

Prism includes standard helper functions to add and handle common flags (`--color`, `--no-color`, `-A`/`--agent`, `--json`, `--toon`, `--version`) using standard Python `argparse`.

### Adding Standard Flags

```python
import argparse
from prism import add_agent_args, add_color_args, apply_agent_args, apply_color_args, ui

parser = argparse.ArgumentParser(description="My Systems Tool")
add_color_args(parser)
add_agent_args(parser)
parser.add_argument("--version", "-v", action="store_true", help="Show version")

args = parser.parse_args()

# Apply flags to the global UI instance
apply_color_args(args, ui=ui)
apply_agent_args(args, ui=ui)
```

---

## Help Screen Generation

Prism provides `HelpBuilder` and `render_help` to generate formatted CLI help manuals that comply with terminal widths and strip decorative syntax when called by agent runners.

```python
from prism import ui

doc = ui.render_help(
    app_name="flaker",
    tagline="Nix flake auditing and vulnerability scanning engine",
    usage="flaker [OPTIONS] <COMMAND> [TARGET]",
    commands=[
        ("check", "Audit flake.lock dependencies for known security advisories"),
        ("update", "Perform conservative dependency updates with regression checks"),
        ("diff", "Compute AST semantic diff between two flake revisions"),
    ],
    options=[
        ("-c, --config <PATH>", "Path to flaker configuration file"),
        ("-A, --agent", "Emit token-dense, unformatted output for LLM agents"),
        ("--json", "Emit structured RFC-8259 JSON output"),
    ],
    examples=[
        ("flaker check", "Run standard security audit on current repository"),
        ("flaker update --dry-run", "Simulate dependency resolution without writing lockfile"),
    ],
    version="1.4.0",
)

print(doc)
```

---

## Machine & Agent Automation

When integrating CLI tools into autonomous pipelines or LLM environments, visual decoration introduces token overhead. Prism provides native content negotiation:

### Environment Variables

| Variable | Mode Triggered | Behavior |
| :--- | :--- | :--- |
| `PRISM_AGENT=1` or `ICEBERG_AGENT=1` | Agent Mode | Strips ANSI escape codes, eliminates emojis, flattens status cards into single-line key-value entries. |
| `PRISM_JSON=1` | JSON Mode | Forces `ui.data()` and `ui.status_card()` to emit pure RFC-8259 JSON. |
| `PRISM_TOON=1` | TOON Mode | Forces `ui.data()` to serialize output as Token-Oriented Object Notation. |
| `NO_COLOR=1` | Plain Text | Disables all ANSI styling, preserving box drawings. |

### Programmatic Mode Switching

```python
from prism import ui

# Enable agent mode programmatically
ui.set_agent_mode(agent=True)

# Emitting a status card in agent mode produces:
# STATUS_ACTIVE: title="Deployment Complete" target="fleet-primary" duration="42s"
ui.status_card(
    title="Deployment Complete",
    target="fleet-primary",
    details={"duration": "42s"},
)
```

---

## Custom Facades & App Branding

You can instantiate dedicated `UI` facades for distinct applications or submodules with individual icons, app names, and color accents:

```python
from prism import UI

# Create customized facades for individual tools
folio_ui = UI(app_name="folio", icon="❄️", badge_color="1;34")
borealis_ui = UI(app_name="borealis", icon="🌌", badge_color="1;35")
cryo_ui = UI(app_name="cryo", icon="🧊", badge_color="1;36")

# Each instance manages its own styling state
folio_ui.success("PDF compilation finished.")
borealis_ui.action("Synchronizing state across nodes.")
cryo_ui.warn("Cache utilization exceeds 85%.")
```
