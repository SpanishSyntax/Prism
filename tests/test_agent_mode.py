"""Comprehensive tests for Prism's Agent / AI Mode."""

import argparse
import io
import os
import pytest

from prism import (
    UI,
    add_agent_args,
    apply_agent_args,
    check_agent_env,
    confirm_input,
    handle_agent_args,
    multiselect_menu,
    prompt_input,
    render_error_panel,
    render_panel,
    select_menu,
    strip_ansi,
)
from prism.styling import Styler


def test_agent_env_detection(monkeypatch):
    monkeypatch.delenv("ICEBERG_AGENT_MODE", raising=False)
    monkeypatch.delenv("PRISM_AGENT_MODE", raising=False)
    monkeypatch.delenv("AGENT_MODE", raising=False)
    assert not check_agent_env()

    monkeypatch.setenv("ICEBERG_AGENT_MODE", "1")
    assert check_agent_env()

    styler = Styler(app_name="snowpack", icon="❄️")
    assert styler.is_agent
    assert styler.badge() == "[snowpack]"


def test_styler_agent_mode_outputs():
    stream = io.StringIO()
    styler = Styler(app_name="barograph", icon="📈", stream=stream, agent_mode=True)
    assert styler.is_agent
    assert styler.badge() == "[barograph]"

    styler.success("Operation complete")
    styler.info("Processing data")
    styler.warn("Rate limit approaching")
    styler.action("Executing step")

    out = stream.getvalue()
    assert "[barograph] [ok] Operation complete" in out
    assert "[barograph] Processing data" in out
    assert "[barograph] [warn] Rate limit approaching" in out
    assert "[barograph] Executing step" in out
    # Ensure no emojis leaked into agent output
    assert "📈" not in out
    assert "✔" not in out
    assert "⚡" not in out


def test_panel_agent_mode_strips_emojis():
    stream = io.StringIO()
    styler = Styler(app_name="basecamp", icon="⛺", stream=stream, agent_mode=True)
    render_panel("⛺  Basecamp Roles Registry", ["Role: snowpack"], styler=styler, stream=stream)

    out = stream.getvalue()
    assert "=== Basecamp Roles Registry ===" in out
    assert "⛺" not in out
    assert "Role: snowpack" in out


def test_panel_agent_mode():
    stream = io.StringIO()
    styler = Styler(app_name="basecamp", icon="⛺", stream=stream, agent_mode=True)
    render_panel("SYSTEM STATUS", ["Service: Nominal", "Version: 1.0.0"], styler=styler, stream=stream)

    out = stream.getvalue()
    assert "=== SYSTEM STATUS ===" in out
    assert "Service: Nominal" in out
    assert "Version: 1.0.0" in out
    # Ensure Unicode box borders are completely omitted
    assert "╭" not in out
    assert "╰" not in out
    assert "│" not in out


def test_error_panel_agent_mode():
    stream = io.StringIO()
    styler = Styler(app_name="borealis", icon="🌌", stream=stream, agent_mode=True)
    render_error_panel("CRITICAL ERROR", ["Connection refused", "Port 8080 unreachable"], styler=styler, stream=stream)

    out = stream.getvalue()
    assert "ERROR: CRITICAL ERROR" in out
    assert "Connection refused" in out
    assert "Port 8080 unreachable" in out
    assert "╭" not in out


def test_inputs_non_blocking_in_agent_mode():
    styler = Styler(app_name="sled", agent_mode=True)

    val = prompt_input("Enter target path", default="/var/log", styler=styler)
    assert val == "/var/log"

    confirmed = confirm_input("Proceed with build?", default=True, styler=styler)
    assert confirmed is True


def test_menus_non_blocking_in_agent_mode():
    styler = Styler(app_name="snowpack", agent_mode=True)

    choice = select_menu("Select compiler mode:", [("typst", "Typst"), ("latex", "LaTeX")], default_index=1, styler=styler)
    assert choice == "latex"

    multi = multiselect_menu("Pick assets:", ["a.png", "b.png"], preselected=["b.png"], styler=styler)
    assert multi == ["b.png"]


def test_cli_agent_args_handling():
    parser = argparse.ArgumentParser()
    add_agent_args(parser)

    # Test -A
    args = parser.parse_args(["-A"])
    assert args.agent is True
    assert args.json is False

    ui_inst = UI(app_name="test")
    is_agent, is_json = handle_agent_args(["--json"], ui=ui_inst)
    assert is_agent is True
    assert is_json is True
    assert ui_inst.is_agent is True
    assert ui_inst.is_json is True
