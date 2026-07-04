# OneDrive Organization & Reorganization Toolkit

A Python toolkit for auditing, analyzing, and reorganizing a locally synced OneDrive folder on Windows.

## Overview

This project is designed to help build a full inventory of OneDrive contents, map folder structure, analyze file types, identify duplicate files, generate a move plan, and execute controlled reorganization with logging.

Target environment:

- Windows
- Local OneDrive sync folder
- Default root path: `C:\Users\codya\OneDrive`

## Features

- Full inventory export to CSV and Excel
- Tree-style folder map generation
- File extension distribution analysis
- SHA256-based duplicate detection
- Safe move-plan generation before any file operations
- Logged file moves with collision handling

## Project Files

```text
config.py
inventory_onedrive.py
build_folder_map.py
analyze_extensions.py
find_duplicates.py
generate_move_plan.py
execute_move_plan.py
```

Generated outputs:

```text
onedrive_inventory.csv
onedrive_inventory.xlsx
folder_map.txt
extension_summary.csv
duplicates.csv
duplicate_hash_errors.csv
move_plan.csv
move_results.csv
```

## Installation

Install dependencies:

```powershell
pip install pandas openpyxl
```

## Workflow

Run the scripts in this order:

```powershell
python inventory_onedrive.py
python build_folder_map.py
python analyze_extensions.py
python find_duplicates.py
python generate_move_plan.py
```

Review these outputs before moving anything:

- `folder_map.txt`
- `extension_summary.csv`
- `duplicates.csv`
- `move_plan.csv`

When satisfied, do a dry run first to confirm the intended destinations without touching any files:

```powershell
python execute_move_plan.py --dry-run
```

Then execute for real:

```powershell
python execute_move_plan.py
```

Then inspect:

- `move_results.csv`

## Script Details

### `inventory_onedrive.py`

Scans all files and folders under the configured OneDrive root and exports metadata including name, full path, parent folder, extension, folder flag, size, modified time, created time, and any access error. Errors get the same schema as successful rows, so downstream scripts never see ragged columns.

Options: `--root PATH`, `--output BASENAME` (default `onedrive_inventory`).

### `build_folder_map.py`

Creates a simple tree-style text representation of the folder structure beneath the OneDrive root.

Options: `--root PATH`, `--output FILE` (default `folder_map.txt`).

### `analyze_extensions.py`

Reads the generated inventory and summarizes file counts by extension.

Options: `--input FILE` (default `onedrive_inventory.csv`), `--output FILE` (default `extension_summary.csv`), `--top N` (default `50`).

### `find_duplicates.py`

Groups files by size, then narrows candidates with a fast partial hash (first 64KB) before running a full SHA256 on whatever's left — avoids reading entire large files that can be ruled out early. Hashing runs on a thread pool with progress logged periodically. Files that fail to hash are written to `duplicate_hash_errors.csv` instead of being silently dropped.

Options: `--root PATH`, `--output FILE` (default `duplicates.csv`), `--errors-output FILE` (default `duplicate_hash_errors.csv`).

### `generate_move_plan.py`

Builds a proposed move plan based on extension rules without moving any files. Every eligible file gets a plan entry — same-named files from different folders are both included; collision-safe renaming happens at execution time, not here.

Options: `--input FILE` (default `onedrive_inventory.csv`), `--output FILE` (default `move_plan.csv`).

Current default classifications:

| File type | Destination folder |
|-----------|--------------------|
| Images | `Photos` |
| Word documents | `Documents\\Word` |
| Excel files | `Documents\\Excel` |
| PowerPoint files | `Documents\\PowerPoint` |
| PDFs | `Documents\\PDFs` |
| Shortcuts | `Shortcuts` |
| Temporary files | `Temp` |

### `execute_move_plan.py`

Creates destination folders as needed, renames on collision (`name_1.ext`, `name_2.ext`, ...), moves files, and writes a results log.

Options: `--root PATH`, `--plan FILE` (default `move_plan.csv`), `--output FILE` (default `move_results.csv`), `--dry-run` (log intended moves without touching any files).

## Safety Notes

- Always review `move_plan.csv` before running file moves.
- Keep a backup of important files before large-scale reorganization.
- Test on a smaller subset first when possible.
- OneDrive may take time to re-sync after large move operations.
- Monitor OneDrive sync status during execution.

## Customization

The OneDrive root path lives in a single place, `config.py`, defaulting to
`C:\Users\codya\OneDrive`. Override it two ways, without editing code:

```powershell
# Environment variable (applies to every script run)
$env:ONEDRIVE_ROOT = "D:\OneDrive"
python inventory_onedrive.py

# Per-run CLI flag (takes priority over the env var)
python inventory_onedrive.py --root "D:\OneDrive"
```

To change move behavior, edit `DESTINATION_RULES` in `generate_move_plan.py`.

## Suggested `.gitignore`

If you do not want generated reports committed to the repository, add entries like these:

```gitignore
*.csv
*.xlsx
folder_map.txt
```

## License

Use at your own risk. Review all generated plans before making filesystem changes.
