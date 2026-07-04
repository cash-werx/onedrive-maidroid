from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(r"C:\Users\codya\OneDrive")

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

        except Exception:
            pass

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
