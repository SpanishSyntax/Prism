# Getting Started

Prism is designed for rapid integration with zero external runtime dependencies. It operates under standard Python 3.10+ environments and embeds natively into Nix flakes.

---

## Installation

### Nix Environment (Recommended)

To run Prism ephemerally without installing:

```bash
nix run github:SpanishSyntax/Prism -- --demo
```

To enter a development shell containing Prism:

```bash
nix develop github:SpanishSyntax/Prism
```

### Python Package (pip / pyproject)

Install from local source:

```bash
git clone https://github.com/SpanishSyntax/Prism.git
cd Prism
pip install .
```

Or install in editable mode for development:

```bash
pip install -e .
```

---

## Quick Start

### Basic Status Logging

Prism exposes a pre-instantiated global interface facade via `prism.ui`:

```python
from prism import ui

ui.success("Build derivation completed successfully.")
ui.info("Configuration loaded from /etc/frost/system.toml")
ui.action("Dispatching job to background worker swarm")
ui.warn("Flake lockfile is older than 30 days")
ui.error("Subprocess terminated with non-zero exit code 1")
```

### Rounded Panels

Render terminal width-aware bounding boxes with customizable borders:

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
    width=64,
)
```

### Diagnostic Error Box

Diagnostic error panels format exceptions and diagnostic traces with red borders and structured formatting:

```python
from prism import ui

ui.error_panel(
    "Evaluation Failure",
    [
        "error: attribute 'prism' missing in pkgs.python3Packages",
        "       at /etc/nixos/flake.nix:42:15",
    ],
)
```

### Threaded Spinners

Wrap blocking operations inside a context manager. The cursor is automatically hidden and cleanly restored even upon early exit or exceptions:

```python
import time
from prism import ui

with ui.spinner("Resolving flake inputs..."):
    time.sleep(1.2)

ui.success("Inputs materialized.")
```

### Interactive Menus

#### Single Selection

```python
from prism import ui

target = ui.select(
    "Select output format",
    [
        ("pdf", "PDF Document", "Compiled via Typst engine"),
        ("slides", "Presentation Deck", "16:9 widescreen slides"),
        ("html", "Web Article", "Standalone HTML5 document"),
    ],
)

print(f"Target selected: {target}")
```

#### Multi Selection

```python
from prism import ui

selected = ui.multiselect(
    "Select services to restart",
    [
        ("docker", "Docker Engine"),
        ("systemd", "Systemd User Units"),
        ("pipewire", "PipeWire Sound Server"),
        ("tailscale", "Tailscale VPN Mesh"),
    ],
    preselected={"docker", "systemd"},
)

print(f"Selected: {selected}")
```

---

## Nix Integration

### Flake Input

To include Prism in a system or project flake:

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
    nixosConfigurations.workstation = nixpkgs.lib.nixosSystem {
      modules = [
        {
          nixpkgs.overlays = [ prism.overlays.default ];
          environment.systemPackages = with nixpkgs.legacyPackages.x86_64-linux; [
            python3Packages.prism
          ];
        }
      ];
    };
  };
}
```

### Home Manager Module

Prism provides an integrated Home Manager module:

```nix
{
  imports = [ inputs.prism.homeManagerModules.default ];

  programs.prism.enable = true;
}
```
