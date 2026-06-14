"""
==================================================
Script: 01_data_audit.py

Purpose:
    Audit the sample camera trap dataset.

Author:
    Bella

Project:
    Wildlife Monitoring Pipeline
==================================================
"""

# ==================================================
# 1. Import Libraries
# ==================================================

from pathlib import Path
from datetime import datetime

# Path is used to work with files and folders.
# We use pathlib because it works on Windows, macOS and Linux.

# ==================================================
# 2. Project Paths
# ==================================================

project_root = Path(__file__).resolve().parent.parent

# __file__ = current Python script
# .resolve() = full absolute path
# .parent.parent = move up two folders to project root

sample_folder = project_root / "data" / "sample" / "REC055_199A"

# Build the path without hardcoding
# C:\Users\Bella\...
# Makes the project portable.

# ==================================================
# 3. Output Paths
# ==================================================

output_folder = project_root / "outputs" / "audit"
output_folder.mkdir(parents=True, exist_ok=True)

report_file = output_folder / "audit_report.txt"

# mkdir() creates the folder if it doesn't exist.
# parents=True  → Create missing parent folders.
# exist_ok=True → Don't raise an error if the folder already exists.

# ==================================================
# 4. Find Photos
# ==================================================

jpg_files = list(sample_folder.glob("*.JPG"))

print(f"Number of JPG files: {len(jpg_files)}")

# glob("*.JPG") finds every JPG file.
# list() stores the results so we can:
# - Count photos
# - Preview photos
# - Loop through them

# ==================================================
# 5. Preview Files
# ==================================================

for photo in jpg_files[:5]:
    print(photo.name)

#[:5] means "show the first 5 items".
# Useful for checking that the correct files
# were loaded before continuing the pipeline.

# ==================================================
# 6. Collect Audit Information
# ==================================================

photo_count = len(jpg_files)
# Count the total number of JPG images found.
# len() returns the number of items inside a list.
# Example:
# [A, B, C]
# len(...) = 3

image_type = jpg_files[0].suffix
# Get the file extension of the first image.
# .suffix returns the extension including the dot.
# Example:
# IMG_0001.JPG
#          ↑
#        .JPG
# Later we can check whether a folder contains
# different image formats.

first_photo = jpg_files[0].name
# Lists start at index 0.
# Therefore:
# jpg_files[0]
# always returns the first image in the list.

last_photo = jpg_files[-1].name
# Python allows negative indexing.
# -1 means the last item in a list.
# Why use -1 instead of [32]?
# Because every folder contains a different number
# of photos.
# This makes the code reusable.

folder_size = sum(photo.stat().st_size for photo in jpg_files)
folder_size_mb = round(folder_size / (1024 ** 2), 2)
# Calculate the total size of all photos.
# photo.stat()
# Returns file information.

# st_size
# Returns the file size in bytes.

# sum(...)
# Adds the size of every image together.

# Finally, convert bytes into megabytes (MB)
# to make the report easier to read.

audit_date = datetime.now().strftime("%Y-%m-%d %H:%M")
# Record when the audit was performed.

# datetime.now()
# Gets the current date and time.

# strftime(...)
# Formats the date into a readable string.
# %Y = Year
# %m = Month
# %d = Day
# %H = Hour (24-hour)
# %M = Minute

# ==================================================
# 7. Create Audit Report
# ==================================================

report = f"""
========================================
Wildlife Monitoring Pipeline
Data Audit Report
========================================

Folder Name : {sample_folder.name}

Folder Exists : {sample_folder.exists()}

Total Photos : {photo_count}

Image Type : {image_type}

First Photo : {first_photo}

Last Photo : {last_photo}

Folder Size : {folder_size_mb:.2f} MB

Audit Date : {audit_date}

========================================
Audit Complete
========================================
"""
# Create the audit report using an f-string.
# An f-string allows Python variables to be inserted
# directly into text using:
# {variable_name}
# This is cleaner than joining many strings together.

# ==================================================
# 8. Save Audit Report
# ==================================================

report_file.write_text(report, encoding="utf-8")
# Save the report as a UTF-8 encoded text file.
# Why UTF-8?
# - Cross-platform compatible.
# - Supports international characters.
# - Supports emojis and special symbols.
# Path.write_text() is a convenient pathlib method
# for writing text files.

# ==================================================
# 9. Display Results
# ==================================================

print(report)
print(f"✓ Report saved to: {report_file}")