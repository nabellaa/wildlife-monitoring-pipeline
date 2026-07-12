# fix path of the output from the google collab to match the current pipeline
import sys
import json
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: python fix_colab_paths.py <deployment_name> <local_project_root>")
    sys.exit(1)

deployment = sys.argv[1]
new_prefix = sys.argv[2]  # e.g. C:\Users\SCSM11\Documents\wildlife-monitoring-pipeline

old_prefix = "/content/wildlife-monitoring-pipeline"

md_path = Path(f"outputs/deployments/{deployment}/megadetector/megadetector_results.json")
with open(md_path, "r", encoding="utf-8") as f:
    md_data = json.load(f)
for item in md_data:
    item["file"] = item["file"].replace(old_prefix, new_prefix).replace("/", "\\")
with open(md_path, "w", encoding="utf-8") as f:
    json.dump(md_data, f, indent=2)

sn_path = Path(f"outputs/deployments/{deployment}/speciesnet/speciesnet_results.json")
with open(sn_path, "r", encoding="utf-8") as f:
    sn_data = json.load(f)
for item in sn_data.get("predictions", []):
    if "filepath" in item:
        item["filepath"] = item["filepath"].replace(old_prefix, new_prefix).replace("/", "\\")
with open(sn_path, "w", encoding="utf-8") as f:
    json.dump(sn_data, f, indent=2)

print(f"Paths fixed for {deployment} — pointed at {new_prefix}")