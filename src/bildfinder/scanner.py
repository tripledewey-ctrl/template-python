"""Plattformunabhaengige Suche nach Bilddateien (ohne GUI-Abhaengigkeiten)."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".bmp", ".gif", ".heic", ".ico", ".jpeg", ".jpg", ".png", ".svg", ".tif", ".tiff", ".webp"}
)


@dataclass(frozen=True, slots=True)
class ImageFile:
    path: Path
    size: int

    @property
    def name(self) -> str:
        return self.path.name


def is_image(path: Path) -> bool:
    """True, wenn die Dateiendung auf ein Bild hindeutet."""
    return path.suffix.lower() in IMAGE_EXTENSIONS


def _walk(root: Path, recursive: bool, include_hidden: bool) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda _err: None):
        if not include_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames.sort()
        for filename in sorted(filenames):
            if include_hidden or not filename.startswith("."):
                yield Path(dirpath) / filename
        if not recursive:
            return


def find_images(
    root: Path | str,
    *,
    recursive: bool = True,
    include_hidden: bool = False,
    limit: int | None = None,
) -> list[ImageFile]:
    """Liefert alle Bilder unterhalb von ``root``, sortiert nach Pfad.

    Nicht lesbare Ordner und Dateien werden stillschweigend uebersprungen.
    """
    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Kein Ordner: {root_path}")
    if limit is not None and limit < 1:
        raise ValueError("limit muss >= 1 sein")

    results: list[ImageFile] = []
    for path in _walk(root_path, recursive, include_hidden):
        if not is_image(path):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        results.append(ImageFile(path=path, size=stat.st_size))
        if limit is not None and len(results) >= limit:
            break
    return results


def format_size(size: int) -> str:
    """Formatiert Bytes menschenlesbar, z.B. ``1.5 MB``."""
    if size < 0:
        raise ValueError("size darf nicht negativ sein")
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")  # pragma: no cover


def default_search_dir() -> Path:
    """Bevorzugt den Bilder-Ordner des Benutzers, sonst das Home-Verzeichnis."""
    home = Path.home()
    for name in ("Pictures", "Bilder"):
        candidate = home / name
        if candidate.is_dir():
            return candidate
    return home
