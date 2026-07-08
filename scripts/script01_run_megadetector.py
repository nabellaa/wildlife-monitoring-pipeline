"""
==================================================
Script: script01_run_megadetector.py

Purpose
    Detect animals in camera trap images using
    MegaDetector (MDV5A).

Input
    data/batch_sample/<deployment>/

Output
    outputs/deployments/<deployment>/megadetector/
    megadetector_results.json

Next
    Script 02 - Run SpeciesNet

Author:
    Bella

Project:
    Wildlife Monitoring Pipeline
==================================================
"""

# ==================================================
# 1. Import Libraries
# ==================================================

from pathlib import Path
import sys
import json

from megadetector.detection.run_detector_batch import (
    load_and_run_detector_batch,
)

# ==================================================
# 2. Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import get_deployment_paths

deployment    = sys.argv[1]
paths         = get_deployment_paths(deployment, create_folders=True)
input_folder  = paths["input_folder"]
output_file   = paths["megadetector_json"]

# ==================================================
# 3. Find Images
# ==================================================

image_extensions = {".jpg", ".jpeg", ".png"}

jpg_files = list({
    p.resolve()
    for p in input_folder.rglob("*")
    if p.is_file()
    and p.suffix.lower() in image_extensions
})

print(f"Images found: {len(jpg_files)}")

# ==================================================
# 4. Run MegaDetector
# ==================================================

# MDV5A detects animals, people and vehicles.
# First run downloads the model automatically (~1 GB).
# Subsequent runs reuse the cached model.

model_name = "MDV5A"

print(f"Model    : {model_name}")
print(f"Images   : {len(jpg_files)}")
print("Starting MegaDetector...")

results = load_and_run_detector_batch(
    model_file=model_name,
    image_file_names=jpg_files,
    quiet=False
)

# ==================================================
# 5. Save Results
# ==================================================

# Convert Path objects to strings for JSON serialization
for r in results:
    r["file"] = str(r["file"])

if not results:
    print("No detections returned.")
    sys.exit(0)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# ==================================================
# 6. Summary
# ==================================================

print("\n" + "=" * 40)
print("MegaDetector Complete")
print("=" * 40)
print(f"Images Processed : {len(jpg_files)}")
print(f"Model Used       : {model_name}")
print(f"Results Saved    : {output_file}")