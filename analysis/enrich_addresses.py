#!/usr/bin/env python3
"""
Enrich seized property addresses with unofficial geocoded data and PDF metadata for forensic mapping.

Inputs:
  - seized_properties_combined.csv (official, normalized/geocoded addresses)
  - mariupol_current_structures.csv (unofficial/prewar geocoded building data)
  - all_pdfs_structured_summary.csv (PDF metadata + extracted addresses)

Output:
  - enriched_seized_properties.csv (official + unofficial + PDF linkage)
  - enriched_seized_properties.json (same as above, for downstream mapping)

Usage:
  python enrich_addresses.py

Author: Cascade AI for forensic mapping, July 2025
"""
import os
import re
import sys
import json
import csv
import pandas as pd
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from config import PROJECT_ROOT

# --- CONFIG ---
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
RAW_PDF_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw', 'downloaded_pdfs')

SEIZED_CSV = os.path.join(PROJECT_ROOT, 'analysis', 'damage_assessment_with_features_normalized.csv')
UNOFFICIAL_CSV = os.path.join(DATA_DIR, 'mariupol_current_structures.csv')
PDF_META_CSV = os.path.join(DATA_DIR, 'all_pdfs_structured_summary.csv')

OUT_CSV = os.path.join(DATA_DIR, 'enriched_seized_properties.csv')
OUT_JSON = os.path.join(DATA_DIR, 'enriched_seized_properties.json')

# --- HELPERS ---
def norm_addr(s):
    if pd.isnull(s):
        return ''
    s = str(s).lower().strip()
    s = re.sub(r'[.,;\s]+', ' ', s)
    s = s.replace('ё', 'е')
    return s

def addr_key(street, number):
    return f"{norm_addr(street)} {norm_addr(number)}".strip()

def fuzzy_match(a, b):
    if not isinstance(a, str) or not isinstance(b, str):
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def find_best_match(addr, candidates, threshold=0.92):
    """Return best (key, row) from candidates if similarity above threshold."""
    best = (None, None, 0)
    for k, row in candidates.items():
        sim = fuzzy_match(addr, k)
        if sim > best[2]:
            best = (k, row, sim)
    return best if best[2] >= threshold else (None, None, 0)

def find_nearest(lat, lon, candidates, max_dist=0.0008):
    # max_dist ~90m (1 deg lat ~111km)
    best = (None, None, float('inf'))
    for k, row in candidates.items():
        try:
            dlat = float(row.get('lat', 0)) - float(lat)
            dlon = float(row.get('lon', 0)) - float(lon)
            dist = (dlat**2 + dlon**2)**0.5
            if dist < best[2]:
                best = (k, row, dist)
        except Exception:
            continue
    return best if best[2] <= max_dist else (None, None, float('inf'))

def pdfs_for_address(addr, pdf_meta_df):
    """Return list of PDF metadata dicts mentioning the address (substring match)."""
    matches = []
    addr_norm = norm_addr(addr)
    for _, row in pdf_meta_df.iterrows():
        addrs_flat = str(row.get('addresses_flat', ''))
        if addr_norm and addr_norm in norm_addr(addrs_flat):
            matches.append({
                'filename': row.get('filename'),
                'pdf_url': row.get('pdf_url'),
                'sha256': row.get('sha256'),
                'absolute_path': row.get('absolute_path'),
                'parent_page': row.get('parent_page'),
                'file_size_bytes': row.get('file_size_bytes'),
                'last_modified': row.get('last_modified'),
            })
    return matches

# --- LOAD DATA ---
print(f"[INFO] Loading input files from {DATA_DIR}")
seized_df = pd.read_csv(SEIZED_CSV, dtype=str)
unofficial_df = pd.read_csv(UNOFFICIAL_CSV, dtype=str)
pdf_meta_df = pd.read_csv(PDF_META_CSV, dtype=str)

# --- BUILD UNOFFICIAL ADDRESS LOOKUP ---
unoff_addr_map = {}
for _, row in unofficial_df.iterrows():
    k = addr_key(row.get('addr:street', ''), row.get('addr:housenumber', ''))
    if k:
        unoff_addr_map[k] = row

# --- ENRICHMENT ---
enriched = []
for idx, row in seized_df.iterrows():
    # Use normalized address for key
    addr_norm = row.get('address_normalized', '')
    # Try direct match in unofficial dataset (normalize as well)
    unoff_row = None
    match_type = 'direct'
    for k, candidate_row in unoff_addr_map.items():
        if addr_norm and addr_norm == norm_addr(k):
            unoff_row = candidate_row
            break
    # Fuzzy match if direct fails
    if not unoff_row:
        # Ensure addr_norm is a string for fuzzy matching
        addr_norm_str = str(addr_norm) if not isinstance(addr_norm, str) else addr_norm
        k, unoff_row, sim = find_best_match(addr_norm_str, unoff_addr_map)
        if unoff_row:
            match_type = f'fuzzy:{sim:.2f}'
    # PDF linkage (by normalized address)
    pdfs = pdfs_for_address(addr_norm, pdf_meta_df)
    # --- Compose enriched row ---
    enriched_row = dict(row)
    if unoff_row:
        for col in unofficial_df.columns:
            enriched_row[f'unoff_{col}'] = unoff_row.get(col, '')
        enriched_row['unoff_match_type'] = match_type
    else:
        for col in unofficial_df.columns:
            enriched_row[f'unoff_{col}'] = ''
        enriched_row['unoff_match_type'] = 'none'
    enriched_row['linked_pdfs'] = json.dumps(pdfs, ensure_ascii=False)
    enriched_row['linked_pdf_count'] = len(pdfs)
    enriched.append(enriched_row)

# --- OUTPUT ---
print(f"[INFO] Writing enriched CSV to {OUT_CSV}")
pd.DataFrame(enriched).to_csv(OUT_CSV, index=False)
print(f"[INFO] Writing enriched JSON to {OUT_JSON}")
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)

print("[DONE] Enrichment complete. Output ready for mapping and forensic analysis.")
