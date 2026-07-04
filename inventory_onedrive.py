"""Build a full inventory of files and folders under the OneDrive root."""
from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import get_root

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

COLUMNS = [
    "name", "full_path", "parent_folder", "extension",
    "is_folder", "size_bytes", "modified", "created", "error",
]


def scan(root: Path) -> list[dict]:
    """Walk every entry under root, returning one record per file/folder.

    Entries that raise on stat() (permission errors, broken symlinks,
    OneDrive placeholder issues) still get a record with the error
    captured, using the same schema as successful entries, so
    downstream scripts never see ragged columns.
    """
    records = []

    for item in root.rglob("*"):
        try:
            stat = item.stat()
            records.append({
                "name": item.name,
                "full_path": str(item),
                "parent_folder": str(item.parent),
                "extension": item.suffix.lower(),
                "is_folder": item.is_dir(),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "error": "",
            })
        except OSError as e:
            records.append({
                "name": item.name,
                "full_path": str(item),
                "parent_folder": str(item.parent),
                "extension": "",
                "is_folder": False,
                "size_bytes": 0,
                "modified": None,
                "created": None,
                "error": str(e),
            })

        if len(records) % 5000 == 0:
            log.info("Scanned %d items...", len(records))

    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="OneDrive root path (overrides ONEDRIVE_ROOT env var)")
    parser.add_argument("--output", default="onedrive_inventory", help="Output file basename, no extension")
    args = parser.parse_args()

    root = get_root(args.root)
    if not root.exists():
        raise SystemExit(f"Root path does not exist: {root}")

    log.info("Scanning %s ...", root)
    records = scan(root)

    df = pd.DataFrame(records, columns=COLUMNS)
    df.to_csv(f"{args.output}.csv", index=False)
    df.to_excel(f"{args.output}.xlsx", index=False)

    errors = int((df["error"] != "").sum())
    log.info("Inventory complete. Items found: %d (errors: %d)", len(df), errors)


if __name__ == "__main__":
    main()
