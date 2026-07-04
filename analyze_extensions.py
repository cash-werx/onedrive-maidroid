"""Summarize file counts by extension from the generated inventory CSV."""
from __future__ import annotations

import argparse
import logging

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def summarize(inventory_csv: str) -> pd.Series:
    df = pd.read_csv(inventory_csv)
    files = df[df["is_folder"] == False]  # noqa: E712

    extensions = files["extension"].fillna("").astype(str)
    extensions = extensions.replace("", "(no extension)")

    return extensions.value_counts()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="onedrive_inventory.csv", help="Inventory CSV to read")
    parser.add_argument("--output", default="extension_summary.csv", help="Summary CSV to write")
    parser.add_argument("--top", type=int, default=50, help="Number of top extensions to print")
    args = parser.parse_args()

    summary = summarize(args.input)
    summary.to_csv(args.output, header=["count"])

    log.info("Top %d extensions by file count:", args.top)
    print(summary.head(args.top))


if __name__ == "__main__":
    main()
