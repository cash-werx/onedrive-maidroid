import hashlib
import pandas as pd

from config import ROOT

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

duplicates = {}
hash_errors = []

print("Hashing candidate duplicate files...")

for size, files in size_groups.items():

    if len(files) < 2:
        continue

    for file in files:

        try:

            hasher = hashlib.sha256()

            with open(file, "rb") as f:

                while chunk := f.read(65536):
                    hasher.update(chunk)

            digest = hasher.hexdigest()

            duplicates.setdefault(
                digest,
                []
            ).append(file)

        except Exception as e:
            hash_errors.append({
                "file": str(file),
                "error": str(e)
            })

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
