from pathlib import Path
import pandas as pd
from datetime import datetime

ROOT = Path(r"C:\Users\codya\OneDrive")

inventory = []

for item in ROOT.rglob("*"):

    try:

        stat = item.stat()

        inventory.append({
            "name": item.name,
            "full_path": str(item),
            "parent_folder": str(item.parent),
            "extension": item.suffix.lower(),
            "is_folder": item.is_dir(),
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(
                stat.st_mtime
            ),
            "created": datetime.fromtimestamp(
                stat.st_ctime
            )
        })

    except Exception as e:

        inventory.append({
            "name": item.name,
            "full_path": str(item),
            "error": str(e)
        })

df = pd.DataFrame(inventory)

df.to_csv(
    "onedrive_inventory.csv",
    index=False
)

df.to_excel(
    "onedrive_inventory.xlsx",
    index=False
)

print(f"Inventory complete")
print(f"Items found: {len(df)}")
