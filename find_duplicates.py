"""Detect duplicate files under the OneDrive root using a two-stage hash.

Files are first grouped by size, then narrowed further by hashing just
the first 64KB, and only genuinely remaining candidates get a full
SHA256 hash. This avoids reading whole large files (video, archives)
that can be ruled out from a small prefix.
"""
from __future__ import annotations

import argparse
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import pandas as pd

from config import get_root

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

CHUNK_SIZE = 65536
PARTIAL_HASH_BYTES = 65536
MAX_WORKERS = 8


def hash_file(path: Path, max_bytes: Optional[int] = None) -> str:
    hasher = hashlib.sha256()
    read = 0

    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
            read += len(chunk)
            if max_bytes is not None and read >= max_bytes:
                break

    return hasher.hexdigest()


def safe_hash(path: Path, max_bytes: Optional[int] = None):
    try:
        return path, hash_file(path, max_bytes=max_bytes), None
    except OSError as e:
        return path, None, str(e)


def group_by_size(root: Path) -> dict[int, list[Path]]:
    groups: dict[int, list[Path]] = {}

    for file in root.rglob("*"):
        if not file.is_file():
            continue
        try:
            groups.setdefault(file.stat().st_size, []).append(file)
        except OSError:
            continue

    return groups


def narrow_candidates(
    candidates: list[Path],
    max_bytes: Optional[int],
    label: str,
    errors: list[dict],
) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = pool.map(lambda p: safe_hash(p, max_bytes=max_bytes), candidates)

        for i, (path, digest, error) in enumerate(results, start=1):
            if error is not None:
                errors.append({"file": str(path), "error": error})
            else:
                groups.setdefault(digest, []).append(path)

            if i % 500 == 0:
                log.info("%s: %d/%d", label, i, len(candidates))

    return groups


def find_duplicates(root: Path) -> tuple[pd.DataFrame, list[dict]]:
    errors: list[dict] = []

    size_groups = group_by_size(root)
    candidates = [f for files in size_groups.values() if len(files) > 1 for f in files]
    log.info("Partial-hashing %d same-size candidate files...", len(candidates))

    partial_groups = narrow_candidates(candidates, PARTIAL_HASH_BYTES, "partial-hashed", errors)

    full_candidates = [f for files in partial_groups.values() if len(files) > 1 for f in files]
    log.info("Full-hashing %d remaining candidate files...", len(full_candidates))

    full_groups = narrow_candidates(full_candidates, None, "full-hashed", errors)

    rows = [
        {"hash": digest, "size_bytes": f.stat().st_size, "file": str(f)}
        for digest, files in full_groups.items()
        if len(files) > 1
        for f in files
    ]

    return pd.DataFrame(rows), errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="OneDrive root path (overrides ONEDRIVE_ROOT env var)")
    parser.add_argument("--output", default="duplicates.csv")
    parser.add_argument("--errors-output", default="duplicate_hash_errors.csv")
    args = parser.parse_args()

    root = get_root(args.root)
    if not root.exists():
        raise SystemExit(f"Root path does not exist: {root}")

    df, errors = find_duplicates(root)
    df.to_csv(args.output, index=False)

    if errors:
        pd.DataFrame(errors).to_csv(args.errors_output, index=False)
        log.info("Files skipped due to hashing errors: %d", len(errors))

    log.info("Duplicate records exported: %d", len(df))


if __name__ == "__main__":
    main()
