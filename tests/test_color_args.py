import argparse
from prism.color import add_color_args, apply_color_args, handle_color_args
from prism.engine import UI


def test_add_color_args():
    parser = argparse.ArgumentParser()
    add_color_args(parser)

    args = parser.parse_args(["--color", "always"])
    assert args.color == "always"
    assert args.no_color is False

    args_no = parser.parse_args(["--no-color"])
    assert args_no.no_color is True


def test_handle_color_args():
    custom_ui = UI(app_name="test")

    mode = handle_color_args(["--no-color"], ui=custom_ui)
    assert mode == "never"
    assert custom_ui.use_color is False

    mode = handle_color_args(["--color=always"], ui=custom_ui)
    assert mode == "always"
    assert custom_ui.use_color is True

    mode = handle_color_args(["--color", "never"], ui=custom_ui)
    assert mode == "never"
    assert custom_ui.use_color is False


def test_apply_color_args():
    custom_ui = UI(app_name="test")
    parser = argparse.ArgumentParser()
    add_color_args(parser)

    args = parser.parse_args(["--no-color"])
    mode = apply_color_args(args, ui=custom_ui)
    assert mode == "never"
    assert custom_ui.use_color is False

    args = parser.parse_args(["--color", "always"])
    mode = apply_color_args(args, ui=custom_ui)
    assert mode == "always"
    assert custom_ui.use_color is True
