import pandas as pd

df = pd.read_csv(
    "onedrive_inventory.csv"
)

moves = []

for _, row in df.iterrows():

    if bool(row["is_folder"]):
        continue

    filename = str(row["name"])
    filename_lower = filename.lower()

    ext = str(
        row["extension"]
    ).lower()

    destination = None

    if ext in [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
        ".heic",
        ".tif",
        ".tiff"
    ]:
        destination = r"Photos"

    elif ext in [
        ".doc",
        ".docx"
    ]:
        destination = r"Documents\Word"

    elif ext in [
        ".xls",
        ".xlsx",
        ".xlsm"
    ]:
        destination = r"Documents\Excel"

    elif ext in [
        ".ppt",
        ".pptx"
    ]:
        destination = r"Documents\PowerPoint"

    elif ext == ".pdf":
        destination = r"Documents\PDFs"

    elif ext == ".lnk":
        destination = r"Shortcuts"

    elif (
        ext == ".tmp"
        or filename_lower.endswith(".driveupload")
        or filename_lower.endswith(".drivedownload")
    ):
        destination = r"Temp"

    if destination is None:
        continue

    moves.append({
        "current_path":
            row["full_path"],
        "filename":
            filename,
        "destination_folder":
            destination
    })

plan = pd.DataFrame(moves)

plan.to_csv(
    "move_plan.csv",
    index=False
)

print(
    f"Planned moves: {len(plan)}"
)
