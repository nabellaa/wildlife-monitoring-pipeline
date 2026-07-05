"""
==================================================
Script: script04_run_speciesnet.py

Purpose
    Classify each detected animal image using SpeciesNet.

Input
    outputs/detection/detection_dataset.csv

Output
    outputs/speciesnet/speciesnet_results.json

Next
    Script 05 - Merge SpeciesNet results with the detection dataset.

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
import os
import pandas as pd

from pathlib import Path

# ==================================================
# 2. Settings and Paths
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import get_deployment_paths

COUNTRY_CODE = "MYS"

deployment = sys.argv[1]
paths = get_deployment_paths(deployment)
INPUT_FILE = paths["detection_csv"]
OUTPUT_DIR = paths["speciesnet_folder"]
OUTPUT_FILE = paths["speciesnet_json"]

# ==================================================
# SAFE CHECK: file exists
# ==================================================
if not os.path.exists(INPUT_FILE):
    print("No detection file found. Skipping SpeciesNet.")
    sys.exit(0)

# ==================================================
# SAFE LOAD CSV
# ==================================================
try:
    df = pd.read_csv(INPUT_FILE)
except pd.errors.EmptyDataError:
    print("Detection file is empty. Skipping SpeciesNet.")
    sys.exit(0)

if df.empty or "image_path" not in df.columns:
    print("Detection dataset is empty. Skipping SpeciesNet.")
    sys.exit(0)

# ==================================================
# Extract images
# ==================================================
image_paths = df["image_path"].dropna().tolist()

if len(image_paths) == 0:
    print("No animals to classify. Skipping SpeciesNet.")
    sys.exit(0)

# ==================================================
# Write file list
# ==================================================
IMAGE_LIST_FILE = OUTPUT_DIR / "image_paths.txt"

with open(IMAGE_LIST_FILE, "w", encoding="utf-8") as f:
    for image_path in image_paths:
        f.write(f"{image_path}\n")

print(f"Running SpeciesNet on {len(image_paths)} images")

# ==================================================
# Build the SpeciesNet command
# ==================================================

command = [
    sys.executable,
    "-m",
    "speciesnet.scripts.run_model",

    "--filepaths_txt",
    str(IMAGE_LIST_FILE),

    "--predictions_json",
    str(OUTPUT_FILE),

    "--country",
    COUNTRY_CODE
]

# ==================================================
# Run SpeciesNet
# ==================================================

print("\nRunning SpeciesNet...")
print("First run may download the model (~1 GB).\n")

subprocess.run(
    command,
    check=True
)

# ==================================================
# 8. Load the JSON results from SpeciesNet
# ==================================================

with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    speciesnet_results = json.load(f)

# ==================================================
# 9. Display summary of results 
# ==================================================

print("\n" + "=" * 40)
print("SpeciesNet Complete")
print("=" * 40)

print(f"Images Classified : {len(image_paths)}")
print(f"Results Saved     : {OUTPUT_FILE}")
