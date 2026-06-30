"""
==============================================================================
script05_merge_species_results
------------------------------------------------------------------------------
Purpose:
Merge the Detection Dataset with SpeciesNet predictions to produce the
final Wildlife Dataset.

Input
-----
outputs/datasets/detection_dataset.csv
outputs/speciesnet/speciesnet_results.json

Output
------
outputs/datasets/wildlife_dataset.csv

The final dataset combines:
- Camera metadata
- MegaDetector detections
- SpeciesNet taxonomy
- Species confidence
- Review-ready fields
==============================================================================
"""

# ==================================================
# 1. Import Libraries
# ==================================================

import json
import pandas as pd
from pathlib import Path

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
detection_file = paths["detection_csv"]
speciesnet_file = paths["speciesnet_json"]
output_file = paths["dataset"]

# ==================================================
# 3. Load Data
# ==================================================

# Load Detection Dataset

print("Loading Detection Dataset...")

dataset = pd.read_csv(detection_file)

print(f"Rows : {len(dataset)}")

# Load SpeciesNet Results

print("Loading SpeciesNet Results...")

with open(speciesnet_file, "r", encoding="utf-8") as f:
    species_results = json.load(f)


# ==================================================
# 4. Build a Lookup Dictionary
# ==================================================

species_lookup = {}

predictions = species_results["predictions"]

for item in predictions:

    species_lookup[item["filepath"]] = item

# ==================================================
# 5. Helper Function
# ==================================================

def parse_speciesnet_prediction(prediction):

    if not prediction:
        return {}

    parts = prediction.split(";")

    while len(parts) < 7:
        parts.append("")

    # ----------------------------------------------
    # Determine prediction rank
    # ----------------------------------------------

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

        "prediction_class": parts[1].title(),
        "prediction_order": parts[2].title(),
        "prediction_family": parts[3].title(),
        "prediction_genus": parts[4].title(),
        "prediction_species": parts[5].title(),
        "prediction_common_name": parts[6].title(),
        "prediction_rank": prediction_rank

    }
# ==================================================
# 6. Parse Top-1 SpeciesNet Predictions
# ==================================================

def parse_classifier_prediction(item):

    classes = item["classifications"]["classes"]
    scores = item["classifications"]["scores"]

    if len(classes) == 0:

        return {}

    parts = classes[0].split(";")

    while len(parts) < 7:
        parts.append("")

    return {

        "classifier_species": parts[5].title(),
        "classifier_common_name": parts[6].title(),
        "classifier_score": scores[0]

    }

# ==================================================
# 7. Merge Datasets
# ==================================================

print("Merging Results...")

for index, row in dataset.iterrows():

    # 1. Get image key
    image_path = row["image_path"]

    # 2. Find prediction result
    if image_path not in species_lookup:
        continue

    # 3. Extract taxonomy (Step 5)
    species = species_lookup[image_path]

    # 4. Split the raw prediction into taxonomy levels and common name
    prediction = parse_speciesnet_prediction(species.get("prediction", ""))

    # 5. Parse classifier's best prediction
    classifier = parse_classifier_prediction(species)

    # 6. Add prediction columns
    for key, value in prediction.items():
        dataset.loc[index, key] = value

    # Add classifier columns
    for key, value in classifier.items():
        dataset.loc[index, key] = value

    # Add prediction metadata
    dataset.loc[index, "prediction_score"] = species.get("prediction_score")

# ==================================================
# 8. Create Verified Taxonomy Columns
# ==================================================

VERIFIED_COLUMNS = [

    "scientific_name",

    "taxonomy_class",
    "taxonomy_order",
    "taxonomy_family",
    "taxonomy_genus",
    "taxonomy_species"

]

for column in VERIFIED_COLUMNS:

    if column not in dataset.columns:
        dataset[column] = ""

# ==================================================
# 9. Save the final dataset
# ==================================================

dataset.to_csv(
    output_file,
    index=False
)

print()

print("=" * 40)
print("Merging Dataset Complete")
print("=" * 40)

print(f"Images : {len(dataset)}")
print(f"Saved : {output_file}")

# later we can use this for full sc name
# scientific_name = f"{prediction_genus} {prediction_species}"