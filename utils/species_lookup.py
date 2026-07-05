# helper that help find the info of the species found and autofill the dataset and update the dicitonary
# could give the full taxonomy and the iucn data of the species for future analyst in the dashboard.
# source can be change when needed

# ==================================================
# Wildlife Monitoring Pipeline
# Species Lookup
# ==================================================

import requests
from pathlib import Path
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import DICTIONARY_PATH

# quick cache to avoid repeated lookups for the same species
SPECIES_CACHE = {}

DICTIONARY_CACHE = None

def load_dictionary():
    global DICTIONARY_CACHE

    if DICTIONARY_CACHE is not None:
        return DICTIONARY_CACHE

    if not DICTIONARY_PATH.exists():
        DICTIONARY_CACHE = pd.DataFrame()
        return DICTIONARY_CACHE

    DICTIONARY_CACHE = pd.read_csv(DICTIONARY_PATH)
    return DICTIONARY_CACHE

# ==================================================
# Empty Species Record
# ==================================================

def empty_species_record(common_name):

    return {

        "common_name": common_name,

        "scientific_name": "",

        "taxonomy_class": "",
        "taxonomy_order": "",
        "taxonomy_family": "",
        "taxonomy_genus": "",
        "taxonomy_species": "",

        "iucn_status": "",
        "population_trend": "",

        "taxonomy_source": "",
        "iucn_source": ""

    }

# refer availability from dictionary
def search_dictionary(common_name):

    if pd.isna(common_name):
        return None

    common_name = str(common_name).strip()

    if common_name == "":
        return None

    if not DICTIONARY_PATH.exists():
        return None

    dictionary = load_dictionary()

    match = dictionary[
        dictionary["common_name"]
        .fillna("")
        .str.strip()
        .str.casefold()
        ==
        common_name.strip().casefold()
    ]

    if match.empty:
        return None

    return match.iloc[0]

# ==================================================
# GBIF Species Search
# ==================================================

def search_gbif(common_name):
    url = "https://api.gbif.org/v1/species/search"

    try:
        response = requests.get(
            url,
            params={
                "q": common_name,
                "limit": 5
            },
            timeout=10
        )

        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            return None

        # Pick first result for now
        return results[0]

    except Exception:

        return None
    
# ==================================================
# convert GBIF
# ==================================================
def gbif_to_species(gbif, common_name):

    species = empty_species_record(common_name)

    species["scientific_name"] = gbif.get("scientificName", "")

    species["taxonomy_class"] = gbif.get("class", "")
    species["taxonomy_order"] = gbif.get("order", "")
    species["taxonomy_family"] = gbif.get("family", "")
    species["taxonomy_genus"] = gbif.get("genus", "")
    species["taxonomy_species"] = gbif.get("species", "")

    species["taxonomy_source"] = "GBIF"

    return species

# ==================================================
# Save to dictionary
# ==================================================
def save_species_to_dictionary(species):

    dictionary = load_dictionary()
    global DICTIONARY_CACHE

    match = (
        dictionary["common_name"]
        .fillna("")
        .str.strip()
        .str.casefold()
        ==
        species["common_name"].strip().casefold()
    )

    if match.any():
        # Update existing row
        idx = dictionary.index[match][0]

        # Only fill missing values
        columns = [

            "scientific_name",

            "taxonomy_class",
            "taxonomy_order",
            "taxonomy_family",
            "taxonomy_genus",
            "taxonomy_species",

            "taxonomy_source"

        ]

        for column in columns:
            current = dictionary.loc[idx, column]

            if pd.isna(current) or str(current).strip() == "":
                dictionary.loc[idx, column] = species[column]

    else:

        next_id = f"SP{len(dictionary)+1:04d}"

        species["species_id"] = next_id
        species["status"] = "Verified"

        new_row = pd.DataFrame([species])

        dictionary = pd.concat(
            [dictionary, new_row],
            ignore_index=True
        )

    dictionary.to_csv(
        DICTIONARY_PATH,
        index=False
    )

    # ==============================
    # CLEAR CACHE (IMPORTANT)
    # ==============================
    SPECIES_CACHE.clear()
    global DICTIONARY_CACHE
    DICTIONARY_CACHE = None

# ==================================================
# Lookup Species Information
# ==================================================
# Returns a dictionary containing taxonomy and conservation fields.

def get_species_information(common_name, prediction=None):

    # ==============================
    # SAFE INPUT CLEANING (IMPORTANT)
    # ==============================
    if pd.isna(common_name):
        return empty_species_record("")

    common_name = str(common_name).strip()

    if common_name == "":
        return empty_species_record("")
    
     # ==============================
    # CACHE CHECK (NEW)
    # ==============================
    key = common_name.casefold()

    if key in SPECIES_CACHE:
        return SPECIES_CACHE[key]

    # ------------------------------------------
    # Search Dictionary
    # ------------------------------------------
    dictionary_species = search_dictionary(common_name)


    if dictionary_species is not None:
        species = empty_species_record(common_name)

        for column in species.keys():

            if column in dictionary_species.index:
                value = dictionary_species[column]
                species[column] = "" if pd.isna(value) else value

        SPECIES_CACHE[key] = species

        # ONLY return if taxonomy is actually filled
        if species["scientific_name"].strip() != "":

            return species

    # ------------------------------------------
    # Use SpeciesNet Prediction
    # ------------------------------------------

    if prediction is not None:
        prediction_name = (
            str(
                prediction.get(
                    "prediction_common_name",
                    ""
                )
            )
            .strip()
            .casefold()
        )

        if prediction_name == common_name.strip().casefold():
            species = empty_species_record(common_name)

            species["scientific_name"] = (
                f"{prediction.get('prediction_genus','')} "
                f"{prediction.get('prediction_species','')}"
            ).strip()

            species["taxonomy_class"] = prediction.get("prediction_class", "")
            species["taxonomy_order"] = prediction.get("prediction_order", "")
            species["taxonomy_family"] = prediction.get("prediction_family", "")
            species["taxonomy_genus"] = prediction.get("prediction_genus", "")
            species["taxonomy_species"] = prediction.get("prediction_species", "")

            species["taxonomy_source"] = "SpeciesNet"

            save_species_to_dictionary(species)
            SPECIES_CACHE[key] = species
            return species
    # ------------------------------------------
    # Search GBIF
    # ------------------------------------------
    gbif = search_gbif(common_name)

    if gbif:
        species = gbif_to_species(gbif, common_name)

        # if prediction exists but GBIF missing species, optionally override genus/species
        if prediction is not None:
            species["taxonomy_source"] = "SpeciesNet + GBIF"

        # save to dictionary
        save_species_to_dictionary(species)
        SPECIES_CACHE[key] = species
        return species
    # ------------------------------------------
    # add iucn info
    # ------------------------------------------
'''
# remove above save to dictionary and cache, because if the species is not found in GBIF, we should not save it to the dictionary yet. We should only save it when we have a valid scientific name.
    
    iucn = search_iucn(species["scientific_name"])

    if iucn:
        species["iucn_status"] = iucn.get("status", "")
        species["population_trend"] = iucn.get("trend", "")
        species["iucn_source"] = "IUCN"

    save_species_to_dictionary(species)
    SPECIES_CACHE[key] = species
    return species

    # Nothing found
    return empty_species_record(common_name)

'''
