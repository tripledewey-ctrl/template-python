from __future__ import annotations

import sys

import pytest

from build_exe import artifact_name


def test_artifact_name_contains_version_and_os(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    name = artifact_name("1.2.0rc1")
    assert name.startswith("bildfinder-1.2.0rc1-windows-")
