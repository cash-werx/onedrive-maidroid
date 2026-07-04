import pandas as pd
from pathlib import Path
import shutil

from config import ROOT

plan = pd.read_csv(
    "move_plan.csv"
)

log = []

for _, row in plan.iterrows():

    src = Path(
        row["current_path"]
    )

    if not src.exists():

        log.append({
            "source": str(src),
            "destination": "",
            "status": "Missing"
        })

        continue

    dst_folder = (
        ROOT /
        row["destination_folder"]
    )

    dst_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    dst = (
        dst_folder /
        src.name
    )

    counter = 1

    while dst.exists():

        dst = (
            dst_folder /
            f"{src.stem}_{counter}{src.suffix}"
        )

        counter += 1

    try:

        shutil.move(
            str(src),
            str(dst)
        )

        log.append({
            "source": str(src),
            "destination": str(dst),
            "status": "Moved"
        })

    except Exception as e:

        log.append({
            "source": str(src),
            "destination": str(dst),
            "status": f"Error: {e}"
        })

pd.DataFrame(log).to_csv(
    "move_results.csv",
    index=False
)

print("Move process complete")
print(
    f"Log entries: {len(log)}"
)
