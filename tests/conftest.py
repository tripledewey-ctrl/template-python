from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def picture_tree(tmp_path: Path) -> Path:
    """Ordnerstruktur mit Bildern, Nicht-Bildern und versteckten Dateien."""
    (tmp_path / "urlaub").mkdir()
    (tmp_path / "urlaub" / "strand.JPG").write_bytes(b"x" * 2048)
    (tmp_path / "urlaub" / "notizen.txt").write_text("kein Bild")
    (tmp_path / "logo.png").write_bytes(b"x" * 10)
    (tmp_path / "icon.webp").write_bytes(b"")
    (tmp_path / ".versteckt").mkdir()
    (tmp_path / ".versteckt" / "geheim.png").write_bytes(b"x")
    (tmp_path / ".thumb.jpg").write_bytes(b"x")
    return tmp_path
