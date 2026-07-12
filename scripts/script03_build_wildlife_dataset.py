"""
==================================================
Script: script03_build_wildlife_dataset.py

Purpose
    Build the final wildlife dataset by combining
    MegaDetector detections, EXIF metadata, and
    SpeciesNet predictions. Flags events for human
    review based on prediction quality rules.

IMPORTANT: 
Required for extracting RECONYX camera trap metadata.
Update the EXIFTOOL_PATH variable to point to your ExifTool installation.

Download:
https://exiftool.org/

save the executable to C:\Tools\ExifTool\exiftool.exe 
(or update the path in the script)

Input
    outputs/deployments/<deployment>/megadetector/
    megadetector_results.json

    outputs/deployments/<deployment>/speciesnet/
    speciesnet_results.json

Output
    outputs/deployments/<deployment>/processed/
    wildlife_dataset.csv

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
import sys
import os

# ==================================================
# 2. Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import get_deployment_paths

deployment      = sys.argv[1]
paths           = get_deployment_paths(deployment, create_folders=True)
megadetector_file = paths["megadetector_json"]
speciesnet_file   = paths["speciesnet_json"]
output_file       = paths["dataset"]

# ==================================================
# Detection Settings
# ==================================================

CONF_THRESHOLD = 0.30
EXIFTOOL_PATH  = r"C:\Tools\ExifTool\exiftool.exe"

# ==================================================
# Safe Check
# ==================================================

if not megadetector_file.exists():
    print("No MegaDetector results found. Skipping merge.")
    sys.exit(0)

if not speciesnet_file.exists():
    print("No SpeciesNet results found. Skipping merge.")
    sys.exit(0)

# ==================================================
# 3. Load MegaDetector Results
# ==================================================

with open(megadetector_file, "r", encoding="utf-8") as f:
    megadetector_results = json.load(f)

# ==================================================
# 4. Load SpeciesNet Results
# ==================================================

with open(speciesnet_file, "r", encoding="utf-8") as f:
    species_results = json.load(f)

# ==================================================
# 5. Build SpeciesNet Lookup
# ==================================================

species_lookup = {}

for item in species_results["predictions"]:
    species_lookup[item["filepath"]] = item

# ==================================================
# 6. Read EXIF Metadata
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
# 7. Helper Functions
# ==================================================

def parse_speciesnet_prediction(prediction):

    if not prediction:
        return {}

    parts = prediction.split(";")

    while len(parts) < 7:
        parts.append("")

    if parts[5]:
        prediction_rank = "Species"
    elif parts[4]:
        prediction_rank = "Genus"
    elif parts[3]:
        prediction_rank = "Family"
    elif parts[2]:
        prediction_rank = "Order"
    elif parts[1]:
        prediction_rank = "Class"
    else:
        prediction_rank = "Unknown"

    return {
        "prediction_class":       parts[1].title(),
        "prediction_order":       parts[2].title(),
        "prediction_family":      parts[3].title(),
        "prediction_genus":       parts[4].title(),
        "prediction_species":     parts[5].title(),
        "prediction_common_name": parts[6].title(),
        "prediction_rank":        prediction_rank
    }

def parse_classifier_prediction(item):

    classes = item["classifications"]["classes"]
    scores  = item["classifications"]["scores"]

    if not classes:
        return {}

    parts = classes[0].split(";")

    while len(parts) < 7:
        parts.append("")

    return {
        "classifier_species":     parts[5].title(),
        "classifier_common_name": parts[6].title(),
        "classifier_score":       scores[0]
    }

# ==================================================
# 8. Build Dataset
# ==================================================
# build lookup with normalised paths
species_lookup = {
    Path(item["filepath"]).name: item
    for item in species_results.get("predictions", [])
}

dataset = []

for image in megadetector_results:

    # filter by confidence
    valid_detections = [
        d for d in image["detections"]
        if d["conf"] >= CONF_THRESHOLD
    ]

    if not valid_detections:
        continue

    image_path = Path(image["file"])

    # extract EXIF
    try:
        metadata = get_metadata(image["file"])
    except Exception:
        metadata = {}

    # parse datetime
    capture_datetime = metadata.get("DateTimeOriginal")
    if capture_datetime:
        try:
            capture_datetime = datetime.strptime(
                capture_datetime,
                "%Y:%m:%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            capture_datetime = None

    # parse temperature
    temperature = metadata.get("AmbientTemperature")
    if temperature:
        try:
            temperature = float(
                str(temperature).replace(" C", "")
            )
        except Exception:
            temperature = None

    # best detection
    best_detection = max(
        valid_detections,
        key=lambda d: d["conf"]
    )

    # Extract Camera Name
    camera_name = ""

    for parent in image_path.parents:
        folder = parent.name.replace(" ", "")

        if (
            folder.startswith("REC")
            or folder.startswith("XR")
            or folder.startswith("HC")
        ):
            camera_name = folder.split("_")[0]
            break

    row = {
        "image_path":           image["file"],
        "file_name":            image_path.name,
        "folder_name":          image_path.parent.parent.name,
        "camera_name":          camera_name,
        "capture_datetime":     capture_datetime,
        "temperature_c":        temperature,
        "moon_phase":           metadata.get("MoonPhase"),
        "event_number":         metadata.get("EventNumber"),
        "sequence":             metadata.get("Sequence"),
        "detection_confidence": best_detection["conf"],
        "bbox_x":               best_detection["bbox"][0],
        "bbox_y":               best_detection["bbox"][1],
        "bbox_width":           best_detection["bbox"][2],
        "bbox_height":          best_detection["bbox"][3]
    }

    # merge speciesnet
    image_key = Path(image["file"]).name
    print("IMAGE KEY:", image_key)

    if len(species_lookup) < 5:
        print("LOOKUP SAMPLE KEYS:", list(species_lookup.keys()))

    if image_key in species_lookup:

        item       = species_lookup[image_key]
        prediction = parse_speciesnet_prediction(item.get("prediction", ""))
        classifier = parse_classifier_prediction(item)

        row.update(prediction)
        row.update(classifier)
        row["prediction_score"] = item.get("prediction_score")

    dataset.append(row)

# ==================================================
# 9. Build DataFrame
# ==================================================

df = pd.DataFrame(dataset)

# ==================================================
# 10. Generate Event ID (previously done in script05_build_review_queue.py)
# ==================================================

df["event_id"] = (
    deployment
    + "_"
    + df["folder_name"]
    + "_"
    + df["camera_name"]
    + "_"
    + df["event_number"].astype(str)
)

# ==================================================
# 11. Review Columns
# ==================================================

df["review_status"]        = "Auto Verified"
df["review_required"]      = False
df["verified_common_name"] = ""
df["reviewer"]             = "System"
df["review_notes"]         = "SpeciesNet prediction accepted automatically."
df["review_timestamp"]     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==================================================
# 12. Flag for Review
# ==================================================

LOW_PREDICTION_CONFIDENCE = 0.80

def flag_for_review(df, mask):
    df.loc[mask, "review_required"] = True

# Rule 1 — incomplete species prediction
flag_for_review(df,
    df["prediction_species"].isna()
    | (df["prediction_species"] == "")
)

# Rule 2 — not species level
flag_for_review(df,
    df["prediction_rank"] != "Species"
)

# Rule 3 — low confidence
flag_for_review(df,
    df["prediction_score"] < LOW_PREDICTION_CONFIDENCE
)

# ==================================================
# 13. Add Verified Taxonomy Columns
# ==================================================

VERIFIED_COLUMNS = [
    "scientific_name",
    "taxonomy_class",
    "taxonomy_order",
    "taxonomy_family",
    "taxonomy_genus",
    "taxonomy_species",

    "taxonomy_source"
]

for column in VERIFIED_COLUMNS:

    if column not in df.columns:
        df[column] = ""

# ==================================================
# 13. Auto-verify Species Level Predictions
# ==================================================

auto_verify_mask = (
    df["prediction_rank"] == "Species"
) & (
    df["prediction_common_name"].fillna("") != ""
)

df.loc[auto_verify_mask, "review_status"]        = "Auto Verified"
df.loc[auto_verify_mask, "review_required"]      = False
df.loc[auto_verify_mask, "verified_common_name"] = df.loc[
    auto_verify_mask, "prediction_common_name"
]
df.loc[auto_verify_mask, "reviewer"]             = "System"
df.loc[auto_verify_mask, "review_notes"]         = "SpeciesNet prediction accepted automatically."
df.loc[auto_verify_mask, "review_timestamp"]     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==================================================
# 14. Save Verified Species to Dictionary
# ==================================================
from utils.species_lookup import get_species_information

for i, row in df.iterrows():

    if str(row.get("scientific_name", "")).strip():
        continue

    if (
        pd.notna(row["verified_common_name"])
        and row["verified_common_name"] != ""
    ):
        species_name = row["verified_common_name"]

    elif (
        row["prediction_rank"] == "Species"  # ← only species ranked
        and pd.notna(row["prediction_common_name"])
        and row["prediction_common_name"] != ""
    ):
        species_name = row["prediction_common_name"]

    else:
        continue

    prediction = row.to_dict()

    species = get_species_information(
        species_name,
        prediction=prediction
    )

    for column in VERIFIED_COLUMNS:

        if column in species:
            df.loc[i, column] = species[column]

# ==================================================
# 15. Save
# ==================================================

df.to_csv(output_file, index=False)

print()
print("=" * 40)
print("Wildlife Dataset Created")
print("=" * 40)
print(f"Images          : {len(df)}")
print(f"Events          : {df['event_id'].nunique()}")
print(f"Review Required : {df['review_required'].sum()}")
print(f"No Review       : {len(df) - df['review_required'].sum()}")
print(f"Saved           : {output_file}")