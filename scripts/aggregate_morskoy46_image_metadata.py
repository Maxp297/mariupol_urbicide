import os
import csv
import pandas as pd
from glob import glob
from config import PROJECT_ROOT as BASE_DIR

# --- CONFIGURABLE PATHS ---
CURATED_DIRS = [
    os.path.join(BASE_DIR, "data/processed/Morskoy46/telegram_images_sorted/building_facade_reference/46_only"),
    os.path.join(BASE_DIR, "data/processed/Morskoy46/telegram_images_sorted/building_facade_reference/historical")
]
MEDIA_METADATA_CSV = os.path.join(BASE_DIR, "data/processed/Morskoy46/telegram_media_metadata.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data/processed/Morskoy46/morskoy46_image_metadata_aggregated.csv")

# --- LOAD TELEGRAM MEDIA METADATA ---
media_df = pd.read_csv(MEDIA_METADATA_CSV)
media_df["basename"] = media_df["file_path"].apply(lambda x: os.path.basename(str(x)))
media_df.set_index("basename", inplace=True, drop=False)

# --- SCAN CURATED IMAGE FOLDERS ---
records = []
for category in CURATED_DIRS:
    abs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), category))
    for img_path in glob(os.path.join(abs_dir, "*.jpg")):
        basename = os.path.basename(img_path)
        rel_path = os.path.relpath(img_path, os.path.dirname(__file__))
        # Try to get Telegram metadata
        meta = media_df.loc[basename] if basename in media_df.index else None
        record = {
            "category": os.path.basename(category),
            "filename": basename,
            "relative_path": rel_path,
        }
        # Add Telegram metadata columns if available
        if meta is not None:
            for col in [
                "media_type", "message_id", "date", "sender_id", "caption", "message_link", "file_size", "mime_type", "file_path"
            ]:
                record[col] = meta[col] if col in meta else None
        else:
            for col in [
                "media_type", "message_id", "date", "sender_id", "caption", "message_link", "file_size", "mime_type", "file_path"
            ]:
                record[col] = None
        records.append(record)

# --- OUTPUT AGGREGATED CSV ---
fieldnames = [
    "category", "filename", "relative_path",
    "media_type", "message_id", "date", "sender_id", "caption", "message_link", "file_size", "mime_type", "file_path"
]
with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for rec in records:
        writer.writerow(rec)

print(f"Aggregated metadata for {len(records)} images written to {OUTPUT_CSV}")
