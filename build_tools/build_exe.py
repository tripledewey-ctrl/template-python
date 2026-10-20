"""Baut eine einzelne ausfuehrbare Datei mit PyInstaller.

Aufruf: ``uv run --group exe poe build-exe``.
Ergebnis: ``dist/bildfinder-<version>-<os>-<arch>[.exe]``.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def artifact_name(version: str) -> str:
    system = {"win32": "windows", "darwin": "macos"}.get(sys.platform, sys.platform)
    machine = platform.machine().lower().replace("amd64", "x64").replace("x86_64", "x64")
    return f"bildfinder-{version}-{system}-{machine}"


def main() -> int:
    try:
        import PyInstaller.__main__ as pyinstaller
    except ImportError:
        print("PyInstaller fehlt: 'uv run --group exe poe build-exe' verwenden.", file=sys.stderr)
        return 1

    from bildfinder import __version__

    name = artifact_name(__version__)
    pyinstaller.run(
        [
            str(ROOT / "build_tools" / "entry.py"),
            "--name",
            name,
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--clean",
            "--copy-metadata",
            "bildfinder",
            "--distpath",
            str(ROOT / "dist"),
            "--workpath",
            str(ROOT / "build" / "pyinstaller"),
            "--specpath",
            str(ROOT / "build"),
        ]
    )
    print(f"Fertig: dist/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
