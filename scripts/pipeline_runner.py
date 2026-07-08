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
            "script": "script01_run_megadetector.py",
            "name":   "Running MegaDetector",
            "output": paths["megadetector_json"]
        },
        {
            "script": "script02_run_speciesnet.py",
            "name":   "Running SpeciesNet",
            "output": paths["speciesnet_json"]
        },
        {
            "script": "script03_build_wildlife_dataset.py",
            "name":   "Merging & Building Review Queue",
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
                f"Step Failed: {step['name']}\n\n"
                f"Script: {step['script']}\n\n"
                f"Deployment: {deployment}\n\n"
                f"STDERR:\n{result.stderr}\n\n"
                f"STDOUT:\n{result.stdout}"
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
                f"{step['name']}\n\n{result.stderr}"
            )

    duration = perf_counter() - start_time
    return duration

# ==================================================
# Run Batch Pipeline
# ==================================================

def run_batch_pipeline(
    deployments,
    skip_completed=False,
    progress_callback=None
):
    """
    Run the full pipeline for multiple deployments.
    Returns a dict of deployment: duration.
    """

    results   = {}
    start_time = perf_counter()

    for deployment in deployments:

        if progress_callback:
            progress_callback(
                deployment=deployment,
                message=f"Starting {deployment}"
            )

        try:
            duration = run_pipeline(
                deployment=deployment,
                skip_completed=skip_completed,
                progress_callback=lambda c, t, s: (
                    progress_callback(
                        deployment=deployment,
                        message=s
                    )
                    if progress_callback else None
                )
            )

            results[deployment] = {
                "status":   "done",
                "duration": duration
            }

        except Exception as error:
            results[deployment] = {
                "status": "failed",
                "error":  str(error)
            }

    return results