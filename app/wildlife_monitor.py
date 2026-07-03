# ==================================================
# Wildlife Monitoring Pipeline
# Review App
# ==================================================

"""
Interactive application for reviewing AI wildlife predictions.

Purpose
-------
Load the processed wildlife dataset, display camera trap images,
allow researchers to verify species predictions, and save the
reviewed results back to the dataset.
"""

# ==================================================
# 1. Import Libraries
# ==================================================

# Streamlit builds the interactive review interface.
import streamlit as st

# Pandas loads and updates the wildlife dataset.
import pandas as pd

# Path handles image file locations.
from pathlib import Path
import sys
import subprocess

# for the image detection box
from PIL import Image
from PIL import ImageDraw

# timestamp
from datetime import datetime

import time
from time import perf_counter

# ==================================================
# Custom Styling, make it look pretty
# ==================================================

st.markdown("""
<style>

/* ── Typography & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background-color: #1a1a1a;
}

/* ── Main content block ── */
.block-container {
    padding: 2rem 3rem;
    max-width: 1200px;
}

/* ── App title ── */
h1 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #e8e6e0 !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem !important;
}

/* ── Section headers ── */
h2, h3 {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #666 !important;
    margin-top: 2rem !important;
    margin-bottom: 0.75rem !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #242424 !important;
    border: 1px solid #333 !important;
    border-radius: 10px;
    padding: 1rem 1.25rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #666 !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    color: #e8e6e0 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #666 !important;
}

/* ── Text inputs & textareas ── */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #666 !important;
}

/* ── Tables ── */
[data-testid="stTable"] table {
    border: none !important;
    font-size: 0.85rem !important;
}

[data-testid="stTable"] th {
    background: #242424 !important;
    color: #666 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    border: none !important;
}

[data-testid="stTable"] td {
    border-bottom: 1px solid #2e2e2e !important;
    color: #c8c6c0 !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #2e2e2e !important;
    margin: 1.75rem 0 !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
    background: #242424 !important;
    border: 1px solid #3a3a3a !important;
    color: #c8c6c0 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}

[data-testid="stButton"] button:hover {
    background: #2e2e2e !important;
    border-color: #555 !important;
    color: #c8c6c0 !important;
}

/* ── Save button accent ── */
[data-testid="stButton"]:last-of-type button {
    background: #e8e6e0 !important;
    color: #1a1a1a !important;
    border-color: #e8e6e0 !important;
}

[data-testid="stButton"]:last-of-type button:hover {
    background: #ccc !important;
}

/* ── Info / warning banners ── */
[data-testid="stInfo"] {
    background: #242424 !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 8px !important;
    color: #999 !important;
    font-size: 0.82rem !important;
}

[data-testid="stSuccess"] {
    background: #1a2e1a !important;
    border: 1px solid #2a4a2a !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid #2e2e2e !important;
    border-radius: 8px !important;
    background: #242424 !important;
}

/* ── Caption text ── */
[data-testid="stCaptionContainer"] {
    color: #555 !important;
    font-size: 0.72rem !important;
}

/* ── Image captions ── */
.stImage > div > small {
    font-size: 0.7rem !important;
    color: #555 !important;
    text-align: center !important;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 2. Configuration
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.paths import (
    DICTIONARY_PATH,
    get_deployment_paths
)

# for run pipeline
from scripts.pipeline_runner import run_pipeline, run_pipeline_from 

# Backup Once Per Session
from scripts.script08_backup_manager import create_backup

# pick folder to run pipeline
from config.deployments import (
    get_deployments,
    get_deployment_path
)


# ==================================================
# 4. Configure Review App
# ==================================================

st.set_page_config(page_title="Wildlife Review", layout="wide")

# ==================================================
# 5. App Header
# ==================================================

st.title("Wildlife Review App")

st.write("Review AI predictions and verify wildlife species.")

# ==================================================
# Deployment Selection
# ==================================================

deployments = get_deployments()

if not deployments:
    st.error("No deployment folders found.")
    st.stop()

if "deployment" not in st.session_state:
    st.session_state["deployment"] = deployments[0]

deployment = st.selectbox(
    "Deployment",
    deployments,
    index=deployments.index(
        st.session_state["deployment"]
    )

)

st.session_state["deployment"] = deployment

# ==================================================
# 3. Load Dataset
# ==================================================

paths = get_deployment_paths(deployment)

# because we formerly use this
DATASET_PATH = paths["dataset"]
REVIEW_LOG_PATH = paths["review_log"]

if DATASET_PATH.exists():

    dataset = pd.read_csv(DATASET_PATH)

else:

    dataset = None

    st.info(
        "No processed dataset found.\n\n"
        "Run the pipeline to create one."
    )

species_dict = pd.read_csv(DICTIONARY_PATH)

# ==================================================
# Backup Once Per Session
# ==================================================

if (
    st.session_state.get("backup_deployment")
    != deployment
):

    backup_folder = create_backup(deployment)

    st.session_state["backup_folder"] = backup_folder
    st.session_state["backup_deployment"] = deployment

    st.toast(
        f"Backup created\n{backup_folder.name}"
    )

# ==================================================
# Pipeline Execute
# ==================================================

st.subheader("Pipeline")

with st.expander("Pipeline Options"):

    skip_completed = st.checkbox(
        "Skip completed steps",
        value=False
    )

    reset_queue = st.checkbox( # for quick test processed data only
        "Reset review queue (run from merge step)",
        value=False
    )

    rebuild_dictionary = st.checkbox(
        "Rebuild species dictionary (Developer)",
        value=False,
        help="Rebuilds the species dictionary and repopulates taxonomy from reviewed datasets."
    )

progress_bar = st.progress(0)

status = st.empty()

if st.button("▶ Run Pipeline"):

    def update_progress(current, total, script):
        progress_bar.progress(current / total)
        status.info(f"Processing:\n{script}")
        print(f"[PIPELINE] {current}/{total} - {script}")

    try:

        # Rebuild Species Dictionary (Developer)
        if rebuild_dictionary:
            status.info("Rebuilding Species Dictionary...")
            start = perf_counter()

            for script in [
                "script07_build_dictionary.py",
                "species_lookup.py"
            ]:

                result = subprocess.run(

                    [
                        sys.executable,
                        str(PROJECT_ROOT / "scripts" / script)
                    ],

                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    raise RuntimeError(
                        f"{script}\n\n{result.stderr}"
                    )
            duration = perf_counter() - start

            
        elif reset_queue:
            duration = run_pipeline_from(
                deployment=deployment,
                start_from=5,
                progress_callback=update_progress
            )

        else:
            duration = run_pipeline(
                deployment=deployment,
                skip_completed=skip_completed,
                progress_callback=update_progress
            )

        progress_bar.progress(1.0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        status.success(
            f"✅ Pipeline completed in "
            f"{minutes} min "
            f"{seconds} sec"
        )

        # Reload dataset after pipeline
        if DATASET_PATH.exists():
            dataset = pd.read_csv(DATASET_PATH)
            st.session_state["dataset"] = dataset

        time.sleep(2)

        st.rerun()

    # This will show the real traceback
    except Exception as error:
        import traceback
        # debug ellipsis
        traceback.print_exc()
        st.exception(error)

# ==================================================
# Build Master Dataset
# ==================================================
if st.button("Build Master Dataset"):

    script = (
        PROJECT_ROOT /
        "scripts" /
        "script09_build_master_dataset.py"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(script)
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        st.success(result.stdout)
    else:
        st.error(result.stderr)

# ==================================================
# Review Interface event no deploy
# ==================================================
if dataset is not None:

    # ==================================================
    # 6. Dataset Summary
    # ==================================================
    st.divider()

    total_images = len(dataset)
    review_required = dataset["review_required"].sum()
    reviewed = (dataset["review_status"] == "Reviewed").sum()

    # ==================================================
    # 7. Display summary metrics in columns.
    # ==================================================

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Images", total_images)
    col2.metric("Review Required", review_required)
    col3.metric("Reviewed", reviewed)

    # Divider
    st.divider()

    # ==================================================
    # 9. Review Queue
    # ==================================================

    review_queue = (
        dataset[dataset["review_required"]]
        ["event_id"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    # Review Progress
    st.subheader(f"Queue — {len(review_queue)} remaining")

    # Check Remaining Reviews
    if not review_queue :
        st.balloons()
        st.success("All events reviewed.")
        st.stop()

    # ==================================================
    # initialise all session state here, before anything else to avoid indentation error
    # ==================================================

    if "view_event" not in st.session_state:
        st.session_state["view_event"] = None

    if "review_event" not in st.session_state:
        st.session_state["review_event"] = None

    if "last_review_event" not in st.session_state:
        st.session_state["last_review_event"] = None

    if "reviewer" not in st.session_state:
        st.session_state["reviewer"] = ""

    if "review_saved" not in st.session_state:
        st.session_state["review_saved"] = False

    if "undo_stack" not in st.session_state:
        st.session_state["undo_stack"] = []

    # ==================================================
    # Create Review Event
    # ==================================================

    # Make sure selected event still exists
    if (
        st.session_state["review_event"] not in review_queue
    ):
        st.session_state["review_event"] = review_queue[0]

    review_event = st.selectbox(
        "Select Event to Review",
        review_queue,
        index=review_queue.index(
            st.session_state["review_event"]
        )
    )

    # Update review target
    st.session_state["review_event"] = review_event

    # Only reset image when the review target changes
    if (
        st.session_state.get("last_review_event")
        != review_event
    ):
        st.session_state["view_event"] = review_event
        st.session_state["last_review_event"] = review_event

    # Two separate sources of truth
    active_event = st.session_state["view_event"]   # what's displayed
    review_event_target = review_event               # what gets saved

    event_data = dataset[dataset["event_id"] == active_event].copy()
    event = event_data.iloc[0]

    st.caption(
        "ℹ️ Species suggestions are loaded from the shared species dictionary when the application starts. "
        "If multiple reviewers are working at the same time, refresh the page to load newly added species."
    ) 

    st.divider()

    # ==================================================
    # Two-column layout: info (left) | actions (right)
    # ==================================================

    col_photo, col_action = st.columns([3, 2], gap="large")

    # ── LEFT: all the read-only context ──────────────
    # BLOCK 5 — Image Display

    with col_photo:

        # BLOCK 6 — Event Context Navigation
        all_events       = sorted(dataset["event_id"].unique())
        current_position = all_events.index(active_event)

        st.subheader("Navigation")

        # button widget
        col_prev, col_next, col_return = st.columns([1, 1, 1])

        with col_prev:
            if current_position > 0 and st.button("← Previous"):
                st.session_state["view_event"] = all_events[current_position - 1]
                st.rerun()

        with col_next:
            if current_position < len(all_events) - 1 and st.button("Next →"):
                st.session_state["view_event"] = all_events[current_position + 1]
                st.rerun()

        with col_return:
            if st.button("Return"):
                st.session_state["view_event"] = review_event_target
                st.rerun()

        # Show Current Event
        if active_event != review_event_target:
            st.info(
                f"Viewing context event **{active_event}**. "
                f"Save will apply to review event **{review_event_target}**."
            )

        st.subheader("Event Images")

        # Draw Bounding Box
        def draw_bbox(image_path, image_row):    
            # If no bounding box exists, show original image.
            if pd.isna(image_row["bbox_x"]):
                return Image.open(image_path)

            # Open image
            image = Image.open(image_path)

            # Get image dimensions
            width, height = image.size

            # Convert normalized coordinates to pixels
            x          = int(image_row["bbox_x"]      * width)
            y          = int(image_row["bbox_y"]      * height)
            box_width  = int(image_row["bbox_width"]  * width)
            box_height = int(image_row["bbox_height"] * height)

            # Draw rectangle
            draw = ImageDraw.Draw(image)
            draw.rectangle(
                [(x, y), (x + box_width, y + box_height)],
                outline="#e85d3a",
                width=4
            )
            return image

        # Display Event Images
        for _, row in event_data.iterrows():
            st.image(
                draw_bbox(row["image_path"], row),
                caption=row["sequence"],
                use_container_width=True
            ) 

    # BLOCK 7 — Verification Panel
    # right
    # ── RIGHT: sticky action panel ───────────────────

    with col_action:

        # Verification    
        st.subheader("Verification")

        # Display species options
        species_options = (
            species_dict["common_name"]
            .dropna()
            .sort_values()
            .tolist()
        )

        # for other option
        species_options.append("Other...")

        # Main selectbox
        verified_common_name = st.selectbox(
            "Select Verified Common Name",
            species_options,
            index=0
        )

        # Handle "Other..." 
        if verified_common_name == "Other...":
            st.info("Species not in dictionary — enter a name below to add it.")
            verified_common_name = st.text_input("Common name")

        # Reviewer (sticky, single source)
        reviewer = st.text_input(
            "Enter Reviewer Name", 
            value=st.session_state["reviewer"],
            key="reviewer_input"
        )
        
        st.session_state["reviewer"] = reviewer
        
        # Notes
        review_notes = st.text_area("Enter Review Notes", height=100)   

        # ==================================================
        # Create Review Log csv
        # ==================================================

        REVIEW_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not REVIEW_LOG_PATH.exists():
            review_log = pd.DataFrame(
                columns=[
                    "timestamp",
                    "event_id",
                    "reviewer",
                    "old_species",
                    "new_species",
                    "review_notes"
                ]
            )

            review_log.to_csv(REVIEW_LOG_PATH, index=False)

        # ==================================================
        # Save Verification
        # ==================================================

        st.divider()

        if st.session_state.get("review_saved", False):
            st.success("Review saved successfully!")
            st.session_state["review_saved"] = False

        # ==================================================
        # Save Button
        # ==================================================
        from scripts.species_lookup import get_species_information
        from scripts.species_lookup import save_species_to_dictionary

        col_save, col_undo = st.columns(2)

        with col_save:

            if st.button("Save Review"): 

                # Reload latest dataset
                dataset = pd.read_csv(DATASET_PATH)
                
                # Store for undo
                log_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                old_row = dataset.loc[dataset["event_id"] == review_event_target].iloc[0]

                # Create Snapshot
                snapshot = {

                    "event_id": review_event_target,

                    "old_species": old_row["verified_common_name"],
                    "old_reviewer": old_row["reviewer"],
                    "old_review_notes": old_row["review_notes"],
                    "old_review_status": old_row["review_status"],
                    "old_review_required": old_row["review_required"],
                    "old_review_timestamp": old_row["review_timestamp"],

                    "new_species": verified_common_name,
                    "new_reviewer": reviewer,
                    "new_review_notes": review_notes,
                    "new_review_status": "Reviewed",
                    "new_review_required": False,
                    "new_review_timestamp": log_timestamp

                }

                st.session_state["undo_stack"].append(snapshot)

                # update dataset
                mask = dataset["event_id"] == review_event_target

                dataset.loc[mask, "verified_common_name"] = verified_common_name
                dataset.loc[mask, "reviewer"] = reviewer
                dataset.loc[mask, "review_notes"] = review_notes
                dataset.loc[mask, "review_status"] = "Reviewed"
                dataset.loc[mask, "review_required"] = False
                dataset.loc[mask, "review_timestamp"] = log_timestamp
                   
                # save CSV 
                dataset.to_csv(DATASET_PATH, index=False)  

                # Save Review Log
                review_log = pd.read_csv(REVIEW_LOG_PATH)

                new_log = pd.DataFrame([{
                    "timestamp":     log_timestamp,
                    "event_id":      review_event_target,        
                    "reviewer":      reviewer,
                    "new_species":   verified_common_name,
                    "review_notes":  review_notes

                }])

                review_log = pd.concat([review_log, new_log], ignore_index=True)
                review_log.to_csv(REVIEW_LOG_PATH, index=False)

                # ==================================================
                # Lookup Verified Taxonomy
                # ==================================================
                current_row = dataset.loc[mask].iloc[0]
                species = get_species_information(verified_common_name, prediction=current_row)
                
                # Always update dataset
                dataset.loc[mask, "scientific_name"] = species["scientific_name"]

                dataset.loc[mask, "taxonomy_class"] = species["taxonomy_class"]
                dataset.loc[mask, "taxonomy_order"] = species["taxonomy_order"]
                dataset.loc[mask, "taxonomy_family"] = species["taxonomy_family"]
                dataset.loc[mask, "taxonomy_genus"] = species["taxonomy_genus"]
                dataset.loc[mask, "taxonomy_species"] = species["taxonomy_species"]
                
                # ==================================================
                # Update Species Dictionary
                # ==================================================
                # Only update dictionary if taxonomy exists
                species_dict = pd.read_csv(DICTIONARY_PATH)

                existing_species = (
                    species_dict["common_name"]
                    .fillna("")
                    .str.strip()
                    .str.lower()
                    .tolist()
                )

                if (
                    verified_common_name.strip().casefold()
                    not in existing_species
                ):

                    # generate species id in the dicitonary 
                    # if else for avoid erorr when delete any
                    if species_dict.empty:
                        next_number = 1

                    else:
                        ids = (
                            species_dict["species_id"]
                            .str.replace("SP", "", regex=False)
                            .astype(int)
                        )

                        next_number = ids.max() + 1

                    next_id = f"SP{next_number:04d}"

                    # Read the verified taxonomy from the dataset 
                    # we just saved
                    new_row = pd.DataFrame([{

                            "species_id": next_id,

                            "common_name": species["common_name"],

                            "scientific_name": species["scientific_name"],

                            "taxonomy_class": species["taxonomy_class"],
                            "taxonomy_order": species["taxonomy_order"],
                            "taxonomy_family": species["taxonomy_family"],
                            "taxonomy_genus": species["taxonomy_genus"],
                            "taxonomy_species": species["taxonomy_species"],

                            "taxonomy_source": species["taxonomy_source"],

                            "status": "Verified"

                        }])
            
                    species_dict = pd.concat(
                        [species_dict, new_row],
                        ignore_index=True
                    )

                    species_dict.to_csv(
                        DICTIONARY_PATH,
                        index=False
                    )
                # ==================================================
                # Save Dataset
                # ==================================================
                
                dataset.to_csv(
                    DATASET_PATH,
                    index=False
                )

                # debug
                # st.write(species)
                # st.stop()

                st.session_state["review_saved"] = True
                st.rerun()        
                
        # ==================================================
        # Undo feature
        # ==================================================
        
        with col_undo:

            if st.session_state.get("undo_stack"):

                if st.button("↩ Undo Review"):

                    last_change = st.session_state["undo_stack"].pop()

                    dataset = pd.read_csv(DATASET_PATH)

                    mask = dataset["event_id"] == last_change["event_id"]

                    dataset.loc[mask, "verified_common_name"] = last_change["old_species"]
                    dataset.loc[mask, "reviewer"] = last_change["old_reviewer"]
                    dataset.loc[mask, "review_notes"] = last_change["old_review_notes"]
                    dataset.loc[mask, "review_status"] = last_change["old_review_status"]
                    dataset.loc[mask, "review_required"] = last_change["old_review_required"]
                    dataset.loc[mask, "review_timestamp"] = last_change["old_review_timestamp"]
                            
                    dataset.to_csv(DATASET_PATH, index=False)

                    st.session_state["view_event"] = last_change["event_id"]            
                    st.session_state["review_event"] = last_change["event_id"]

                    st.success("↩ Undo successful.")
                    st.rerun()

        # ==================================================
        # review saved data
        # ==================================================
        
        st.subheader("Saved Preview")

        if st.session_state["undo_stack"]:

            saved = st.session_state["undo_stack"][-1]

            notes = saved["new_review_notes"].strip()

            st.markdown(f"**Event ID:** `{saved['event_id']}`")
            st.markdown(f"**Species:** `{saved['new_species']}`")
            st.markdown(f"**Reviewer:** `{saved['new_reviewer']}`")
            
            if notes:
                st.markdown(f"**Review Notes:** `{notes}`")
            else:
                st.markdown("**Review Notes:** _No notes added_")

            st.markdown(f"**Time:** `{saved['new_review_timestamp']}`")

        else:
            st.info("No recent changes yet.")
        
    # ==================================================
    # BLOCK 2 — Event Information ---- already shown on photo---
    # ==================================================

    #col1, col2 = st.columns(2)

    #with col1:
    #    st.markdown(f"**Folder** &nbsp; `{event['folder_name']}`")
    #   st.markdown(f"**Event** &nbsp; `{event['event_number']}`")
    #    st.markdown(f"**Captured** &nbsp; `{event['capture_datetime']}`")

    #with col2:
    #    st.markdown(f"**Temperature** &nbsp; `{event['temperature_c']} °C`")
    #    st.markdown(f"**Moon phase** &nbsp; `{event['moon_phase']}`")

    #st.divider()

    # BLOCK 3 AI Prediction Summary
    st.divider()
    # display
    st.subheader("AI Predictions Summary")
    # summarize
    event_predictions = event_data["prediction_common_name"].fillna("")
    # classifier
    event_classifier = event_data["classifier_common_name"].fillna("")
    # remove blanks
    event_predictions = event_predictions[event_predictions != ""]
    classifier_predictions = event_classifier[event_classifier != ""]
    # count predictions
    prediction_counts = event_predictions.value_counts()
    classifier_counts = classifier_predictions.value_counts()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**SpeciesNet Prediciton**")
        st.table(prediction_counts.rename("Images"))

    with col_b:
        st.markdown("**Classifier Prediciton**")
        st.table(classifier_counts.rename("Images"))

    st.divider()

    # BLOCK 4 — display Review Reasons + Confidence

    # Review Reasons
    def get_review_reasons(event_data):
        reasons = []

        # Mixed Species Predictions
        species_predictions = event_data.loc[
            event_data["prediction_rank"] == "Species",
            "prediction_common_name"
        ].dropna().unique()

        if len(species_predictions) > 1:
            reasons.append("Mixed species predictions within event")

        # Incomplete Species Prediction
        if any(event_data["prediction_rank"] != "Species"):
            reasons.append("Incomplete species prediction")

        # Low Confidence
        if any(event_data["prediction_score"] < 0.80):
            reasons.append("Low prediction confidence")

        return reasons

    reasons       = get_review_reasons(event_data)
    average_score = event_data["prediction_score"].mean()

    col_reasons, col_confidence = st.columns(2)

    with col_reasons:
        st.subheader("Review Flags")
        if reasons:
            for reason in reasons:
                st.markdown(f"— {reason}")
        else:
            st.caption("No flags raised.")

    with col_confidence:
        st.subheader("Confidence")
        st.metric("Average Prediction Confidence", f"{average_score:.2%}")
