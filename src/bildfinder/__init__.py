"""Bildfinder - sucht Bilder auf dem Rechner und zeigt sie in einer Liste an."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bildfinder")
except PackageNotFoundError:  # pragma: no cover - nur ohne Installation
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
