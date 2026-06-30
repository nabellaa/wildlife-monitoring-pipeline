# ==================================================
# Wildlife Monitoring Pipeline
# Script 08 - Backup Manager
# ==================================================

from pathlib import Path
from datetime import datetime
import shutil

from config.paths import (
    BACKUP_PATH,
    DICTIONARY_PATH,
    get_deployment_paths
)

# ==================================================
# Backup Settings
# ==================================================

MAX_BACKUPS = 10

# ==================================================
# Cleanup Old Backups
# ==================================================

def cleanup_old_backups(

    deployment_backup_folder,
    keep=MAX_BACKUPS
    
):

    backups = sorted(
        [
            folder
            for folder in deployment_backup_folder.iterdir()
            if folder.is_dir()
        ],
        key=lambda folder: folder.stat().st_mtime
    )

    while len(backups) > keep:
        shutil.rmtree(
            backups.pop(0)
        )

# ==================================================
# Create Backup
# ==================================================

def create_backup(deployment):

    # Current timestamp
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    # Deployment paths
    paths = get_deployment_paths(deployment)

    # Source folder
    source_folder = paths["processed_folder"]

    # Backup location
    backup_folder = (
        BACKUP_PATH /
        deployment /
        f"backup_{timestamp}" 
        # folder name will become backup_2026-06-29_14-33-02/
    )

    backup_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # Copy processed folder
    shutil.copytree(
        source_folder,
        backup_folder / "processed",
        dirs_exist_ok=True
    )

    # Cleanup old backups
    cleanup_old_backups(
        BACKUP_PATH / deployment
    )

    # Backup information
    info_file = backup_folder / "backup_info.txt"

    with open(info_file, "w") as f:

        f.write("Wildlife Monitoring Pipeline Backup\n")
        f.write(f"Deployment : {deployment}\n")
        f.write(f"Created : {datetime.now()}\n")
        f.write(f"Dataset : {paths['dataset'].name}\n")
        f.write(f"Dictionary : {DICTIONARY_PATH.name}\n")

        if paths["review_log"].exists():

            f.write(f"Review Log : {paths['review_log'].name}\n")

    # Remove old backups
    cleanup_old_backups(
        BACKUP_PATH / deployment
    )

    return backup_folder


# restrore feature in future