"""The sync script: which merged files are proposed to the app, and where they land."""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_to_app", ROOT / "scripts" / "sync_to_app.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

PATHS = ["manimate/", "tests/", "catalog.json"]


def test_load_paths_skips_comments_and_blanks():
    assert s.load_paths("# a comment\n\nmanimate/\n  tests/  \n") == ["manimate/", "tests/"]


def test_the_shipped_path_list_is_valid():
    paths = s.load_paths((ROOT / s.PATHS_FILE).read_text())
    assert paths and all(not p.startswith(("/", ".")) and ".." not in p for p in paths)


@pytest.mark.parametrize("path,expected", [
    ("manimate/components/community/x.py", True),
    ("tests/test_x.py", True),
    ("catalog.json", True),
    ("catalog.json.bak", False),                      # an exact file path is not a prefix
    ("docs/MAINTAINING.md", False),
    (".github/workflows/ci.yml", False),
    ("manimate/__pycache__/x.cpython-312.pyc", False),
    ("manimate/x.pyc", False),
    ("manimate_other/x.py", False),                   # a directory entry matches whole folders only
])
def test_is_synced(path, expected):
    assert s.is_synced(path, PATHS) is expected


def test_apply_copies_updates_and_deletes_only_what_changed(tmp_path):
    app = tmp_path / "app"
    (app / "renderer/manimate").mkdir(parents=True)
    (app / "renderer/manimate/old.py").write_text("old")
    (app / "renderer/manimate/app_only.py").write_text("keep me")
    blobs = {"manimate/new.py": b"new", "manimate/upd.py": b"upd"}
    lines = s.apply([("A", "manimate/new.py"), ("M", "manimate/upd.py"), ("D", "manimate/old.py")],
                    blobs.__getitem__, app, "renderer")
    assert (app / "renderer/manimate/new.py").read_bytes() == b"new"
    assert (app / "renderer/manimate/upd.py").read_bytes() == b"upd"
    assert not (app / "renderer/manimate/old.py").exists()
    assert (app / "renderer/manimate/app_only.py").read_text() == "keep me"      # never touched
    assert len(lines) == 3 and "removed" in lines[2]


def test_deleting_a_file_the_app_never_had_is_fine(tmp_path):
    assert s.apply([("D", "manimate/gone.py")], lambda p: b"", tmp_path, "renderer")


def test_apply_refuses_to_escape_the_app_checkout(tmp_path):
    with pytest.raises(ValueError):
        s.apply([("A", "../../evil.py")], lambda p: b"x", tmp_path / "app", "renderer")
