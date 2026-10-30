"""Check the served brand assets: script-free SVGs, a resolvable web manifest, and tag drift."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BRAND_DIRS = ("banner", "logo", "favicon", "social", "docs")
MANIFEST = "favicon/site.webmanifest"
SCRIPT_RE = re.compile(r"<script\b", re.IGNORECASE)
EVENT_ATTR_RE = re.compile(r"[\s/](on[a-z]+)\s*=", re.IGNORECASE)


class CheckError(Exception):
    """The check could not examine what it exists to examine."""


def svg_files(root: Path) -> list[Path]:
    svgs = sorted(p for d in BRAND_DIRS for p in (root / d).rglob("*.svg"))
    if not svgs:
        raise CheckError(f"no SVG files under {', '.join(BRAND_DIRS)} in {root}")
    return svgs


def svg_violations(root: Path) -> list[str]:
    violations = []
    for svg in svg_files(root):
        rel = svg.relative_to(root).as_posix()
        text = svg.read_text(encoding="utf-8")
        if SCRIPT_RE.search(text):
            violations.append(f"{rel}: contains a <script> element")
        violations.extend(
            f"{rel}: contains an on* event attribute ({match.group(1)})" for match in EVENT_ATTR_RE.finditer(text)
        )
    return violations


def manifest_violations(root: Path) -> list[str]:
    manifest = root / MANIFEST
    icons = json.loads(manifest.read_text(encoding="utf-8")).get("icons", [])
    if not icons:
        return [f"{MANIFEST}: lists no icons"]
    return [
        f"{MANIFEST}: icon {icon['src']} does not exist"
        for icon in icons
        if not (manifest.parent / icon["src"]).is_file()
    ]


def untagged_changes(root: Path, tag: str) -> list[str]:
    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)

    if run("rev-parse", "--verify", "--quiet", f"refs/tags/{tag}").returncode != 0:
        raise CheckError(f"tag {tag} is not present; fetch tags to compare against it")
    diff = run("diff", "--name-only", f"refs/tags/{tag}", "HEAD", "--", *BRAND_DIRS)
    if diff.returncode != 0:
        raise CheckError(f"git diff against {tag} failed: {diff.stderr.strip()}")
    return diff.stdout.split()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--tag", default="v1", help="floating tag consumers pin (default: v1)")
    args = parser.parse_args(argv)

    errors = svg_violations(args.root) + manifest_violations(args.root)
    for error in errors:
        sys.stdout.write(f"::error::{error}\n")
    try:
        drift = untagged_changes(args.root, args.tag)
    except CheckError as exc:
        drift = []
        sys.stdout.write(f"::warning::{exc}\n")
    for path in drift:
        sys.stdout.write(f"::warning::{path} differs from tag {args.tag}; @{args.tag} consumers do not see it\n")
    checked = f"checked {len(svg_files(args.root))} SVG file(s) and {MANIFEST}"
    sys.stdout.write(f"{checked}: {len(errors)} error(s), {len(drift)} file(s) not yet under tag {args.tag}\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
