"""
==================================================
Script: 03_build_detection_dataset.py

Purpose:
    Convert MegaDetector detection results into a structured CSV dataset for downstream analysis.

This script:
1. Loads MegaDetector JSON results.
2. Filters detections using a confidence threshold.
3. Extracts EXIF metadata from each detected image.
4. Creates one record per image.
5. Saves the results as detection_dataset.csv.

Input
outputs/megadetector/megadetector_results.json

Output
outputs/detection/detection_dataset.csv

IMPORTANT: Update the EXIFTOOL_PATH variable to point to your ExifTool installation.

Download:
https://exiftool.org/

save the executable to C:\Tools\ExifTool\exiftool.exe (or update the path in the script)

Next Step
Script 04 - SpeciesNet classification

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

import pandas as pd

from pathlib import Path

# ==================================================
# 2. Paths
# ==================================================

project_root = Path(__file__).resolve().parent.parent

input_file = (project_root/ "outputs"/ "megadetector"/ "megadetector_results.json")

output_folder = (project_root/ "outputs"/ "detection")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = (output_folder/ "detection_dataset.csv")

# ==================================================
# 2. Detection Settings
# ==================================================

# Minimum MegaDetector confidence required to keep an image.
CONF_THRESHOLD = 0.30

# Location of ExifTool executable.
# Update this path if ExifTool is installed elsewhere.
EXIFTOOL_PATH = r"C:\Tools\ExifTool\exiftool.exe"

# ==================================================
# 3. Load MegaDetector results
# ==================================================

with open(input_file, "r", encoding="utf-8") as f:
    results = json.load(f)

# ==================================================
# 4. Read Image Metadata
# ==================================================

def get_metadata(image_path):

    command = [
        EXIFTOOL_PATH,
        "-j",
        str(image_path)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return json.loads(result.stdout)[0]

# ==================================================
# 5. Build Detection Dataset
# ==================================================

dataset = []

for image in results:

    detections = image["detections"]

    valid_detections = []

    for detection in detections:

        if detection["conf"] >= CONF_THRESHOLD:
            valid_detections.append(detection)

    if not valid_detections:
        continue

    # Read metadata
    image_metadata = get_metadata(image["file"])

    row = {
        "image_path": image["file"],
        "file_name": Path(image["file"]).name,
        "folder_name": Path(image["file"]).parent.name,
        "capture_datetime": image_metadata.get("DateTimeOriginal"),
        "temperature_c": image_metadata.get("AmbientTemperature"),
        "moon_phase": image_metadata.get("MoonPhase"),
        "event_number": image_metadata.get("EventNumber"),
        "sequence": image_metadata.get("Sequence"),
        "detection_conf": max(d["conf"] for d in valid_detections)
    }

    dataset.append(row)

# ==================================================
# 6. Save dataset
# ==================================================

df = pd.DataFrame(dataset)
df.to_csv(output_file, index=False)

# ==================================================
# 7. Summary
# ==================================================

print("=" * 40)
print("Detection Dataset Complete")
print("=" * 40)

print(f"Confidence Threshold : {CONF_THRESHOLD}")
print(f"Images Processed : {len(results)}")
print(f"Detections Saved : {len(df)}")

print(f"\nOutput:")
print(output_file)

