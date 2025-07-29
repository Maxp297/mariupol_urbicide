#!/usr/bin/env python3
"""
Deduplication audit for Mariupol PDF downloads.
Compares mariupol_pdf_links.json to files in data/raw/downloaded_pdfs/ to identify lost/overwritten PDFs due to non-unique filenames.
Outputs a CSV with all URLs, expected filenames, and whether each is present or lost (overwritten).
"""
import os
import json
import hashlib
import csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_JSON = os.path.join(PROJECT_ROOT, 'data', 'raw', 'mariupol_pdf_links.json')
PDF_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw', 'downloaded_pdfs')
OUT_CSV = os.path.join(PROJECT_ROOT, 'analysis', 'deduplication_audit.csv')

with open(LINKS_JSON, 'r', encoding='utf-8') as f:
    links = json.load(f)

# Build expected filename mapping (current logic: os.path.basename(url))
filename_map = {}
for entry in links:
    url = entry['pdf_url']
    fname = os.path.basename(url)
    if fname not in filename_map:
        filename_map[fname] = []
    filename_map[fname].append(url)

# List all files in PDF_DIR
existing_files = set(os.listdir(PDF_DIR))

# Audit: for each URL, check if its basename exists and if there are duplicates
rows = []
for fname, urls in filename_map.items():
    present = fname in existing_files
    status = 'present' if present else 'missing/overwritten'
    for url in urls:
        rows.append({
            'url': url,
            'expected_filename': fname,
            'present': present,
            'status': status,
            'num_urls_with_this_name': len(urls)
        })

with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Deduplication audit complete. Results written to {OUT_CSV}")
