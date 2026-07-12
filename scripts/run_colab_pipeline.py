# ==================================================
# Wildlife Monitoring Pipeline
# Colab Pipeline Runner
#
# Runs MegaDetector + SpeciesNet in Colab, then
# patches the output JSON file paths so they point
# at your local machine instead of the Colab VM.
#
# Usage (in a Colab cell):
#   !python scripts/run_colab_pipeline.py <deployment> "<local_project_root>"
#
# Example:
#   !python scripts/run_colab_pipeline.py July-1 "C:\Users\SCSM11\Documents\wildlife-monitoring-pipeline"
# ==================================================

import subprocess
import sys
from pathlib import Path
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import get_deployment_paths

# ==================================================
# Args
# ==================================================

if len(sys.argv) < 3:
    print("Usage: python scripts/run_colab_pipeline.py <deployment> <local_project_root>")
    print(r'Example: python scripts/run_colab_pipeline.py July-1 "C:\Users\SCSM11\Documents\wildlife-monitoring-pipeline"')
    sys.exit(1)

deployment       = sys.argv[1]
local_project_root = sys.argv[2]

paths = get_deployment_paths(deployment, create_folders=True)

# ==================================================
# Pipeline Steps (Colab: script01 + script02 + path fix only)
# ==================================================

pipeline = [
    {
        "script": "script01_run_megadetector.py",
        "name":   "Running MegaDetector",
        "args":   [deployment],
        "output": paths["megadetector_json"]
    },
    {
        "script": "script02_run_speciesnet.py",
        "name":   "Running SpeciesNet",
        "args":   [deployment],
        "output": paths["speciesnet_json"]
    },
    {
        "script": "fix_colab_paths.py",
        "name":   "Fixing Colab paths for local use",
        "args":   [deployment, local_project_root],
        "output": None  # patches existing files, doesn't create a new one
    }
]

# ==================================================
# Run
# ==================================================

def run_colab_pipeline():

    total_steps = len(pipeline)
    start_time  = perf_counter()

    for index, step in enumerate(pipeline):

        script_path = PROJECT_ROOT / "scripts" / step["script"]

        print()
        print("=" * 50)
        print(f"Step {index + 1}/{total_steps}: {step['name']}")
        print("=" * 50)

        result = subprocess.run(
            [sys.executable, str(script_path), *step["args"]],
            cwd=PROJECT_ROOT,
            capture_output=False,  # stream output live in Colab
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Step Failed: {step['name']}\n"
                f"Script: {step['script']}\n"
                f"Deployment: {deployment}"
            )

    duration = perf_counter() - start_time

    print()
    print("=" * 50)
    print("Colab Pipeline Complete")
    print("=" * 50)
    print(f"Deployment : {deployment}")
    print(f"Duration   : {duration:.1f}s")
    print(f"MegaDetector JSON : {paths['megadetector_json']}")
    print(f"SpeciesNet JSON   : {paths['speciesnet_json']}")
    print()
    print("Both JSON files now use local Windows paths.")
    print("Ready to download / copy to Drive.")

    return duration


if __name__ == "__main__":
    run_colab_pipeline()
