import pandas as pd

df = pd.read_csv(
    "onedrive_inventory.csv"
)

files = df[
    df["is_folder"] == False
]

summary = (
    files
    .groupby("extension")
    .size()
    .sort_values(
        ascending=False
    )
)

summary.to_csv(
    "extension_summary.csv"
)

print(summary.head(50))
