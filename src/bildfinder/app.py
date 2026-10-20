"""Einstiegspunkt: startet die GUI oder - mit ``--cli`` - die Konsolenausgabe."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from bildfinder import __version__
from bildfinder.scanner import default_search_dir, find_images, format_size


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bildfinder", description="Sucht Bilder auf dem Rechner und zeigt sie an."
    )
    parser.add_argument("ordner", nargs="?", type=Path, help="Startordner der Suche")
    parser.add_argument("--cli", action="store_true", help="Ergebnis in der Konsole ausgeben")
    parser.add_argument("--flach", action="store_true", help="Unterordner nicht durchsuchen")
    parser.add_argument("--limit", type=int, default=None, help="Maximale Anzahl Treffer")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def run_cli(folder: Path, *, recursive: bool, limit: int | None) -> int:
    try:
        images = find_images(folder, recursive=recursive, limit=limit)
    except (NotADirectoryError, ValueError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2
    for image in images:
        print(f"{format_size(image.size):>10}  {image.path}")
    print(f"{len(images)} Bild(er) gefunden in {folder}")
    return 0


def _ensure_std_streams() -> None:
    # In einer --windowed Exe gibt es keine Konsole: stdout/stderr sind None.
    if sys.stdout is None:
        sys.stdout = Path(os.devnull).open("w")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = Path(os.devnull).open("w")  # noqa: SIM115


def main(argv: Sequence[str] | None = None) -> int:
    _ensure_std_streams()
    args = build_parser().parse_args(argv)
    folder: Path = args.ordner or default_search_dir()
    if args.cli:
        return run_cli(folder, recursive=not args.flach, limit=args.limit)

    from bildfinder.gui import run_gui

    return run_gui(folder)
