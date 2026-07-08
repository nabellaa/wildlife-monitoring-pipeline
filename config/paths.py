# gives you one place to change paths if you ever move folders or support multiple datasets.

# ==================================================
# Path Configuration
# ==================================================

from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# __file__ = current Python script
# .resolve() = full absolute path
# .parent.parent = move up two folders to project root

# Build the path without hardcoding
# C:\Users\Bella\...
# Makes the project portable.

# ==================================================
# Main Folders
# ==================================================

DATA_PATH         = PROJECT_ROOT / "data"
SAMPLE_PATH       = DATA_PATH / "sample"
BATCH_SAMPLE_PATH = DATA_PATH / "batch_sample"
OUTPUT_PATH       = PROJECT_ROOT / "outputs"
REFERENCE_PATH    = PROJECT_ROOT / "reference"
BACKUP_PATH       = PROJECT_ROOT / "backup"

# ==================================================
# Output Folders
# ==================================================

DEPLOYMENTS_OUTPUT = OUTPUT_PATH / "deployments"
MASTER_OUTPUT      = OUTPUT_PATH / "master"
LOGS_OUTPUT        = OUTPUT_PATH / "logs"

DEPLOYMENTS_OUTPUT.mkdir(parents=True, exist_ok=True)
MASTER_OUTPUT.mkdir(parents=True, exist_ok=True)
LOGS_OUTPUT.mkdir(parents=True, exist_ok=True)

# ==================================================
# Master Files
# ==================================================

MASTER_DATASET     = MASTER_OUTPUT / "wildlife_dataset_master.csv"
CLEAN_DATASET      = MASTER_OUTPUT / "wildlife_clean_dataset.csv"
DEPLOYMENT_SUMMARY = MASTER_OUTPUT / "deployment_summary.csv"

# ==================================================
# Reference Files
# ==================================================

DICTIONARY_PATH = REFERENCE_PATH / "species_dictionary.csv"

# ==================================================
# Deployment Output Paths
# ==================================================

def get_deployment_paths(deployment,create_folders=False):
    """
    Build every output path for one deployment.
    """
    # INPUT (sample/batch sample /RAW DATA)
    input_root = BATCH_SAMPLE_PATH / deployment

    # OUTPUT (PROCESSED DATA)
    deployment_root = DEPLOYMENTS_OUTPUT  / deployment

    audit        = deployment_root / "audit"
    megadetector = deployment_root / "megadetector"
    detection    = deployment_root / "detection"
    speciesnet   = deployment_root / "speciesnet"
    processed    = deployment_root / "processed"

    # Only create folders when running pipeline
    if create_folders:
        for folder in (
            audit,
            megadetector,
            detection,
            speciesnet,
            processed
        ):
            folder.mkdir(parents=True, exist_ok=True)

    return {
        
        # INPUT
        "input_folder": input_root,

        # OUTPUT ROOT
        "deployment_root": deployment_root,

        # OUTPUT SUBFOLDERS
        "audit_folder":        audit,
        "megadetector_folder": megadetector,
        "detection_folder":    detection,
        "speciesnet_folder":   speciesnet,
        "processed_folder":    processed,

        # OUTPUT FILES
        "audit_report":      audit        / "audit_report.txt",
        "megadetector_json": megadetector / "megadetector_results.json",
        "detection_csv":     detection    / "detection_dataset.csv",
        "speciesnet_json":   speciesnet   / "speciesnet_results.json",
        "dataset":           processed    / "wildlife_dataset.csv",
        "review_log":        processed    / "review_log.csv"

    }