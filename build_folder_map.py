"""Create a tree-style text map of folders under the OneDrive root."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from config import get_root

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def build_map(root: Path) -> list[str]:
    folders = sorted(
        (p for p in root.rglob("*") if p.is_dir()),
        key=lambda p: str(p).lower(),
    )

    lines = []
    for folder in folders:
        depth = len(folder.relative_to(root).parts)
        lines.append(f"{'    ' * depth}{folder.name}")

    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="OneDrive root path (overrides ONEDRIVE_ROOT env var)")
    parser.add_argument("--output", default="folder_map.txt", help="Output file path")
    args = parser.parse_args()

    root = get_root(args.root)
    if not root.exists():
        raise SystemExit(f"Root path does not exist: {root}")

    lines = build_map(root)
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")

    log.info("Folder map created: %s (%d folders)", args.output, len(lines))


if __name__ == "__main__":
    main()
