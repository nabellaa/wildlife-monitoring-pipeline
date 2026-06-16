"""
==================================================
Script: 04_run_speciesnet.py

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

import pandas as pd

from pathlib import Path

# ==================================================
# 2. Settings and Paths
# ==================================================

COUNTRY_CODE = "MYS"

INPUT_FILE = Path(
    "outputs/detection/detection_dataset.csv"
)

OUTPUT_DIR = Path(
    "outputs/speciesnet"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "speciesnet_results.json"

# ==================================================
# 3. Read the detection dataset
# ==================================================

# Load the detection dataset.
df = pd.read_csv(INPUT_FILE)

# Get image paths for SpeciesNet.
image_paths = df["image_path"].tolist()

IMAGE_LIST_FILE = OUTPUT_DIR / "image_paths.txt"

with open(IMAGE_LIST_FILE, "w", encoding="utf-8") as f:

    for image_path in image_paths:
        f.write(f"{image_path}\n")

# ==================================================
# 4. Display summary
# ==================================================   

print("=" * 40)
print("Running SpeciesNet")
print("=" * 40)

print(f"Country Code        : {COUNTRY_CODE}")
print(f"Images to classify  : {len(image_paths)}")

# ==================================================
# 5. Skip if nothing to classify
# ==================================================

if not image_paths:

    print("\nNo detected animals found.")
    print("SpeciesNet skipped.")

    quit()

# ==================================================
# 6. Build the SpeciesNet command
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
# 7. Run SpeciesNet
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
