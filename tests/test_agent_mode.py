"""Comprehensive tests for Prism's Agent / AI Mode."""

import argparse
import io

from prism import (
    UI,
    add_agent_args,
    check_agent_env,
    confirm_input,
    handle_agent_args,
    multiselect_menu,
    prompt_input,
    render_error_panel,
    render_panel,
    select_menu,
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
    render_panel(
        "⛺  Basecamp Roles Registry", ["Role: snowpack"], styler=styler, stream=stream
    )

    out = stream.getvalue()
    assert "[Basecamp Roles Registry]" in out
    assert "===" not in out
    assert "⛺" not in out
    assert "Role: snowpack" in out


def test_panel_agent_mode():
    stream = io.StringIO()
    styler = Styler(app_name="basecamp", icon="⛺", stream=stream, agent_mode=True)
    render_panel(
        "SYSTEM STATUS",
        ["Service: Nominal", "Version: 1.0.0"],
        styler=styler,
        stream=stream,
    )

    out = stream.getvalue()
    assert "[SYSTEM STATUS]" in out
    assert "===" not in out
    assert "Service: Nominal" in out
    assert "Version: 1.0.0" in out
    # Ensure Unicode box borders and decorative margin lines are completely omitted
    assert "╭" not in out
    assert "╰" not in out
    assert "│" not in out


def test_error_panel_agent_mode():
    stream = io.StringIO()
    styler = Styler(app_name="borealis", icon="🌌", stream=stream, agent_mode=True)
    render_error_panel(
        "CRITICAL ERROR",
        ["Connection refused", "Port 8080 unreachable"],
        styler=styler,
        stream=stream,
    )

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

    choice = select_menu(
        "Select compiler mode:",
        [("typst", "Typst"), ("latex", "LaTeX")],
        default_index=1,
        styler=styler,
    )
    assert choice == "latex"

    multi = multiselect_menu(
        "Pick assets:", ["a.png", "b.png"], preselected=["b.png"], styler=styler
    )
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


def test_is_interactive_property(monkeypatch):
    ui_inst = UI(app_name="test")
    # In agent mode, is_interactive is always False
    ui_inst.set_agent_mode(agent=True)
    assert ui_inst.is_interactive is False

    ui_inst.set_agent_mode(agent=False)
    # Mock TTY for stdin
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert ui_inst.is_interactive is True

    # When JSON mode active, not interactive
    ui_inst.set_agent_mode(agent=True, json_output=True)
    assert ui_inst.is_interactive is False


def test_ui_json_emitter():
    stream = io.StringIO()
    ui_inst = UI(app_name="test", stream=stream)
    ui_inst.json({"key": "value"}, status="ok")
    out = stream.getvalue()
    assert '"status": "ok"' in out
    assert '"key": "value"' in out

    # List payload with status wrapping
    stream = io.StringIO()
    ui_inst.set_stream(stream)
    ui_inst.json(["item1", "item2"], status="ok")
    out = stream.getvalue()
    assert '"status": "ok"' in out
    assert '"items": [' in out


def test_ui_version_and_handle_version_arg():
    from prism import handle_version_arg

    # Human mode
    stream = io.StringIO()
    ui_inst = UI(app_name="demo", stream=stream)
    assert handle_version_arg(["--version"], "1.2.3", ui=ui_inst) is True
    out = stream.getvalue()
    assert "demo 1.2.3" in out
    assert "v1.2.3" in out

    # Agent mode
    stream = io.StringIO()
    ui_inst = UI(app_name="demo", stream=stream, agent_mode=True)
    assert handle_version_arg(["-V"], "v1.2.3", ui=ui_inst) is True
    assert stream.getvalue().strip() == "demo 1.2.3"

    # JSON mode
    stream = io.StringIO()
    ui_inst = UI(app_name="demo", stream=stream)
    ui_inst.set_agent_mode(agent=True, json_output=True)
    assert handle_version_arg(["version"], "1.2.3", ui=ui_inst) is True
    assert '"version": "1.2.3"' in stream.getvalue()
    assert '"app": "demo"' in stream.getvalue()

    # Non-version argument returns False
    assert handle_version_arg(["build", "file.md"], "1.2.3", ui=ui_inst) is False


def test_get_agent_and_json_env():
    from prism import get_agent_env, get_json_env

    a_env = get_agent_env({"CUSTOM": "val"})
    assert a_env["ICEBERG_AGENT_MODE"] == "1"
    assert a_env["PRISM_AGENT_MODE"] == "1"
    assert a_env["CUSTOM"] == "val"
    assert "ICEBERG_JSON_MODE" not in a_env

    j_env = get_json_env()
    assert j_env["ICEBERG_AGENT_MODE"] == "1"
    assert j_env["ICEBERG_JSON_MODE"] == "1"
    assert j_env["PRISM_JSON_MODE"] == "1"


def test_help_builder_human_and_agent():
    from prism import HelpBuilder

    hb = (
        HelpBuilder(app_name="snowpack", tagline="Document Compiler", version="0.1.0")
        .set_usage(["snowpack [file]", "snowpack build [file]"])
        .add_command("build", "Compile document")
        .add_option("-o, --output PATH", "Output filename")
        .add_example("snowpack report.md", "Compile report")
    )

    human = hb.render(is_agent=False)
    assert "Usage:" in human
    assert "snowpack [file]" in human
    assert "Commands:" in human
    assert "build" in human
    assert "Compile document" in human
    assert "Options:" in human
    assert "Examples:" in human

    agent = hb.render(is_agent=True)
    assert "snowpack v0.1.0 - Document Compiler" in agent
    assert "Usage: snowpack [file]" in agent
    assert "       snowpack build [file]" in agent
    assert "Commands:" in agent
    assert "Options:" in agent
    assert "\033[" not in agent


def test_agent_mode_strips_caller_emojis_and_margins():
    stream = io.StringIO()
    ui_inst = UI(app_name="prism", stream=stream, agent_mode=True)
    ui_inst.info("🚀 Launching rocket to Mars 🌌")
    ui_inst.success("✨ All systems nominal ✔")
    ui_inst.warn("⚠️ High solar radiation ⚡")
    ui_inst.action("📡 Calibrating telemetry 🛰️")

    out = stream.getvalue()
    assert "[prism] Launching rocket to Mars" in out
    assert "[prism] [ok] All systems nominal" in out
    assert "[prism] [warn] High solar radiation" in out
    assert "[prism] Calibrating telemetry" in out
    # Verify no emojis leak through
    for emoji in ("🚀", "🌌", "✨", "✔", "⚠️", "⚡", "📡", "🛰️"):
        assert emoji not in out

    # Test header and subheader: no margin lines (no === or ---)
    stream_hdr = io.StringIO()
    ui_inst.set_stream(stream_hdr)
    ui_inst.header("Fleet Status 🚢")
    ui_inst.subheader("Telemetry Units 🌡️")
    hdr_out = stream_hdr.getvalue()
    assert "[Fleet Status]" in hdr_out
    assert "Telemetry Units:" in hdr_out
    assert "===" not in hdr_out
    assert "---" not in hdr_out
    assert "🚢" not in hdr_out
    assert "🌡️" not in hdr_out


def test_ui_data_polymorphic():
    headers = ["Name", "Role", "Ready"]
    rows = [["Prism", "UI", True], ["Sled", "MCP", True]]

    # 1. JSON mode
    stream_json = io.StringIO()
    ui_json = UI(app_name="test", stream=stream_json)
    ui_json.set_agent_mode(agent=True, json_output=True)
    ui_json.data(headers=headers, rows=rows, title="Fleet")
    out_j = stream_json.getvalue()
    assert '"title": "Fleet"' in out_j
    assert '"Name": "Prism"' in out_j

    # 2. TOON mode
    stream_toon = io.StringIO()
    ui_toon = UI(app_name="test", stream=stream_toon)
    ui_toon.set_agent_mode(agent=True, toon_output=True)
    ui_toon.data(headers=headers, rows=rows, title="Fleet")
    out_t = stream_toon.getvalue()
    assert "[Fleet]" in out_t
    assert "items[2]{Name,Role,Ready}:" in out_t
    assert "Prism,UI,true" in out_t

    # 3. Agent mode (default)
    stream_agent = io.StringIO()
    ui_agent = UI(app_name="test", stream=stream_agent, agent_mode=True)
    ui_agent.data(headers=headers, rows=rows, title="Fleet")
    out_a = stream_agent.getvalue()
    assert "[Fleet]" in out_a
    assert "items[2]{Name,Role,Ready}:" in out_a
    assert "Prism,UI,true" in out_a
