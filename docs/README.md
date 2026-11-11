<p align="center">
  <img src="assets/banner.png" alt="Glass prism refracting light into spectral color palette" width="100%" />
</p>

# Prism 🌈

A crystalline, zero-dependency CLI design system and terminal UI engine for Python and Nix.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/SpanishSyntax/Prism/blob/main/LICENSE)
[![Built with Nix](https://img.shields.io/badge/Built_with-Nix-5277C3.svg?logo=nixos&logoColor=white)](https://github.com/SpanishSyntax/Prism/blob/main/flake.nix)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://github.com/SpanishSyntax/Prism/blob/main/pyproject.toml)

Prism provides the shared terminal design language, logging primitives, width-aware bounding boxes, braille spinners, and interactive selection menus powering the **Frost** iceberg ecosystem (`Folio`, `Cryo`, `Borealis`, `Firn`, `Glaze`, `Flaker`).

---

## Why "Prism"? (The Lore)

> **ice prism** (`/ˈprɪz.əm/`) — *noun:* A microscopic, hexagonal ice crystal suspended in frozen polar air, refracting cold winter sunlight into sun dogs, luminous halos, and sharp spectral color pillars.

In the arctic atmosphere, microscopic ice prisms take unorganized white sunlight and refract it into crisp, geometric halos of pure color.

**Prism organizes terminal output into crystalline structure:**
- **Spectral Refraction**: Formats unstructured stdout/stderr into structured panels, status badges, tabular summaries, and interactive selection lists.
- **Crystalline Purity**: Operates with zero runtime dependencies beyond Python's standard library (`termios`, `tty`, `select`, `shutil`, `threading`), providing uniform ANSI palettes, typography tracking, and semantic CLI components across Python and Nix.

---

## Key Capabilities

- **Zero External Runtime Dependencies**: Built entirely upon Python's standard library. Avoids heavy dependencies such as `rich`, `curses`, or `prompt_toolkit`.
- **Responsive Rounded Panels**: Terminal width-aware bounding boxes (`╭─╮│╰─╯`) that automatically adapt to terminal columns and truncate overflowing lines with visual ellipsis.
- **Threaded Braille Spinners**: Non-blocking background spinners with clean signal handling and automated cursor restoration.
- **Interactive Keyboard Menus**: Height- and width-aware single- and multi-selection menus supporting arrow navigation, vi keys (`j`/`k`), spacebar toggling, and list pagination.
- **Polymorphic Output Modes**: Automatic content negotiation between human TTYs (rich ANSI, TrueColor), agent runners (stripped ANSI, token-efficient single-line output), JSON (`--json`), and TOON (`--toon`).
- **Nix-Native Packaging**: Out-of-the-box Nix Flake exposing apps, packages, overlays (`overlays.default`), and Home Manager modules.

---

## Quick Demo

```bash
# Run the interactive live demo directly via Nix
nix run github:SpanishSyntax/Prism -- --demo
```

Or invoke within a local Python virtual environment:

```bash
python -m prism --demo
```

---

## Table of Contents

- [Getting Started](getting-started.md)
  - [Installation](getting-started.md#installation)
  - [Quick Start](getting-started.md#quick-start)
  - [Nix Integration](getting-started.md#nix-integration)
- [Architecture & Design](architecture.md)
  - [Design Philosophy](architecture.md#design-philosophy)
  - [The Lore: Ice Prisms](architecture.md#why-prism-the-lore)
  - [Subsystem Hierarchy](architecture.md#subsystem-hierarchy)
  - [Execution Modes](architecture.md#execution-modes)
- [Primitives Reference](primitives.md)
  - [Status Badges & Logging](primitives.md#status-badges--logging)
  - [Bounding Panels & Error Boxes](primitives.md#bounding-panels--diagnostic-boxes)
  - [Status Cards & Dashboards](primitives.md#status-cards--dashboards)
  - [Threaded Braille Spinners](primitives.md#threaded-braille-spinners)
  - [Interactive Selection Menus](primitives.md#interactive-selection-menus)
  - [Fuzzy Searchbox](primitives.md#fuzzy-searchbox)
  - [Data Tables & Encoders](primitives.md#data-tables--encoders)
- [Integration & Usage Guide](usage.md)
  - [CLI Argument Integration](usage.md#cli-argument-integration)
  - [Help Screen Generation](usage.md#help-screen-generation)
  - [Machine & Agent Automation](usage.md#machine--agent-automation)
  - [Custom Facades & App Branding](usage.md#custom-facades--app-branding)
