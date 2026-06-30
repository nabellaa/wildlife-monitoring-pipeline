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

DATA_PATH = PROJECT_ROOT / "data"
SAMPLE_PATH = DATA_PATH / "sample"
OUTPUT_PATH = PROJECT_ROOT / "outputs"
REFERENCE_PATH = PROJECT_ROOT / "reference"
BACKUP_PATH = PROJECT_ROOT / "backup"

# ==================================================
# Output Folders
# ==================================================

AUDIT_OUTPUT = OUTPUT_PATH / "audit"
MEGADETECTOR_OUTPUT = OUTPUT_PATH / "megadetector"
DETECTION_OUTPUT = OUTPUT_PATH / "detection"
SPECIESNET_OUTPUT = OUTPUT_PATH / "speciesnet"
PROCESSED_OUTPUT = OUTPUT_PATH / "processed"


# ==================================================
# Master Output
# ==================================================
# for create a master dataset
MASTER_OUTPUT = OUTPUT_PATH / "master"

MASTER_OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

MASTER_DATASET = (
    MASTER_OUTPUT /
    "wildlife_dataset_master.csv"
)

CLEAN_DATASET = (
    MASTER_OUTPUT /
    "wildlife_clean_dataset.csv"
)

DEPLOYMENT_SUMMARY = (
    MASTER_OUTPUT /
    "deployment_summary.csv"
)

# ==================================================
# Main Files
# ==================================================

AUDIT_REPORT = AUDIT_OUTPUT / "audit_report.txt"

MEGADETECTOR_JSON = (
MEGADETECTOR_OUTPUT /
"megadetector_results.json"
)

DETECTION_DATASET = (
DETECTION_OUTPUT /
"detection_dataset.csv"
)

SPECIESNET_JSON = (
SPECIESNET_OUTPUT /
"speciesnet_results.json"
)

DATASET_PATH = (
    PROCESSED_OUTPUT /
    "wildlife_dataset.csv"
)

DICTIONARY_PATH = (
    REFERENCE_PATH /
    "species_dictionary.csv"
)

REVIEW_LOG_PATH = (
    PROCESSED_OUTPUT /
    "review_log.csv"
)

# ==================================================
# Deployment Output Paths
# ==================================================

def get_deployment_paths(deployment):
    """
    Build every output path for one deployment.
    """

    deployment_root = OUTPUT_PATH / deployment

    audit = deployment_root / "audit"
    megadetector = deployment_root / "megadetector"
    detection = deployment_root / "detection"
    speciesnet = deployment_root / "speciesnet"
    processed = deployment_root / "processed"

    # Create folders automatically
    for folder in (
        audit,
        megadetector,
        detection,
        speciesnet,
        processed
    ):
        folder.mkdir(
            parents=True,
            exist_ok=True
        )

    return {

        "deployment_root": deployment_root,

        "audit_folder":        audit,
        "megadetector_folder": megadetector,
        "detection_folder":    detection,
        "speciesnet_folder":   speciesnet,
        "processed_folder":    processed,

        "audit_report":      audit / "audit_report.txt",
        "megadetector_json": megadetector / "megadetector_results.json",
        "detection_csv":     detection / "detection_dataset.csv",
        "speciesnet_json":   speciesnet / "speciesnet_results.json",
        "dataset":           processed / "wildlife_dataset.csv",
        "review_log":        processed / "review_log.csv"

    }