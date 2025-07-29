#!/usr/bin/env python3
"""
build_asset_database.py
Recursively indexes all evidence assets in the project, extracts metadata, and builds/updates a canonical asset database (CSV or SQLite).
"""
import os
import hashlib
import mimetypes
import pandas as pd
from datetime import datetime

import argparse

# CONFIGURATION
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASSET_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed', 'Morskoy46')
DEFAULT_DB_CSV = os.path.join(PROJECT_ROOT, 'data', 'processed', 'Morskoy46', 'asset_database.csv')


# Helper: compute SHA-256 hash for a file (first 1 MB for speed)
def compute_sha256(filepath, blocksize=1024*1024):
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(blocksize)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f'ERROR: {e}'

# Helper: extract asset type from path or filename
def infer_asset_type(path):
    parts = path.lower().split(os.sep)
    if 'facade' in parts or 'building_facade' in path:
        return 'facade_reference'
    elif 'entrance' in path or 'podiezd' in path or 'entrance_breakdown' in path:
        return 'entrance_breakdown'
    elif 'docs' in parts or path.endswith('.pdf'):
        return 'document'
    elif 'map' in parts or path.endswith('.geojson'):
        return 'map'
    elif path.endswith(('.jpg','.jpeg','.png','.bmp','.gif','.webp')):
        return 'image'
    elif path.endswith(('.mp4','.mov','.avi')):
        return 'video'
    else:
        return 'other'

# Helper: extract date from filename (yyyy-mm-dd or yyyymmdd or yyy-mm-dd)
def extract_date(filename):
    import re
    patterns = [r'(\d{4}-\d{2}-\d{2})', r'(\d{8})']
    for p in patterns:
        m = re.search(p, filename)
        if m:
            s = m.group(1)
            if '-' in s:
                return s
            else:
                try:
                    return datetime.strptime(s, '%Y%m%d').strftime('%Y-%m-%d')
                except:
                    continue
    return ''

# Main indexer
def index_assets(asset_dirs, db_csv):
    records = []
    for asset_dir in asset_dirs:
        for root, dirs, files in os.walk(asset_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                relpath = os.path.relpath(fpath, PROJECT_ROOT)
                asset_type = infer_asset_type(relpath)
                sha256 = compute_sha256(fpath)
                size = os.path.getsize(fpath)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
                ext = os.path.splitext(fname)[1].lower()
                mime, _ = mimetypes.guess_type(fpath)
                date = extract_date(fname)
                records.append({
                    'filename': fname,
                    'relative_path': relpath,
                    'asset_type': asset_type,
                    'sha256': sha256,
                    'size_bytes': size,
                    'last_modified': mtime,
                    'file_ext': ext,
                    'mime_type': mime or '',
                    'date': date,
                })
    df = pd.DataFrame(records)
    df.to_csv(db_csv, index=False, encoding='utf-8-sig')
    print(f"Indexed {len(df)} assets. Database saved to {db_csv}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recursively index assets and build a metadata database.')
    parser.add_argument('--root', type=str, default=DEFAULT_ASSET_DIR, help='Root directory to index (default: Morskoy46)')
    parser.add_argument('--output', type=str, default=DEFAULT_DB_CSV, help='Output CSV file (default: asset_database.csv in Morskoy46)')
    args = parser.parse_args()
    asset_dirs = [os.path.abspath(args.root)]
    db_csv = os.path.abspath(args.output)
    index_assets(asset_dirs, db_csv)

