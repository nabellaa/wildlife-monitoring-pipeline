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

# =================================================
# 2. File Paths
# ==================================================
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import (
    DATASET_PATH,
    DICTIONARY_PATH
)

# ==================================================
# 3. Load Data
# ==================================================
print("Loading Wildlife Dataset...")
dataset = pd.read_csv(DATASET_PATH)

# ==================================================
# 4. Select Best Available Species Name
# ==================================================
print("Selecting Best Available Species...")

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

# ==================================================
# 5. Remove Empty Species
# ==================================================
print("Removing Empty Species...")

dictionary = dataset[
    dataset["best_common_name"] != ""
].copy()

# ==================================================
# 6. Remove AI Placeholder Labels
# ==================================================

print("Keeping Species-Level Predictions Only...")

dictionary = dictionary[
    (dictionary["verified_common_name"].fillna("") != "")
    |
    (dictionary["prediction_rank"] == "Species")
]

# ==================================================
# 7. Removing Non-Wildlife Labels
# ==================================================
print("Removing Non-Wildlife Labels...")

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

species_dictionary = pd.DataFrame({

    "species_id": dictionary["species_id"],
    "common_name": dictionary["best_common_name"],
    "scientific_name": "",
    "taxonomy_class": "",
    "taxonomy_order": "",
    "taxonomy_family": "",
    "taxonomy_genus": "",
    "taxonomy_species": "",
    "status": "Draft"

})

# ==================================================
# 11. Save Species Dictionary
# ==================================================
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
