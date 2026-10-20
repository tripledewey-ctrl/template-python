from __future__ import annotations

from pathlib import Path

import pytest

from bildfinder.scanner import default_search_dir, find_images, format_size, is_image


@pytest.mark.parametrize(
    ("name", "expected"),
    [("a.png", True), ("b.JPEG", True), ("c.WebP", True), ("d.txt", False), ("png", False)],
)
def test_is_image(name: str, expected: bool) -> None:
    assert is_image(Path(name)) is expected


def test_find_images_recursive(picture_tree: Path) -> None:
    names = [img.name for img in find_images(picture_tree)]
    assert names == ["icon.webp", "logo.png", "strand.JPG"]


def test_find_images_reports_size(picture_tree: Path) -> None:
    sizes = {img.name: img.size for img in find_images(picture_tree)}
    assert sizes["strand.JPG"] == 2048


def test_find_images_flat(picture_tree: Path) -> None:
    names = [img.name for img in find_images(picture_tree, recursive=False)]
    assert names == ["icon.webp", "logo.png"]


def test_find_images_hidden(picture_tree: Path) -> None:
    names = {img.name for img in find_images(picture_tree, include_hidden=True)}
    assert {"geheim.png", ".thumb.jpg"} <= names


def test_find_images_limit(picture_tree: Path) -> None:
    assert len(find_images(picture_tree, limit=2)) == 2


def test_find_images_invalid_limit(picture_tree: Path) -> None:
    with pytest.raises(ValueError, match="limit"):
        find_images(picture_tree, limit=0)


def test_find_images_not_a_dir(tmp_path: Path) -> None:
    with pytest.raises(NotADirectoryError):
        find_images(tmp_path / "gibtsnicht")


def test_find_images_skips_vanished_file(
    picture_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_stat = Path.stat

    def flaky_stat(self: Path, **kwargs: bool) -> object:
        if self.name == "logo.png":
            raise PermissionError("kein Zugriff")
        return original_stat(self, **kwargs)

    monkeypatch.setattr(Path, "stat", flaky_stat)
    assert "logo.png" not in [img.name for img in find_images(picture_tree)]


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (0, "0 B"),
        (1023, "1023 B"),
        (1536, "1.5 KB"),
        (5 * 1024**2, "5.0 MB"),
        (3 * 1024**4, "3072.0 GB"),
    ],
)
def test_format_size(size: int, expected: str) -> None:
    assert format_size(size) == expected


def test_format_size_negative() -> None:
    with pytest.raises(ValueError):
        format_size(-1)


def test_default_search_dir_prefers_pictures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert default_search_dir() == tmp_path
    (tmp_path / "Bilder").mkdir()
    assert default_search_dir() == tmp_path / "Bilder"
