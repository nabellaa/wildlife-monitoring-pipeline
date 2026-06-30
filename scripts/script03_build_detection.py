"""
==================================================
Script: script03_build_detection.py

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

IMPORTANT: 
Required for extracting RECONYX camera trap metadata.
Update the EXIFTOOL_PATH variable to point to your ExifTool installation.

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
from datetime import datetime

# ==================================================
# 2. Paths
# ==================================================
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
    
from config.paths import get_deployment_paths

deployment = sys.argv[1]
paths = get_deployment_paths(deployment)
input_file = paths["megadetector_json"]
output_folder = paths["detection_folder"]
output_file = paths["detection_csv"]

# ==================================================
# 2. Detection Settings
# ==================================================

# Minimum MegaDetector confidence required to keep an image.
CONF_THRESHOLD = 0.30

# Required for extracting RECONYX camera trap metadata.
# Update this path if ExifTool is installed in a different location.
EXIFTOOL_PATH = r"C:\Tools\ExifTool\exiftool.exe"

# ==================================================
# 3. Load MegaDetector results
# ==================================================

with open(input_file, "r", encoding="utf-8") as f:
    results = json.load(f)

# ==================================================
# 4. Read Image Metadata
# ==================================================

# Read EXIF metadata from an image using ExifTool.
def get_metadata(image_path):

    # Build the ExifTool command and return metadata as JSON.
    command = [
        EXIFTOOL_PATH,
        "-j",
        str(image_path)
    ]

    # Execute ExifTool and capture its output.
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    # Convert JSON text into a Python dictionary.
    return json.loads(result.stdout)[0]

# ==================================================
# 5. Build Detection Dataset
# ==================================================

# Store the final detection dataset.
dataset = []

# Process each image from MegaDetector results.
for image in results:

    # Get all detections for the current image.
    detections = image["detections"]

    # Store detections that pass the confidence threshold.
    valid_detections = []

    # Keep only confident detections.
    for detection in detections:

        if detection["conf"] >= CONF_THRESHOLD:
            valid_detections.append(detection)

    # Skip images with no valid detections.
    if not valid_detections:
        continue

    # Extract camera trap metadata from the image.
    image_metadata = get_metadata(image["file"])

    # Convert EXIF timestamp to ISO format
    capture_datetime = image_metadata.get("DateTimeOriginal")

    if capture_datetime:
        capture_datetime = datetime.strptime(
            capture_datetime,
            "%Y:%m:%d %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")

    # Clean temperature value (e.g. "25 C" -> 25)
    temperature = image_metadata.get("AmbientTemperature")
    
    if temperature:
        temperature = float(temperature.replace(" C", ""))

    # Create one dataset record for the detected image.
    best_detection = max(
        valid_detections,
        key=lambda d: d["conf"]
    )

    row = {
        "image_path": image["file"],
        "file_name": Path(image["file"]).name,
        "folder_name": Path(image["file"]).parent.name,

        "capture_datetime": capture_datetime,
        "temperature_c": temperature,
        "moon_phase": image_metadata.get("MoonPhase"),
        "event_number": image_metadata.get("EventNumber"),
        "sequence": image_metadata.get("Sequence"),

        "detection_confidence": best_detection["conf"],
        "bbox_x": best_detection["bbox"][0],
        "bbox_y": best_detection["bbox"][1],
        "bbox_width": best_detection["bbox"][2],
        "bbox_height": best_detection["bbox"][3]
    }

    # Add the completed record to the dataset.
    dataset.append(row)

# ==================================================
# 6. Save dataset
# ==================================================

# Convert the dataset into a DataFrame.
df = pd.DataFrame(dataset)

# Save the dataset as a CSV file.
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

