

# ==================================================
# 1. Import Libraries
# ==================================================

import pandas as pd
from pathlib import Path
import os

# ==================================================
# 2. File Paths
# ==================================================
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import get_deployment_paths

deployment = sys.argv[1]
paths = get_deployment_paths(deployment)
INPUT_FILE = paths["dataset"]

# ==================================================
# 3. Load Wildlife Dataset
# ==================================================

# SAFE CHECK: file exists
if not os.path.exists(INPUT_FILE):
    print("No dataset file found. Skipping review queue build.")
    sys.exit(0)

# SAFE LOAD CSV
try:
    dataset = pd.read_csv(INPUT_FILE)
except pd.errors.EmptyDataError:
    print("Dataset is empty. Skipping review queue build.")
    sys.exit(0)

# SAFE CHECK: dataset is not empty
if dataset.empty:
    print("Dataset is empty. Skipping review queue build.")
    sys.exit(0)

# ==================================================
# 4. Generate Event ID
# ==================================================

dataset["event_id"] = (
    dataset["folder_name"]
    + "_"
    + dataset["camera_name"]
    + "_"
    + dataset["folder_name"]
    + "_"
    + dataset["event_number"].astype(str)
)

# ==================================================
# 5. Review Columns  
# ==================================================

dataset["review_status"] = ""
dataset["review_required"] = False
dataset["verified_common_name"] = ""
dataset["reviewer"] = ""
dataset["review_notes"] = ""
dataset["review_timestamp"] = ""

# ==================================================
# 5. Helper Function
# ==================================================

def flag_for_review(dataset, mask):

    dataset.loc[mask, "review_required"] = True

# ==================================================
# 6. Rule 1 - Species-Level Prediction
# ==================================================

mask = (
    dataset["prediction_species"].isna()
    | (dataset["prediction_species"] == "")
)

flag_for_review(dataset,mask,)

# ==================================================
# 7. Rule 2 - Mixed Predictions Within Event
# ==================================================

mask = dataset["prediction_rank"] != "Species"

flag_for_review(
    dataset,
    mask,
)

# ==================================================
# 7. Rule 3 - Low prediction confidence
# ==================================================

LOW_PREDICTION_CONFIDENCE = 0.80

mask = dataset["prediction_score"] < LOW_PREDICTION_CONFIDENCE

flag_for_review(dataset,mask,)

# ==================================================
# 8. Save Updated Dataset
# ==================================================

dataset.to_csv(INPUT_FILE, index=False)

print()

print("=" * 40)
print("Review Queue Ready")
print("=" * 40)
print(f"Events : {dataset['event_id'].nunique()}")
print(f"Images : {len(dataset)}")

print("=" * 40)
print("Review Summary")
print("=" * 40)
print("Review Required :",dataset["review_required"].sum())
print("No Review :",len(dataset) - dataset["review_required"].sum())


print(f"Saved  : {INPUT_FILE}")

