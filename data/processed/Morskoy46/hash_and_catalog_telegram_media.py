#!/usr/bin/env python3
# hash_and_catalog_telegram_media.py
# Computes SHA-256 hashes for all Telegram media and updates the metadata CSV.

import os
import hashlib
import pandas as pd
from config import PROJECT_ROOT

# Paths
BASE = f'{PROJECT_ROOT}/data/processed/Morskoy46'
MEDIA_FOLDERS = ['telegram_images_raw', 'telegram_videos_raw', 'telegram_docs_raw']
METADATA_CSV = os.path.join(BASE, 'telegram_media_metadata.csv')
OUTPUT_CSV = os.path.join(BASE, 'telegram_media_metadata_hashed.csv')

# Hashing function
def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

# Load metadata
meta = pd.read_csv(METADATA_CSV)
meta['sha256'] = ''

# Build map: absolute filepath -> hash
for folder in MEDIA_FOLDERS:
    folder_path = os.path.join(BASE, folder)
    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if os.path.isfile(fpath):
            # Find matching row(s) in metadata
            rel_path = fpath  # stored as absolute in metadata
            matches = meta['file_path'] == fpath
            if matches.any():
                file_hash = sha256sum(fpath)
                meta.loc[matches, 'sha256'] = file_hash

# Save new catalog
meta.to_csv(OUTPUT_CSV, index=False)
print(f"Hashed and updated metadata saved to {OUTPUT_CSV}")
