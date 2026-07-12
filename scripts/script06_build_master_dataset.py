# ==================================================
# Wildlife Monitoring Pipeline
# Script 09 - Build Master Dataset
# ==================================================

# ==================================================
# Project Root
# ==================================================
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.deployments import (
    get_deployments)

from config.paths import (
    DEPLOYMENTS_OUTPUT,
    get_deployment_paths,
    MASTER_DATASET,
    DEPLOYMENT_SUMMARY
)
    
# ==================================================
# Selected Deployments
# ==================================================
all_data = []

# if deployments passed as args use them
# otherwise process all
if len(sys.argv) > 1:
    selected = sys.argv[1:]
else:
    selected = [
        f.name
        for f in sorted(DEPLOYMENTS_OUTPUT.iterdir())
        if f.is_dir()
    ]

print(f"Building master dataset for: {selected}")

for deployment in selected:
    paths = get_deployment_paths(deployment)
    dataset_file = paths["dataset"]

    if not dataset_file.exists():
        continue

    df = pd.read_csv(dataset_file)

    # Keep deployment information
    df.insert(0, "deployment", deployment)
    all_data.append(df)

# ==================================================
# Combine
# ==================================================

if all_data:

    master = pd.concat(all_data, ignore_index=True)

    # organized master dataset
    master = master.sort_values(
        by=[
            "deployment",
            "event_id"
        ]
    ).reset_index(drop=True)

    master.to_csv(MASTER_DATASET, index=False)

    print(
        f"Master dataset created "
        f"({len(master)} rows)"
    )

else:
    print("No deployment datasets found.")

# ==================================================
# Deployment Summary
# ==================================================

summary_rows = []

for deployment in selected:
    paths = get_deployment_paths(deployment)
    dataset_file = paths["dataset"]

    if not dataset_file.exists():
        continue

    df = pd.read_csv(dataset_file)
    images = len(df)
    events = df["event_id"].nunique()

    reviewed = (
        df["review_status"]
        .isin([
            "Auto Verified",
            "Verified",
            "Corrected"
        ])
        .sum()
    )

    display_species = (
        df["verified_common_name"]
        .replace("", pd.NA)
        .fillna(df["prediction_common_name"])
    )

    species = display_species.nunique()

    unknown = (display_species == "Unknown").sum()

    human = (display_species == "Human").sum()

    summary_rows.append({
        "deployment": deployment,
        "images": images,
        "events": events,
        "reviewed": reviewed,
        "species_found": species,
        "unknown": unknown,
        "human": human
    })

summary = pd.DataFrame(summary_rows)

summary = summary.sort_values(
    "deployment"
).reset_index(drop=True)

summary.to_csv(
    DEPLOYMENT_SUMMARY,
    index=False
)