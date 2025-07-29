import os
import re
import json
import csv
from datetime import datetime

# Directory containing extracted PDF JSONs
EXTRACTED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed", "extracted_text")
DATA_PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
OUTPUT_CSV = os.path.join(DATA_PROCESSED_DIR, "pdf_actor_signatures.csv")
OUTPUT_JSON = os.path.join(DATA_PROCESSED_DIR, "pdf_actor_signatures.json")

# Regex patterns
ROLE_PATTERNS = [
    r"глава [^\n,\r]+",  # e.g. глава администрации города Мариуполя
    r"заместитель [^\n,\r]+",
    r"председатель [^\n,\r]+",
    r"администрация [^\n,\r]+",
    r"исполнитель [^\n,\r]+",
    r"подписал[а]?(?:[^\n\r]{0,50})",  # подписал/подписала
    r"ответственный [^\n,\r]+"
]
# Typical Russian formal name: Фамилия И.О.
NAME_PATTERN = r"[А-ЯЁ][а-яё]+ [А-ЯЁ]\. ?[А-ЯЁ]\."
# Date patterns (dd.mm.yyyy or dd month yyyy)
DATE_PATTERNS = [
    r"\b(\d{2})[.](\d{2})[.](\d{4})\b",
    r"\b(\d{2}) ([а-яё]+) (\d{4})\b"
]
MONTHS_RU = {
    "января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
    "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
}

def extract_dates(text):
    dates = []
    for pat in DATE_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            if len(m.groups()) == 3:
                if "." in m.group(0):
                    # dd.mm.yyyy
                    dates.append(f"{m.group(3)}-{m.group(2)}-{m.group(1)}")
                else:
                    # dd month yyyy
                    month = MONTHS_RU.get(m.group(2).lower(), "??")
                    dates.append(f"{m.group(3)}-{month}-{m.group(1)}")
    return dates

def find_with_context(pattern, text, window=50):
    matches = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        start, end = m.start(), m.end()
        context = text[max(0, start-window):min(len(text), end+window)]
        matches.append({
            "match": m.group(0),
            "context": context.strip()
        })
    return matches

def process_file(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    text = data.get("full_text", "")
    filename = data.get("filename", os.path.basename(json_path))
    meta_date = None
    # Try to extract date from filename (if present)
    date_match = re.search(r"(\d{2})[.](\d{2})[.](\d{4})", filename)
    if date_match:
        meta_date = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
    # Extract roles
    roles = []
    for pat in ROLE_PATTERNS:
        roles.extend(find_with_context(pat, text))
    # Extract names
    names = find_with_context(NAME_PATTERN, text)
    # Extract signature dates
    dates = extract_dates(text)
    return {
        "filename": filename,
        "roles": roles,
        "names": names,
        "signature_dates": dates if dates else ([meta_date] if meta_date else []),
    }

def main():
    results = []
    for fname in os.listdir(EXTRACTED_DIR):
        if not fname.lower().endswith(".json"):
            continue
        fpath = os.path.join(EXTRACTED_DIR, fname)
        try:
            res = process_file(fpath)
            results.append(res)
        except Exception as e:
            print(f"Error processing {fname}: {e}")
    # Write CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "role_match", "role_context", "name_match", "name_context", "signature_dates"])
        for r in results:
            maxlen = max(len(r["roles"]), len(r["names"]))
            for i in range(maxlen):
                role = r["roles"][i] if i < len(r["roles"]) else {"match": "", "context": ""}
                name = r["names"][i] if i < len(r["names"]) else {"match": "", "context": ""}
                writer.writerow([
                    r["filename"],
                    role["match"],
                    role["context"],
                    name["match"],
                    name["context"],
                    ";".join(r["signature_dates"])
                ])
    # Write JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as jf:
        json.dump(results, jf, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
