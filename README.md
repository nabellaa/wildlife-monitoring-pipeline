# Wildlife Monitoring Pipeline

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pipeline](https://img.shields.io/badge/AI-Pipeline-green)
![Status](https://img.shields.io/badge/Status-90%25%20Complete-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

An AI-assisted end-to-end wildlife monitoring system that transforms camera trap images into a structured, review-ready, and analytics-ready ecological dataset.

Built on real fieldwork data — **~86,000 camera trap images** collected over **187 days across 4 sites** at Mount Khantan, Perak, Malaysia.

---

## Project Overview

This system processes wildlife camera trap images through:

- AI detection (MegaDetector) + species classification (SpeciesNet)
- Human-in-the-loop verification via Streamlit review interface
- Full audit trail (review logs, undo system, session backup)
- Multi-deployment dataset management
- Master dataset + clean dataset generation
- Analytics-ready ecological data pipeline

Designed for **scalable biodiversity monitoring across multiple locations and deployments**.

---

## App Preview

### Deployment and Pipeline Runner
![Deployment and Pipeline Runner](docs/images/deployment_pipeline.png)

### Folder Information and Event Queue
![Folder Information and Event Queue](docs/images/info_review_queue.png)

### Review Interface
![Review Interface](docs/images/review_interface.png)

### AI Prediction Information
![AI Prediction Information](docs/images/ai_prediction_info.png)

---

# System Architecture

The system is built in **three main layers**:

---

## 1. Deployment Layer (Per-Experiment Processing)

Each deployment is an independent, reproducible processing unit.

### Features:
- Raw image processing
- Detection + classification pipeline
- Human-in-the-loop review system
- Independent logs, backups, and session state per deployment

### Structure:
```text
deployments/
├── deployment_01/
├── deployment_02/
├── deployment_03/
```

---

## 2. Master Dataset Layer (Aggregation Layer)

All deployments are merged into a single unified dataset.

### Responsibilities:
- Combine all deployment outputs
- Standardize schema across runs
- Add deployment metadata
- Ensure cross-experiment consistency

### Output:
- `master_dataset_raw.csv`

---

## 3. Clean Dataset Layer (Intelligence Layer)

Final curated dataset for analytics and dashboards.

### Responsibilities:
- Taxonomy normalization and species name standardization
- Review reconciliation and duplicate handling
- Final ground-truth dataset generation

### Output:
- `clean_dataset.csv`

---

# System Pipeline Flow

```text
Camera Trap Images
        ↓
script01_audit.py              — Validate images and metadata
        ↓
script02_run_megadetector.py   — Object detection (animal/human/vehicle/empty)
        ↓
script03_build_detection.py    — Build structured detection dataset
        ↓
script04_run_speciesnet.py     — Species classification + confidence scoring
        ↓
script05_merge_species_results.py  — Merge detection + classification outputs
        ↓
script06_build_review_queue.py — Flag low-confidence and unknown predictions
        ↓
wildlife_monitor.py            — Streamlit human-in-the-loop review UI
        ↓
script08_backup_manager.py     — Session backup and state management
        ↓
script09_build_master_dataset.py   — Aggregate all deployments into master dataset
        ↓
Clean Dataset Generation       — Final analytics-ready output
```

---

# Project Structure

```text
config/
├── deployment.py              — Deployment configuration
├── paths.py                   — Path management

app/
├── wildlife_monitor.py        — Streamlit review interface (main UI)

scripts/
├── script01_audit.py
├── script02_run_megadetector.py
├── script03_build_detection.py
├── script04_run_speciesnet.py
├── script05_merge_species_results.py
├── script06_build_review_queue.py
├── script08_backup_manager.py
├── script09_build_master_dataset.py
├── species_lookup.py          ⭐ In progress — IUCN + taxonomy enrichment
├── pipeline_runner.py         — Central pipeline execution controller
```

---

# AI Pipeline Workflow

### 1. Data Audit
- Validate raw camera trap images, folder structure, and metadata consistency

### 2. Object Detection (MegaDetector)
- Detect animals, humans, vehicles, and empty frames
- Produce bounding boxes and confidence scores per image

### 3. Detection Dataset Building
- Convert MegaDetector JSON outputs into structured tabular dataset
- Standardize event-based format (event_id, image mapping)

### 4. Species Classification (SpeciesNet)
- Predict species from detected wildlife images
- Generate predicted species (common name), confidence score, and full taxonomy (class → order → family → genus → species)
- Flag low-confidence and unknown predictions for human review

### 5. Data Integration
- Merge MegaDetector detection output with SpeciesNet classification results
- Build unified single-source-of-truth dataset per deployment

### 6. Review Queue Generation
- Filter cases requiring human attention:
  - Unknown species
  - Low-confidence predictions
  - Conflicting AI outputs
- Prioritize images for manual verification

### 7. Human-in-the-Loop Review System (Streamlit)
- Species verification dropdown with dynamic "Other…" custom input
- Event-based image navigation with bounding box overlay
- Session-based undo stack — snapshot before every change, safe rollback
- Full dataset backup per session
- Dynamic species dictionary — auto-updates as new species are added during review

### 8. Review Logging
- Tracks every review action:
  - Original AI prediction
  - Human correction
  - Timestamp and event_id
- Enables complete audit trail of all verification decisions

### 9. Master Dataset Builder
- Aggregates all reviewed deployment outputs into a unified master dataset
- Standardizes schema and adds deployment metadata across runs

### 10. Clean Dataset Output
- Final analysis-ready dataset after taxonomy normalization, deduplication, and review reconciliation

---

# Final Output Dataset

### Image Metadata
- `image_path`, `file_name`, `folder_name`
- `capture_datetime`, `temperature_c`, `moon_phase`
- `event_number`, `sequence`

### AI Predictions
- `prediction_class`, `prediction_species`, `prediction_common_name`, `prediction_score`

### Classifier Output
- `classifier_species`, `classifier_common_name`, `classifier_score`

### Taxonomy
- `class`, `order`, `family`, `genus`, `species`, `common_name`

### Human Review Layer
- `review_status` (Pending / Verified / Corrected / Skipped)
- `review_required`, `verified_common_name`
- `reviewer`, `review_notes`, `review_timestamp`

---

# Technologies Used

| Category | Tools |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas, JSON |
| AI Models | MegaDetector (object detection), SpeciesNet (species classification) |
| Review Interface | Streamlit |
| Pipeline Orchestration | pipeline_runner.py (modular script controller) |
| Data Engineering | ETL pipeline, session state management, audit logging |

---

# Current Development Status

```
██████████████████░░  90%
```

### ✅ Completed
- Data audit layer
- MegaDetector detection pipeline
- SpeciesNet classification pipeline
- Detection dataset builder
- Merge results layer
- Review queue system
- Streamlit review interface
- Undo system (session-based snapshot rollback)
- Backup system (per-session dataset + log backup)
- Review log system (full audit trail)
- Pipeline runner (central execution controller)
- Session state management
- Dynamic species dictionary (auto-growing)
- Multi-deployment support
- Master dataset builder (script09)
- Clean dataset generation

### 🟡 In Progress
- `species_lookup.py` — automatic taxonomy enrichment (IUCN status, population level, full taxonomy auto-fill for new species)

### 🔜 Next Phase — Intelligence Layer
**Dashboard** (Power BI / Python):
- Overall statistics
- Deployment summary
- Species distribution analysis
- Confidence scoring trends
- Review performance metrics

**Admin Panel** (Streamlit):
- Species dictionary management
- Backup management system
- Review logs explorer
- System monitoring

**Data Enrichment**:
- Integration of camera site data (coordinates, habitat type, environment)
- GIS spatial analysis layer

---

## Author Note

This project was built as a self-driven exploration of **AI + environmental data systems**, combining computer vision, data engineering, and ecological fieldwork into a unified analytics pipeline.

The dataset is real — collected during conservation biology fieldwork at **Mount Khantan, Perak, Malaysia** over 187 days across 4 camera trap sites.

---

## Future Vision

A fully automated wildlife intelligence system:

> From forest camera → to real-time biodiversity insights