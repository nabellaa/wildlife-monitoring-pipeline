import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.deployments import summarize_deployment
from config.paths import get_deployment_paths, OUTPUT_PATH

all_data = []

for deployment_folder in summarize_deployment(OUTPUT_PATH):

    if deployment_folder.name == "master":
        continue

    paths = get_deployment_paths(deployment_folder.name)
    dataset_file = paths["dataset"]

    if not dataset_file.exists():
        continue

    dataset = pd.read_csv(dataset_file)
    all_data.append(dataset)

if not all_data:
    print("No deployment datasets found.")
    sys.exit()

dataset = pd.concat(all_data, ignore_index=True)

print(f"Total rows: {len(dataset)}")
print(f"Columns: {dataset.columns.tolist()}")
print()
print(f"prediction_rank values: {dataset['prediction_rank'].value_counts().to_dict()}")
print()
print(f"Verified rows: {dataset['verified_common_name'].notna().sum()}")
print(f"Prediction rank Species: {(dataset['prediction_rank'] == 'Species').sum()}")
print()
print(f"Sample prediction names:")
print(dataset['prediction_common_name'].dropna().unique()[:10])