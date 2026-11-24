"""The static community check: what a contribution must satisfy before anything is installed or run."""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_community", ROOT / "scripts" / "check_community.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

GOOD = '''"""Teaches one thing."""
from manim import Text

from ...registry import Param as P, component


@component("my_thing", "Shows a thing.", {"x": P("integer", "A number", default=1)}, {"x": 1})
def my_thing(ctx, x=1):
    ctx.play(Text("hi"))
'''


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    (tmp_path / "community").mkdir()
    (tmp_path / "tests").mkdir()
    monkeypatch.setattr(cc, "COMMUNITY", tmp_path / "community")
    monkeypatch.setattr(cc, "TESTS", tmp_path / "tests")
    monkeypatch.setattr(cc, "ROOT", tmp_path)
    return tmp_path


def check(repo, src, name="my_thing"):
    f = repo / "community" / f"{name}.py"
    f.write_text(src)
    return cc.check_component_file(f)


def test_the_real_repository_passes():
    assert cc.main([]) == 0


def test_good_component_passes(repo):
    assert check(repo, GOOD) == []


@pytest.mark.parametrize("src, needle", [
    (GOOD.replace('"""Teaches one thing."""\n', ""), "docstring"),
    (GOOD.replace("from manim import Text", "from manim import *"), "import *"),
    (GOOD + "\nprint('x')\n", "print()"),
    (GOOD.replace('"my_thing"', '"other_name"', 1), "must match"),
    (GOOD + '\n@component("second", "d", {}, {})\ndef second(ctx): pass\n', "exactly one"),
    (GOOD.replace("from manim import Text", "import os"), "safety"),
    ("def broken(:\n", "syntax"),
    (GOOD + "#" * 41000, "limit"),
])
def test_rules(repo, src, needle):
    assert any(needle in p for p in check(repo, src)), check(repo, src)


def test_bad_file_name(repo):
    assert any("snake_case" in p for p in check(repo, GOOD.replace("my_thing", "MyThing"), name="MyThing"))


def test_component_declared_with_name_keyword_is_read(repo):
    src = GOOD.replace('@component("my_thing", "Shows a thing.", {"x": P("integer", "A number", default=1)}, {"x": 1})',
                       '@component(name="my_thing", description="Shows a thing.", params={}, example={})')
    assert src != GOOD and check(repo, src) == []


def test_layout_rejects_stray_files_and_orphan_tests(repo):
    (repo / "community" / "README.md").write_text("x")
    (repo / "community" / "data.json").write_text("{}")
    (repo / "community" / "my_thing.py").write_text(GOOD)
    (repo / "tests" / "test_ghost.py").write_text("")
    (repo / "tests" / "test_loader.txt").write_text("")
    text = "\n".join(cc.check_layout())
    assert "data.json" in text and "ghost" in text and "test_loader.txt" in text and "README.md:" not in text


def test_its_test_file_may_only_use_allowed_imports(repo):
    (repo / "tests" / "test_my_thing.py").write_text("import subprocess\n")
    assert any("subprocess" in p for p in check(repo, GOOD))
