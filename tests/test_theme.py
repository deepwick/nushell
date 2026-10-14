import re
import shutil
import subprocess
from pathlib import Path

import pytest

from deepwick_spec.ansi import runs, style_of
from deepwick_spec.check_port import check_port
from deepwick_spec.palette import load_palette
from deepwick_spec.tui import capture, tmux_available

REPO = Path(__file__).resolve().parents[1]
PALETTE = load_palette()
C = PALETTE.colors


def isolated_env(tmp_path, **extra):
    dirs = {"HOME": tmp_path / "home"}
    for kind in ("CONFIG", "DATA", "STATE", "CACHE"):
        dirs[f"XDG_{kind}_HOME"] = tmp_path / kind.lower()
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    env = {key: str(path) for key, path in dirs.items()}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    env.update({key: str(value) for key, value in extra.items()})
    return env


THEME = REPO / "deepwick.nu"
requires_nu = pytest.mark.skipif(shutil.which("nu") is None, reason="requires nu")
renders = pytest.mark.skipif(not (tmux_available() and shutil.which("nu")), reason="requires tmux and nu")
EXPECTED = {
    "shape_internalcall": "'#DCDCAA'", "shape_external": "'#DCDCAA'", "shape_keyword": "'#569CD6'",
    "shape_string": "'#CE9178'", "shape_flag": "'#9CDCFE'", "shape_variable": "'#9CDCFE'",
    "shape_vardecl": "'#9CDCFE'", "shape_int": "'#B5CEA8'", "shape_operator": "'#D4D4D4'",
    "shape_garbage": "{ fg: '#F44747' attr: u }", "header": "{ fg: '#569CD6' attr: b }",
    "hints": "'#6E7899'", "datetime": "'#7A86A8'", "filesize": "'#B5CEA8'",
    "search_result": "{ fg: '#D7BA7D' bg: '#264F78' }",
}


def record_body(text, anchor):
    start = text.index("{", text.index(anchor))
    depth = 0
    for end in range(start, len(text)):
        depth += {"{": 1, "}": -1}.get(text[end], 0)
        if depth == 0:
            return text[start + 1 : end]
    raise AssertionError(f"unbalanced record after {anchor}")


def record_entries(body):
    return dict(re.findall(r"^\s*([a-z][a-z0-9_-]*):\s*(.+?)\s*$", body, re.M))


def theme():
    assert THEME.is_file(), "deepwick.nu missing"
    return record_entries(record_body(THEME.read_text(encoding="utf-8"), "$env.config.color_config ="))


def test_role_values():
    t = theme()
    for key, value in EXPECTED.items():
        assert t[key] == value, key


@requires_nu
def test_covers_every_default_color_key():
    default = subprocess.run(["nu", "-n", "-c", "config nu --default"], capture_output=True, text=True, check=True).stdout
    if "color_config" not in default:
        pytest.skip("default config has no color_config record")
    keys = set(record_entries(record_body(default, "color_config"))) - {"fg", "bg", "attr"}
    assert keys - set(theme()) == set()


def nu_env(tmp_path, cwd):
    env = isolated_env(tmp_path)
    config = Path(env["XDG_CONFIG_HOME"]) / "nushell"
    config.mkdir(parents=True)
    (config / "env.nu").write_text("")
    (config / "config.nu").write_text(
        "$env.config.show_banner = false\n"
        "$env.PROMPT_COMMAND = {|| 'nu' }\n"
        "$env.PROMPT_COMMAND_RIGHT = {|| '' }\n"
        "$env.PROMPT_INDICATOR = {|| '> ' }\n"
        f"source {THEME}\n"
    )
    cwd.mkdir(parents=True, exist_ok=True)
    (cwd / "notes.txt").write_text("deepwick\n")
    return env


@renders
def test_nu_highlights_command_line(tmp_path):
    work = tmp_path / "work"
    text = capture(f"cd {work} && nu", nu_env(tmp_path, work), wait_for="nu>",
                   literal='let x = "hi" | str length --grapheme-clusters')
    assert style_of(text, "let")["fg"] == C["yellow"].lower()
    assert style_of(text, "x")["fg"] == C["lightBlue"].lower()
    assert style_of(text, '"hi"')["fg"] == C["orange"].lower()
    assert style_of(text, "--grapheme-clusters")["fg"] == C["lightBlue"].lower()


@renders
def test_nu_table_header(tmp_path):
    work = tmp_path / "work"
    text = capture(f"cd {work} && nu", nu_env(tmp_path, work), wait_for="nu>",
                   literal="ls", keys=("Enter",), after="modified")
    header = style_of(text, "name")
    assert header["fg"] == C["blue"].lower() and header["bold"]


@renders
def test_nu_completion_menu(tmp_path):
    work = tmp_path / "work"
    text = capture(f"cd {work} && nu", nu_env(tmp_path, work), wait_for="nu>",
                   literal="str ", keys=("Tab",))
    assert any(s["bg"] == C["selection"].lower() for _, s in runs(text))


def test_port_conventions():
    assert check_port(REPO, PALETTE.allowed_hex()) == []
