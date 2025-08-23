import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re
import json
import csv
from rapidfuzz import process, fuzz
from config import PROJECT_ROOT

# Set up paths
PDF_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "downloaded_pdfs")
METADATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "pdf_metadata.json")
EXTRACTED_TEXT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "extracted_text")
SUMMARY_JSON = os.path.join(PROJECT_ROOT, "data", "processed", "all_pdfs_structured_summary.json")
SUMMARY_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "all_pdfs_structured_summary.csv")
GEOJSON_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "seized_properties_combined.geojson")

os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)

# Load metadata
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_map = {entry["filename"]: entry for entry in json.load(f)}

# Load normalized/geocoded addresses from GeoJSON
with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)
address_lookup = []
for feature in geojson_data["features"]:
    props = feature["properties"]
    address_lookup.append({
        "orig_address_ru": props.get("orig_address_ru", ""),
        "address_ua": props.get("address_ua", ""),
        "lat": props.get("lat"),
        "lon": props.get("lon"),
        "street_norm": props.get("street_norm"),
        "housenumber_norm": props.get("housenumber_norm"),
        "source": props.get("source"),
        "geometry": feature.get("geometry")
    })
address_strings = [a["orig_address_ru"] for a in address_lookup]

def extract_text(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    # OCR fallback with rotation
                    img = page.to_image(resolution=300).original
                    for angle in [0, 90, 180, 270]:
                        rotated = img.rotate(angle, expand=True)
                        ocr_text = pytesseract.image_to_string(rotated, lang="rus+eng")
                        if ocr_text.strip():
                            text += ocr_text + "\n"
                            break
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def parse_structured_fields(text):
    # Example patterns, refine as needed
    addresses = re.findall(r"г\.?\s*Мариупол[^\n,]*[,][^\n]+", text)
    cadastral_numbers = re.findall(r"\d{2}:\d{2}:\d{6,7}:\d{1,4}", text)
    return {
        "addresses": addresses,
        "cadastral_numbers": cadastral_numbers
    }

def enrich_addresses(addresses):
    enriched = []
    for addr in addresses:
        match, score, idx = process.extractOne(
            addr, address_strings, scorer=fuzz.token_sort_ratio
        )
        if score >= 85:
            geo = address_lookup[idx]
            enriched.append({
                "raw_extracted": addr,
                "matched_address_ru": geo["orig_address_ru"],
                "matched_score": score,
                "address_ua": geo["address_ua"],
                "lat": geo["lat"],
                "lon": geo["lon"],
                "street_norm": geo["street_norm"],
                "housenumber_norm": geo["housenumber_norm"],
                "source": geo["source"],
                "geometry": geo["geometry"]
            })
        else:
            enriched.append({
                "raw_extracted": addr,
                "matched_address_ru": None,
                "matched_score": score
            })
    return enriched

summary = []
errors = []

for fname in os.listdir(PDF_DIR):
    if not fname.lower().endswith(".pdf"):
        continue
    extracted_json_path = os.path.join(EXTRACTED_TEXT_DIR, f"{fname}.json")
    if os.path.exists(extracted_json_path):
        print(f"Skipping {fname} (already processed)")
        # Optionally, load summary info from existing JSON for summary regeneration
        with open(extracted_json_path, "r", encoding="utf-8") as f:
            result = json.load(f)
        summary.append({
            "filename": fname,
            "addresses": result.get("addresses", []),
            "cadastral_numbers": result.get("cadastral_numbers", []),
            **result.get("metadata", {})
        })
        continue
    pdf_path = os.path.join(PDF_DIR, fname)
    print(f"Processing {fname} ...")
    text = extract_text(pdf_path)
    if not text.strip():
        errors.append(fname)
        continue
    structured = parse_structured_fields(text)
    enriched_addresses = enrich_addresses(structured["addresses"])
    meta = metadata_map.get(fname, {})
    result = {
        "filename": fname,
        "full_text": text,
        "addresses": enriched_addresses,
        "cadastral_numbers": structured["cadastral_numbers"],
        "metadata": meta
    }
    # Write per-PDF JSON
    with open(extracted_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    # Prepare summary (without full text)
    summary.append({
        "filename": fname,
        "addresses": enriched_addresses,
        "cadastral_numbers": structured["cadastral_numbers"],
        **meta
    })

# Write summary JSON
with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

# Write summary CSV (flatten addresses for CSV)
if summary:
    keys = list(summary[0].keys())
    # Flatten addresses for CSV readability
    for entry in summary:
        entry["addresses_flat"] = "; ".join(
            [a.get("matched_address_ru") or a.get("raw_extracted") for a in entry.get("addresses", [])]
        )
        # Remove the original 'addresses' field for CSV output
        if "addresses" in entry:
            del entry["addresses"]
    if "addresses" in keys:
        keys.remove("addresses")
    if "addresses_flat" not in keys:
        keys.append("addresses_flat")
    # Always write the CSV after flattening
    with open(SUMMARY_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(summary)

if errors:
    print("Extraction failed for the following files:", errors)
