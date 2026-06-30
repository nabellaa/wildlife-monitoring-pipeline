# ==================================================
# Wildlife Monitoring Pipeline
# Pipeline Runner
# ==================================================

import subprocess
import sys
from time import perf_counter

from config.paths import (
    PROJECT_ROOT,
    get_deployment_paths
)

# ==================================================
# Pipeline Steps
# ==================================================

def get_pipeline(deployment):

    paths = get_deployment_paths(deployment)

    return [

        {
            "script": "script02_run_megadetector.py",
            "name": "Running MegaDetector",
            "output": paths["megadetector_json"]
        },

        {
            "script": "script03_build_detection.py",
            "name": "Building Detection Dataset",
            "output": paths["detection_csv"]
        },

        {
            "script": "script04_run_speciesnet.py",
            "name": "Running SpeciesNet",
            "output": paths["speciesnet_json"]
        },

        {
            "script": "script05_merge_species_results.py",
            "name": "Merging Species Results",
            "output": paths["dataset"]
        },

        {
            "script": "script06_build_review_queue.py",
            "name": "Building Review Queue",
            "output": paths["dataset"]
        }

    ]
# ==================================================
# Run Pipeline
# ==================================================

def run_pipeline(

    deployment,
    skip_completed=False,
    progress_callback=None

):

    pipeline = get_pipeline(deployment)
    total_steps = len(pipeline)
    start_time = perf_counter()

    for index, step in enumerate(pipeline):

        script_path = (
            PROJECT_ROOT /
            "scripts" /
            step["script"]
        )

        # ------------------------------------------
        # Skip Existing Outputs
        # ------------------------------------------

        if (
            skip_completed
            and
            step["output"].exists()
        ):

            if progress_callback:
                progress_callback(
                    index + 1,
                    total_steps,
                    f"⏭ {step['name']} (Skipped)"
                )
            continue

        # ------------------------------------------
        # Running
        # ------------------------------------------

        if progress_callback:

            progress_callback(
                index + 1,
                total_steps,
                step["name"]
            )

        result = subprocess.run(

            [
                sys.executable,
                str(script_path),
                deployment
            ],

            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True

        )

        if result.returncode != 0:
            raise RuntimeError(
                f"""
        Step Failed:
        {step['name']}

        Script:
        {step['script']}

        Deployment:
        {deployment}

        STDERR:
        {result.stderr}

        STDOUT:
        {result.stdout}
        """
            )
        
    duration = perf_counter() - start_time
    return duration

# ==================================================
# Run Pipeline From Step for reset button
# ==================================================

def run_pipeline_from(
    deployment,
    start_from, 
    progress_callback=None
):

    pipeline = get_pipeline(deployment)
    total_steps = len(pipeline)
    start_time = perf_counter()

    for index, step in enumerate(
        pipeline[start_from - 1:],
        start=start_from - 1
    ):

        script_path = (
            PROJECT_ROOT /
            "scripts" /
            step["script"]
        )

        if progress_callback:
            progress_callback(
                index + 1,
                total_steps,
                step["name"]
            )

        result = subprocess.run(
            [
                sys.executable, 
                str(script_path),
                deployment
            ],

            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{step['name']}\n\n"
                f"{result.stderr}"
            )

    duration = perf_counter() - start_time
    return duration