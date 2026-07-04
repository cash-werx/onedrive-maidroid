"""Execute a previously generated move plan, with collision-safe renaming."""
from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

import pandas as pd

from config import get_root

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def resolve_destination(dst_folder: Path, name: str) -> Path:
    """Pick a non-colliding destination path, appending _1, _2, ... as needed."""
    dst = dst_folder / name
    stem, suffix = Path(name).stem, Path(name).suffix
    counter = 1

    while dst.exists():
        dst = dst_folder / f"{stem}_{counter}{suffix}"
        counter += 1

    return dst


def execute(plan: pd.DataFrame, root: Path, dry_run: bool) -> list[dict]:
    log_entries = []

    for _, row in plan.iterrows():
        src = Path(row["current_path"])

        if not src.exists():
            log_entries.append({"source": str(src), "destination": "", "status": "Missing"})
            continue

        dst_folder = root / row["destination_folder"]
        dst = resolve_destination(dst_folder, src.name)

        if dry_run:
            log_entries.append({"source": str(src), "destination": str(dst), "status": "DryRun"})
            continue

        try:
            dst_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            log_entries.append({"source": str(src), "destination": str(dst), "status": "Moved"})
        except OSError as e:
            log_entries.append({"source": str(src), "destination": str(dst), "status": f"Error: {e}"})

    return log_entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="OneDrive root path (overrides ONEDRIVE_ROOT env var)")
    parser.add_argument("--plan", default="move_plan.csv", help="Move plan CSV to read")
    parser.add_argument("--output", default="move_results.csv", help="Results log CSV to write")
    parser.add_argument("--dry-run", action="store_true", help="Log intended moves without touching files")
    args = parser.parse_args()

    root = get_root(args.root)
    plan = pd.read_csv(args.plan)

    log_entries = execute(plan, root, args.dry_run)
    pd.DataFrame(log_entries).to_csv(args.output, index=False)

    moved = sum(1 for e in log_entries if e["status"] == "Moved")
    log.info("Move process complete. Log entries: %d, moved: %d", len(log_entries), moved)


if __name__ == "__main__":
    main()
