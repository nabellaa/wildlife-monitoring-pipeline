"""
==================================================
Script: script02_run_megadetector.py

Purpose:
    Run MegaDetector on camera trap images.

Stage in Pipeline:
    02 - Detection

Author:
    Bella

Project:
    Wildlife Monitoring Pipeline

Description:
    Applies pre-trained MegaDetector model to detect animals,
    people, and vehicles in camera trap images.
==================================================
"""

# ==================================================
# 1. Import Libraries
# ==================================================

from pathlib import Path
import json

from megadetector.detection.run_detector_batch import (
    load_and_run_detector_batch,
)

# ==================================================
# 2. Project Paths
# ==================================================
import sys

# allow Python to find your config folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
    
from config.paths import (
    get_deployment_paths,
)

deployment = sys.argv[1]
paths = get_deployment_paths(deployment)
input_folder = paths["input_folder"]

# ==================================================
# 3. Output Paths
# ==================================================

output_folder = paths["megadetector_folder"]
output_file = paths["megadetector_json"]

# ==================================================
# 4. Find Photos
# ==================================================

image_extensions = {".jpg", ".jpeg", ".png"}

jpg_files = list({
    p.resolve()
    for p in input_folder.rglob("*")
    if p.is_file() and p.suffix.lower() in image_extensions
})

print(f"Photos found: {len(jpg_files)}")
print(f"Unique files: {len(set(jpg_files))}")


# ==================================================
# 5. MegaDetector Model
# ==================================================

model_name = "MDV5A"

# MegaDetector uses a pre-trained AI model (MDV5A)
# to detect animals, people and vehicles in images.

# The first run downloads the model automatically.
# Later runs reuse the local copy, making them much faster.

print(f"Using model: {model_name}")
print(f"Processing {len(jpg_files)} images...")


# ==================================================
# Note on Model Download:
# The first time MegaDetector runs,
# it automatically downloads the MDV5A model.

# Model location (Windows):
# C:\Users\<username>\AppData\Local\Temp\megadetector_models

# Later runs reuse this file, so they start much faster.
# ==================================================

# ==================================================
# 6. Run MegaDetector
# ==================================================

print("Starting MegaDetector...")

results = load_and_run_detector_batch(
    model_file=model_name,               #Use the AI model called MDV5A.
    image_file_names=jpg_files,          #List of image file paths to process.
    quiet=False                          #Print progress and info to the console.
)

# While saving MegaDetector results using `json.dump()`, the script failed with the error:
# TypeError: Object of type windowspath is not JSON serializable
# This is because the results contain Path objects (from pathlib) which cannot be directly serialized to JSON.
# To fix this, we need to convert the Path objects to strings before saving.
# Convert Path objects to strings (JSON safe)
for r in results:
    r["file"] = str(r["file"])

print("MegaDetector finished.")
# ==================================================
# 7. Save Results
# ==================================================
if not results:
    print("No detections returned.")
    sys.exit(0)

print(type(results))
print(type(results[0]))
print(results[0])

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)     #Save the results as a JSON file with pretty formatting.


# ==================================================
# 8. Summary
# ==================================================

print("\n========================================")
print("MegaDetector Complete")
print("========================================")
print(f"Photos Processed : {len(jpg_files)}")
print(f"Model Used       : {model_name}")
print(f"Output Saved     : {output_file}")
print("========================================")