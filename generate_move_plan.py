"""Generate a proposed file move plan by extension, without moving anything."""
from __future__ import annotations

import argparse
import logging
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# Each rule maps a set of extensions to a destination folder, checked in
# order. To change move behavior, edit this table.
DESTINATION_RULES: list[tuple[set[str], str]] = [
    ({".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".tif", ".tiff"}, "Photos"),
    ({".doc", ".docx"}, r"Documents\Word"),
    ({".xls", ".xlsx", ".xlsm"}, r"Documents\Excel"),
    ({".ppt", ".pptx"}, r"Documents\PowerPoint"),
    ({".pdf"}, r"Documents\PDFs"),
    ({".lnk"}, "Shortcuts"),
]

TEMP_SUFFIXES = (".driveupload", ".drivedownload")


def classify(filename: str, extension: str) -> Optional[str]:
    ext = extension.lower()
    name_lower = filename.lower()

    for extensions, destination in DESTINATION_RULES:
        if ext in extensions:
            return destination

    if ext == ".tmp" or name_lower.endswith(TEMP_SUFFIXES):
        return "Temp"

    return None


def build_plan(inventory_csv: str) -> pd.DataFrame:
    df = pd.read_csv(inventory_csv)
    files = df[df["is_folder"] == False]  # noqa: E712

    moves = []
    for _, row in files.iterrows():
        filename = str(row["name"])
        extension = str(row["extension"]) if pd.notna(row["extension"]) else ""

        destination = classify(filename, extension)
        if destination is None:
            continue

        moves.append({
            "current_path": row["full_path"],
            "filename": filename,
            "destination_folder": destination,
        })

    return pd.DataFrame(moves, columns=["current_path", "filename", "destination_folder"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="onedrive_inventory.csv", help="Inventory CSV to read")
    parser.add_argument("--output", default="move_plan.csv", help="Move plan CSV to write")
    args = parser.parse_args()

    plan = build_plan(args.input)
    plan.to_csv(args.output, index=False)

    log.info("Planned moves: %d", len(plan))


if __name__ == "__main__":
    main()
