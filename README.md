# Wildlife Monitoring Pipeline

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pipeline](https://img.shields.io/badge/AI-Pipeline-green)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)


An AI-assisted end-to-end wildlife monitoring system that transforms camera trap images into a structured and review-ready ecological dataset.

---

## Project Overview

This project automates wildlife data processing from raw camera trap images into a final structured dataset using AI models and data engineering workflows.

It is designed to support ecological research by reducing manual image sorting and species identification work.

---

## System Pipeline

```text
Camera Trap
↓
AI Pipeline
↓
Review App
↓
Final Dataset
```

---

## AI Pipeline Workflow

The AI Pipeline includes:

### 1. Data Audit  
   - Validate raw camera trap images and metadata  

### 2. Object Detection (MegaDetector)  
   - Detect animals, humans, and empty frames  
   - Filter relevant wildlife images  

### 3. Detection Dataset Building  
   - Convert detection outputs into structured tables  

### 4. Species Classification (SpeciesNet)  
   - Predict species from detected animals  
   - Generate confidence scores  

### 5. Data Integration  
   - Merge detection + classification results  
   - Extract taxonomy hierarchy (class → species)  

### 6. Processed Dataset Creation  
   - Generate analysis-ready dataset  

---

## Final Output Dataset

The final dataset contains:

### Image Metadata
- image_path
- folder_name
- timestamp
- event sequence

### AI Predictions
- top-1 species prediction
- confidence score
- detection confidence

### Taxonomy
- class
- order
- family
- genus
- species
- common name

### Human Review Layer
- review_status (Pending / Verified / Corrected / Skipped)
- reviewer
- review_notes

---

## Technologies Used

- Python
- pandas
- MegaDetector
- SpeciesNet
- JSON processing
- Data pipeline engineering

---

## Project Structure

```text
wildlife-monitoring-pipeline/
│
├── scripts/
│ ├── 01_data_audit.py
│ ├── 02_run_megadetector.py
│ ├── 03_build_detection_dataset.py
│ ├── 04_run_speciesnet.py
│ └── 05_merge_species_results.py
│
├── outputs/
│ ├── detection/
│ ├── speciesnet/
│ └── processed/ wildlife_dataset.csv
│
└── README.md
```


---

## Key Features

- End-to-end AI wildlife processing pipeline
- Camera trap image automation
- Species classification + taxonomy extraction
- Human-in-the-loop review system
- Structured final dataset for analytics

---

## Status

Active Development

Planned improvements:
- Database integration (PostgreSQL)
- Review web app (Streamlit)
- Fully automated pipeline execution
- Analytics dashboard (Power BI / Python)
- Model evaluation metrics layer

---

## Author Note

This project was built as a self-driven exploration of **AI + environmental data systems**, combining computer vision, data engineering, and ecological workflows into a unified pipeline.

---

## Future Vision

A fully automated wildlife intelligence system:

> From forest camera → to real-time biodiversity insights