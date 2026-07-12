'''
Build a standardized wildlife species dictionary.

The dictionary provides a single source of truth for
taxonomy, scientific names, and common names used
throughout the review application.

This ensures consistent species labels across all
datasets and future projects.
'''

# ==================================================
# 1. Import Libraries
# ==================================================
import pandas as pd
from pathlib import Path
import sys

# =================================================
# 2. File Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.species_lookup import get_species_information

from config.paths import (
    DICTIONARY_PATH,
    DEPLOYMENTS_OUTPUT,
    get_deployment_paths
)

# ==================================================
# 3. Load Data
# ==================================================

all_data = []

for deployment_folder in sorted(DEPLOYMENTS_OUTPUT.iterdir()):

    if not deployment_folder.is_dir():
        continue

    # skip master folder
    if deployment_folder.name == "master":
        continue

    paths = get_deployment_paths(deployment_folder.name)
    dataset_file = paths["dataset"]

    if not dataset_file.exists():
        continue

    dataset = pd.read_csv(dataset_file)
    all_data.append(dataset)

if not all_data:
    print("No deployment datasets found.")
    sys.exit()

# combine all deployments into one
dataset = pd.concat(all_data, ignore_index=True)

# ==================================================
# 4. Select Best Available Species Name
# ==================================================

# Use the best available species label.
dataset["best_common_name"] = (
    dataset["verified_common_name"]
    .fillna("")
)

# Continue filling missing values.
mask = dataset["best_common_name"] == ""

dataset.loc[mask, "best_common_name"] = dataset.loc[
    mask,
    "prediction_common_name"
]

# then classifier
mask = dataset["best_common_name"] == ""

dataset.loc[mask, "best_common_name"] = dataset.loc[
    mask,
    "classifier_common_name"
]

# Keep Only Species-Level Detections

dataset = dataset[
    # human verified — trust regardless of rank
    (
        dataset["verified_common_name"]
        .fillna("")
        .str.strip()
        != ""
    )
    |
    # SpeciesNet reached species level
    (
        dataset["prediction_rank"] == "Species"
    )
].copy()

# ==================================================
# 5. Remove Empty Species
# ==================================================

dictionary = dataset[
    dataset["best_common_name"] != ""
].copy()

# ==================================================
# 7. Removing Non-Wildlife Labels
# ==================================================

INVALID_SPECIES = [
    "No Cv Result",
    "Human"
]

dictionary = dictionary[
    ~dictionary["best_common_name"].isin(
        INVALID_SPECIES
    )
]

# ==================================================
# 7. Remove Duplicate Species
# ==================================================
dictionary = dictionary.drop_duplicates(
    subset="best_common_name"
)

# ==================================================
# 8. Sort Species
# ==================================================
dictionary = dictionary.sort_values(
    "best_common_name"
).reset_index(drop=True)

# ==================================================
# 9. Create Species IDs
# ==================================================
dictionary["species_id"] = [
    
    f"SP{i:04d}"

    for i in range(
        1,
        len(dictionary) + 1
    )

]

# ==================================================
# 10. Build Species Dictionary
# ==================================================

species_rows = []

for index, (_, row) in enumerate(dictionary.iterrows(), start=1):

    species = get_species_information(
        row.best_common_name,
        prediction=row.to_dict()
    )

    species["species_id"] = f"SP{index:04d}"
    species["status"] = "Verified"

    species_rows.append(species)

species_dictionary = pd.DataFrame(species_rows)

# ==================================================
# 11. Save Species Dictionary
# ==================================================

# created species dictionary CSV file column fix
species_dictionary = species_dictionary[[
    "species_id",
    "common_name",
    "scientific_name",
    "taxonomy_class",
    "taxonomy_order",
    "taxonomy_family",
    "taxonomy_genus",
    "taxonomy_species",
    "taxonomy_source",
    "status"
]]

species_dictionary.to_csv(
    DICTIONARY_PATH,
    index=False
)

# ==================================================
# 12. Summary
# ==================================================
print("=" * 40)
print("Species Dictionary Created")
print("=" * 40)

print(f"Species : {len(species_dictionary)}")

print(f"Saved   : {DICTIONARY_PATH}")
