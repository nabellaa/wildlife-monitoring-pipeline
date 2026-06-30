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


from config.deployments import get_deployments

from config.paths import (
    get_deployment_paths,
    MASTER_DATASET,
    CLEAN_DATASET,
    DEPLOYMENT_SUMMARY
)

# ==================================================
# Build Master Dataset
# ==================================================

all_data = []

for deployment in get_deployments():
    paths = get_deployment_paths(deployment)
    dataset_file = paths["dataset"]

    if dataset_file.exists():
        df = pd.read_csv(dataset_file)
        # keep deployment information
        df.insert(
        0,
        "deployment",
        deployment
    )

    df.insert(
        1,
        "master_updated",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

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

for deployment in get_deployments():
    paths = get_deployment_paths(deployment)
    dataset_file = paths["dataset"]

    if not dataset_file.exists():
        continue

    df = pd.read_csv(dataset_file)
    images = len(df)
    events = df["event_id"].nunique()

    reviewed = (
        df["review_status"] == "Reviewed"
    ).sum()

    species = (
        df["verified_common_name"]
        .dropna()
        .nunique()
    )

    unknown = (
        df["verified_common_name"]
        == "Unknown"
    ).sum()

    human = (
        df["verified_common_name"]
        == "Human"
    ).sum()

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
