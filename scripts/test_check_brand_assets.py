import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_brand_assets as cba  # noqa: E402

CLEAN_SVG = '<svg xmlns="http://www.w3.org/2000/svg" font-family="x"><path d="M0 0"/></svg>'


def write(root: Path, rel: str, content: str | bytes) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)
    return path


def write_manifest(root: Path, *srcs: str) -> None:
    icons = [{"src": src, "sizes": "192x192", "type": "image/png"} for src in srcs]
    write(root, "favicon/site.webmanifest", json.dumps({"name": "Xberg", "icons": icons}))


def git(root: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.com",
            "-c",
            "tag.gpgSign=false",
            "-c",
            "commit.gpgSign=false",
            *args,
        ],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_clean_svg_has_no_violations(tmp_path: Path) -> None:
    write(tmp_path, "logo/a.svg", CLEAN_SVG)
    assert cba.svg_violations(tmp_path) == []


def test_svg_with_script_element_is_rejected(tmp_path: Path) -> None:
    write(tmp_path, "logo/a.svg", "<svg><SCRIPT>alert(1)</SCRIPT></svg>")
    assert cba.svg_violations(tmp_path) == ["logo/a.svg: contains a <script> element"]


def test_svg_with_event_attribute_is_rejected(tmp_path: Path) -> None:
    write(tmp_path, "docs/b.svg", '<svg><rect\n  onLoad = "x()"/></svg>')
    assert cba.svg_violations(tmp_path) == ["docs/b.svg: contains an on* event attribute (onLoad)"]


def test_svg_with_slash_separated_event_attribute_is_rejected(tmp_path: Path) -> None:
    write(tmp_path, "logo/c.svg", '<svg/onload="x()"/>')
    assert cba.svg_violations(tmp_path) == ["logo/c.svg: contains an on* event attribute (onload)"]


def test_svg_scan_requires_at_least_one_svg(tmp_path: Path) -> None:
    with pytest.raises(cba.CheckError, match="no SVG files"):
        cba.svg_violations(tmp_path)


def test_manifest_with_existing_icons_passes(tmp_path: Path) -> None:
    write(tmp_path, "favicon/icon-192.png", b"\x89PNG")
    write_manifest(tmp_path, "icon-192.png")
    assert cba.manifest_violations(tmp_path) == []


def test_manifest_with_missing_icon_is_rejected(tmp_path: Path) -> None:
    write(tmp_path, "favicon/icon-192.png", b"\x89PNG")
    write_manifest(tmp_path, "icon-192.png", "icon-512.png")
    assert cba.manifest_violations(tmp_path) == ["favicon/site.webmanifest: icon icon-512.png does not exist"]


def test_manifest_without_icons_is_rejected(tmp_path: Path) -> None:
    write_manifest(tmp_path)
    assert cba.manifest_violations(tmp_path) == ["favicon/site.webmanifest: lists no icons"]


def test_brand_files_changed_since_tag_are_listed(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    write(tmp_path, "social/card.png", b"old")
    write(tmp_path, "README.md", "old")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "init")
    git(tmp_path, "tag", "v1")
    write(tmp_path, "social/card.png", b"new")
    write(tmp_path, "README.md", "new")
    git(tmp_path, "commit", "-qam", "change")
    assert cba.untagged_changes(tmp_path, "v1") == ["social/card.png"]


def test_untagged_changes_reports_a_missing_tag(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    write(tmp_path, "README.md", "x")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "init")
    with pytest.raises(cba.CheckError, match="tag v1"):
        cba.untagged_changes(tmp_path, "v1")


def test_main_fails_on_errors_and_only_warns_on_untagged_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    git(tmp_path, "init", "-q")
    write(tmp_path, "favicon/icon-192.png", b"\x89PNG")
    write_manifest(tmp_path, "icon-192.png")
    write(tmp_path, "logo/a.svg", CLEAN_SVG)
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "init")
    git(tmp_path, "tag", "v1")
    write(tmp_path, "logo/a.svg", CLEAN_SVG.replace("M0 0", "M1 1"))
    git(tmp_path, "commit", "-qam", "change")

    assert cba.main(["--root", str(tmp_path)]) == 0
    assert "::warning::logo/a.svg differs from tag v1" in capsys.readouterr().out

    write(tmp_path, "logo/a.svg", '<svg onclick="x()"/>')
    assert cba.main(["--root", str(tmp_path)]) == 1
    assert "::error::logo/a.svg: contains an on* event attribute (onclick)" in capsys.readouterr().out
