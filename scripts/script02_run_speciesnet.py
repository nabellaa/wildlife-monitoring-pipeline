"""
==================================================
Script: script02_run_speciesnet.py

Purpose
    Classify each detected animal image using SpeciesNet.

Input
    outputs/deployments/<deployment>/megadetector/
    megadetector_results.json

Output
    outputs/deployments/<deployment>/speciesnet/
    speciesnet_results.json

Next
    Script 03 - Build Wildlife Dataset

Author:
    Bella

Project:
    Wildlife Monitoring Pipeline

==================================================
"""

# ==================================================
# 1. Import Libraries
# ==================================================

import json
import subprocess
import sys

from pathlib import Path

# ==================================================
# 2. Settings and Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import get_deployment_paths

COUNTRY_CODE   = "MYS"
CONF_THRESHOLD = 0.30

deployment  = sys.argv[1]
paths       = get_deployment_paths(deployment, create_folders=True)
INPUT_FILE  = paths["megadetector_json"]
OUTPUT_DIR  = paths["speciesnet_folder"]
OUTPUT_FILE = paths["speciesnet_json"]

# ==================================================
# 3. Safe Check
# ==================================================

if not INPUT_FILE.exists():
    print("No MegaDetector results found. Skipping SpeciesNet.")
    sys.exit(0)

# ==================================================
# 4. Load MegaDetector Results
# ==================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    megadetector_results = json.load(f)

# ==================================================
# 5. Extract Image Paths Above Confidence Threshold
# ==================================================

image_paths = [
    r["file"]
    for r in megadetector_results
    if any(
        d["conf"] >= CONF_THRESHOLD
        for d in r["detections"]
    )
]

if not image_paths:
    print("No animals detected above threshold. Skipping SpeciesNet.")
    sys.exit(0)

print(f"Running SpeciesNet on {len(image_paths)} images")

# ==================================================
# 6. Write Image List File
# ==================================================

IMAGE_LIST_FILE = OUTPUT_DIR / "image_paths.txt"

with open(IMAGE_LIST_FILE, "w", encoding="utf-8") as f:
    for image_path in image_paths:
        f.write(f"{image_path}\n")

# ==================================================
# 7. Run SpeciesNet
# ==================================================

print("\nRunning SpeciesNet...")
print("First run may download the model (~1 GB).\n")

command = [
    sys.executable,
    "-m",
    "speciesnet.scripts.run_model",
    "--filepaths_txt",   str(IMAGE_LIST_FILE),
    "--predictions_json", str(OUTPUT_FILE),
    "--country",          COUNTRY_CODE
]

subprocess.run(command, check=True)

# ==================================================
# 8. Summary
# ==================================================

with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    speciesnet_results = json.load(f)

print("\n" + "=" * 40)
print("SpeciesNet Complete")
print("=" * 40)
print(f"Images Classified : {len(image_paths)}")
print(f"Results Saved     : {OUTPUT_FILE}")