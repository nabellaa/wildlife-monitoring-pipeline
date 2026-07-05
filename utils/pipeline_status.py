# utils/pipeline_status.py
# Utility functions for managing pipeline status information
# This module provides functions to load and save the status of the wildlife monitoring pipeline.

import json
from pathlib import Path
from datetime import datetime

from config.paths import OUTPUT_PATH

PIPELINE_STATUS_PATH = OUTPUT_PATH / "logs" / "pipeline_status.json"


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

    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)

    data = {
        "last_run_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deployment": deployment,
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