import os
import hashlib
import json
import csv
from datetime import datetime

# Set up paths
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "downloaded_pdfs")
LINKS_JSON = os.path.join(PROJECT_ROOT, "data", "raw", "mariupol_pdf_links.json")
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "pdf_metadata.csv")
OUT_JSON = os.path.join(PROJECT_ROOT, "data", "processed", "pdf_metadata.json")

os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)

# Load URL mapping
with open(LINKS_JSON, "r", encoding="utf-8") as f:
    links = json.load(f)

# Build mapping: filename -> {pdf_url, parent_page, link_text}
url_map = {}
for entry in links:
    fname = os.path.basename(entry["pdf_url"])
    url_map[fname] = {
        "pdf_url": entry.get("pdf_url"),
        "parent_page": entry.get("parent_page"),
        "link_text": entry.get("link_text"),
    }

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

records = []
for fname in sorted(os.listdir(DOWNLOAD_DIR)):
    if not fname.lower().endswith(".pdf"):
        continue
    abs_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, fname))
    file_size = os.path.getsize(abs_path)
    mtime = os.path.getmtime(abs_path)
    last_modified = datetime.fromtimestamp(mtime).isoformat()
    sha256 = sha256_file(abs_path)
    url_info = url_map.get(fname, {})
    record = {
        "filename": fname,
        "absolute_path": abs_path,
        "sha256": sha256,
        "file_size_bytes": file_size,
        "last_modified": last_modified,
        "pdf_url": url_info.get("pdf_url", ""),
        "parent_page": url_info.get("parent_page", ""),
        "link_text": url_info.get("link_text", ""),
    }
    records.append(record)

# Write CSV
with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

# Write JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Metadata for {len(records)} PDFs written to {OUT_CSV} and {OUT_JSON}")