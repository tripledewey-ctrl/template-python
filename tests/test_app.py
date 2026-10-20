from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from bildfinder import __version__, app


def test_cli_lists_images(picture_tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert app.main(["--cli", str(picture_tree)]) == 0
    out = capsys.readouterr().out
    assert "strand.JPG" in out
    assert "3 Bild(er) gefunden" in out


def test_cli_flat_and_limit(picture_tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert app.main(["--cli", "--flach", "--limit", "1", str(picture_tree)]) == 0
    assert "1 Bild(er) gefunden" in capsys.readouterr().out


def test_cli_missing_folder(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert app.main(["--cli", str(tmp_path / "fehlt")]) == 2
    assert "Fehler" in capsys.readouterr().err


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        app.main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_gui_mode_dispatches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[Path] = []

    def fake_run_gui(folder: Path) -> int:
        calls.append(folder)
        return 0

    fake_gui = types.ModuleType("bildfinder.gui")
    fake_gui.run_gui = fake_run_gui  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "bildfinder.gui", fake_gui)
    assert app.main([str(tmp_path)]) == 0
    assert calls == [tmp_path]


def test_missing_std_streams_are_replaced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    app._ensure_std_streams()
    assert sys.stdout is not None
    assert sys.stderr is not None
    sys.stdout.close()
    sys.stderr.close()
