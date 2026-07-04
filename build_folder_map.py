from pathlib import Path

ROOT = Path(r"C:\Users\codya\OneDrive")

with open(
    "folder_map.txt",
    "w",
    encoding="utf-8"
) as f:

    for folder in sorted(
        [p for p in ROOT.rglob("*") if p.is_dir()]
    ):

        relative = folder.relative_to(ROOT)

        depth = len(relative.parts)

        indent = "    " * depth

        f.write(
            f"{indent}{folder.name}\n"
        )

print("Folder map created")
