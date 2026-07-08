# utils/pipeline_status.py
# Utility functions for managing pipeline status information
# This module provides functions to load and save the status of the wildlife monitoring pipeline.

import json
from pathlib import Path
from datetime import datetime

from config.paths import LOGS_OUTPUT

PIPELINE_STATUS_PATH = LOGS_OUTPUT / "pipeline_status.json"


def load_pipeline_status():

    if not PIPELINE_STATUS_PATH.exists():
        return {}

    with open(PIPELINE_STATUS_PATH, "r") as f:
        return json.load(f)


def save_pipeline_status(
    deployment,
    duration_seconds,
    images_processed,
    status="Completed"
):

    data = load_pipeline_status()

    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)

    data[deployment] = {
        "last_run_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": duration_seconds,
        "duration_text": f"{minutes}m {seconds}s",
        "images_processed": images_processed,
        "status": status
    }

    PIPELINE_STATUS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(PIPELINE_STATUS_PATH, "w") as f:
        json.dump(data, f, indent=4)


# ==================================================
# Estimate Pipeline Time
# ==================================================

def estimate_pipeline_time(
    deployment,
    image_count
):
    """
    Estimate processing time (seconds).

    Priority:
    1. Previous run of the same deployment.
    2. Weighted average of all previous deployments.
    """

    pipeline_status = load_pipeline_status()

    # ------------------------------------------
    # Same deployment history
    # ------------------------------------------
    status = pipeline_status.get(deployment)

    if (
        status
        and status["images_processed"] > 0
    ):

        seconds_per_image = (
            status["duration_seconds"]
            / status["images_processed"]
        )

        return seconds_per_image * image_count

    # ------------------------------------------
    # Weighted average
    # ------------------------------------------
    total_seconds = 0
    total_images = 0

    for run in pipeline_status.values():

        images = run.get("images_processed", 0)

        if images > 0:

            total_seconds += run["duration_seconds"]
            total_images += images

    if total_images == 0:
        return None

    seconds_per_image = (
        total_seconds
        / total_images
    )

    return seconds_per_image * image_count