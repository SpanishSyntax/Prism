<p align="center">
  <img src="assets/banner.png" alt="Glass prism refracting light into spectral color palette" width="100%" />
</p>

# Prism 🌈

A crystalline, zero-dependency CLI design system and terminal UI engine for Python and Nix.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Built with Nix](https://img.shields.io/badge/Built_with-Nix-5277C3.svg?logo=nixos&logoColor=white)](flake.nix)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)

Prism provides the shared terminal design language, logging primitives, bounding boxes, braille spinners, and interactive selection menus powering the **Frost** iceberg ecosystem (`Folio`, `Cryo`, `Borealis`, `Firn`, `Glaze`, `Flaker`).

> [!TIP]
> **Documentation Site:** Complete API references, component parameters, and interactive guides are available at the **[Prism Documentation Site](https://spanishsyntax.github.io/Prism)**.

---

## Why "Prism"? (The Lore)

> **ice prism** (`/ˈprɪz.əm/`) — *noun:* A microscopic, hexagonal ice crystal suspended in frozen polar air, refracting cold winter sunlight into sun dogs, luminous halos, and sharp spectral color pillars.

In the arctic atmosphere, microscopic ice prisms take unorganized white sunlight and refract it into crisp, geometric halos of pure color.

**Prism organizes terminal output into crystalline structure:**
- **Spectral Refraction**: A zero-dependency CLI design system and terminal UI engine that formats raw text into structured panels, status badges, tables, and progress indicators.
- **Crystalline Purity**: Operates with zero runtime dependencies beyond Python's standard library (`termios`, `tty`, `select`, `shutil`, `threading`), providing uniform ANSI color palettes, typography tracking, and semantic CLI components across Python and Nix.

---

## Highlights

- **Zero External Runtime Dependencies**: Implemented entirely with Python's standard library (`termios`, `tty`, `select`, `shutil`, `threading`). Avoids heavy runtime dependencies like `rich`, `curses`, or `prompt_toolkit`.
- **Responsive Rounded Panels**: Terminal width-aware bounding boxes (`╭─╮│╰─╯`) that auto-adapt to terminal size and gracefully truncate overflowing text.
- **Threaded Braille Spinners**: Smooth background spinners that restore the terminal cursor and cleanly format stdout/stderr upon completion.
- **Interactive Keyboard Menus**: Height- and width-aware single-selection and multi-selection menus supporting arrow keys, vim bindings (`j`/`k`), spacebar toggling, and list pagination.
- **Adaptive Color Support**: ANSI styling with automatic detection for TTYs, `NO_COLOR`, `FORCE_COLOR`, and 24-bit TrueColor.
- **Nix-Native Architecture**: Out-of-the-box Nix Flake exposing apps, packages, `overlays.default` (`pythonPackagesExtensions`), and Home Manager modules.

---

## Quick Start

### Try the Interactive Demo

```bash
nix run github:SpanishSyntax/Prism -- --demo
```

Or from a local clone:

```bash
nix develop -c python -m prism --demo
```

---

## Usage in Python

### Basic Status & Badges

```python
from prism import ui

# Status logging with icons
ui.success("Derivation built successfully")
ui.action("Dispatching job to background runner")
ui.info("Configuration loaded from ~/.config")
ui.warn("Flake lockfile is older than 30 days")
ui.error("Subprocess terminated unexpectedly")
```

### Rounded Panels & Dashboards

```python
from prism import ui

ui.panel(
    "FLEET STATUS",
    [
        "All 7 iceberg projects are operational",
        "Architecture: NixOS Unstable / Flakes",
        "Active Workspace: ~/Workspace/Production",
    ],
    border_color="0;36",
    width=60,
)
```

### Diagnostic Error Box

```python
from prism import ui

ui.error_panel(
    "Evaluation Error",
    [
        "error: attribute 'prism' missing in pkgs.python3Packages",
        "       at /etc/nixos/flake.nix:42:15",
    ],
)
```

### Threaded Spinner

```python
import time
from prism import ui

with ui.spinner("Resolving flake inputs..."):
    time.sleep(1.5)
ui.success("Inputs materialized")
```

### Interactive Single-Select Menu

```python
from prism import ui

choice = ui.select(
    "Select target format",
    [
        ("pdf", "PDF Document", "Compiled via Typst engine"),
        ("slides", "Presentation Slides", "16:9 widescreen deck"),
        ("html", "Web Article", "Standalone HTML5 reader"),
    ],
)
print(f"Selected: {choice}")
```

### Interactive Multi-Select Menu

```python
from prism import ui

# Space to toggle, 'a' to toggle all, Enter to confirm
selected = ui.multiselect(
    "Select icebergs to audit",
    [
        ("folio", "Folio"),
        ("cryo", "Cryo"),
        ("borealis", "Borealis"),
        ("glaze", "Glaze"),
    ],
    preselected={"folio", "cryo"},
)
```

### Prompts & Confirmations

```python
from prism import ui

name = ui.prompt("Project name", default="frost-workspace")
if ui.confirm("Initialize git repository?", default=True):
    ui.success("Git initialized")
```

---

## Custom App Branding

You can instantiate customized `UI` facades for any project with specific badges and icons:

```python
from prism import UI

folio_ui = UI(app_name="folio", icon="❄️", badge_color="1;34")
borealis_ui = UI(app_name="borealis", icon="🌌", badge_color="1;35")
cryo_ui = UI(app_name="cryo", icon="🧊", badge_color="1;36")

folio_ui.success("Document assembled")
```

---

## Nix Integration

### Flake Input

Add Prism to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    prism = {
      url = "github:SpanishSyntax/Prism";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, prism, ... }: {
    # Consume as Python package via overlay
    nixosConfigurations.workstation = nixpkgs.lib.nixosSystem {
      modules = [
        {
          nixpkgs.overlays = [ prism.overlays.default ];
          environment.systemPackages = [
            # pkgs.python3Packages.prism is now available
          ];
        }
      ];
    };
  };
}
```

### Home Manager Module

```nix
{
  imports = [ inputs.prism.homeManagerModules.default ];

  programs.prism.enable = true;
}
```

---

## Testing

Run the full pytest suite inside the Nix devShell:

```bash
nix develop -c pytest
```

---

## License

MIT © [SpanishSyntax](https://github.com/SpanishSyntax)
