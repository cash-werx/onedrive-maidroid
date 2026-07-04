import hashlib
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from config import ROOT

PARTIAL_HASH_BYTES = 65536


def hash_file(file, max_bytes=None):
    hasher = hashlib.sha256()

    with open(file, "rb") as f:

        read = 0

        while chunk := f.read(65536):
            hasher.update(chunk)
            read += len(chunk)

            if max_bytes is not None and read >= max_bytes:
                break

    return hasher.hexdigest()


size_groups = {}

print("Grouping files by size...")

for file in ROOT.rglob("*"):

    if not file.is_file():
        continue

    try:
        size = file.stat().st_size
        size_groups.setdefault(size, []).append(file)

    except Exception:
        pass

hash_errors = []


def safe_hash(file, max_bytes=None):
    try:
        return file, hash_file(file, max_bytes=max_bytes), None
    except Exception as e:
        return file, None, str(e)


# Same-size files are only candidates for duplication. Before paying the
# cost of hashing the full file (expensive for large videos/archives),
# narrow candidates down using a hash of just the first chunk.
candidates = [
    file
    for files in size_groups.values()
    if len(files) > 1
    for file in files
]

print(f"Partial-hashing {len(candidates)} same-size candidate files...")

partial_groups = {}

with ThreadPoolExecutor(max_workers=8) as pool:
    for i, (file, digest, error) in enumerate(
        pool.map(lambda f: safe_hash(f, max_bytes=PARTIAL_HASH_BYTES), candidates),
        start=1
    ):
        if error is not None:
            hash_errors.append({"file": str(file), "error": error})
        else:
            partial_groups.setdefault(digest, []).append(file)

        if i % 500 == 0:
            print(f"  partial-hashed {i}/{len(candidates)}")

full_candidates = [
    file
    for files in partial_groups.values()
    if len(files) > 1
    for file in files
]

print(f"Full-hashing {len(full_candidates)} remaining candidate files...")

duplicates = {}

with ThreadPoolExecutor(max_workers=8) as pool:
    for i, (file, digest, error) in enumerate(
        pool.map(safe_hash, full_candidates),
        start=1
    ):
        if error is not None:
            hash_errors.append({"file": str(file), "error": error})
        else:
            duplicates.setdefault(digest, []).append(file)

        if i % 500 == 0:
            print(f"  full-hashed {i}/{len(full_candidates)}")

if hash_errors:
    pd.DataFrame(hash_errors).to_csv(
        "duplicate_hash_errors.csv",
        index=False
    )
    print(f"Files skipped due to hashing errors: {len(hash_errors)}")

rows = []

for digest, files in duplicates.items():

    if len(files) > 1:
        for file in files:

            rows.append({
                "hash": digest,
                "size_bytes": file.stat().st_size,
                "file": str(file)
            })

df = pd.DataFrame(rows)

df.to_csv(
    "duplicates.csv",
    index=False
)

print(f"Duplicate records exported: {len(df)}")
