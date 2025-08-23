import os
import json
import csv
import re
from config import PROJECT_ROOT

STRUCTURED_JSON = os.path.join(PROJECT_ROOT, "data", "processed", "p.1173_structured.json")
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "p.1173_ownerless_table.csv")

with open(STRUCTURED_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

full_text = data["full_text"]

# Locate the start of the table section
header_pattern = r"РЕЕСТР[\s\S]{0,200}кадастровый номер"
header_match = re.search(header_pattern, full_text, re.IGNORECASE)

if not header_match:
    print("Could not find table header.")
    exit(1)

table_start = header_match.end()
table_text = full_text[table_start:]

# Split into lines and filter out empty/noise lines
lines = [l.strip() for l in table_text.split('\n') if l.strip()]

# Heuristic: Table rows often contain numbers, address fragments, and area/condition/date/cadastral fields
rows = []
for line in lines:
    # Stop if we hit the end of the table (next decree, signature, or appendix)
    if re.search(r'(Приложение|Глава|\bАдминистрация\b|^$)', line):
        break
    # Only keep lines with enough fields (tune as needed)
    if len(re.findall(r'\d', line)) >= 2:
        rows.append(line)

# Interactive parsing
print(f"Found {len(rows)} candidate table rows.\n")
print("Columns: [№, Наименование, Адрес, Площадь, Состояние, Дата, Кадастровый номер]")

parsed = []
for i, row in enumerate(rows):
    print(f"\nRow {i+1}: {row}")
    # Try to split by |, tab, or multiple spaces
    fields = re.split(r'\s*[|\t]+\s*|\s{2,}', row)
    # Pad/truncate to 7 columns
    while len(fields) < 7:
        fields.append("")
    if len(fields) > 7:
        fields = fields[:7]
    print("Parsed fields:")
    for j, f in enumerate(fields):
        print(f"  {j+1}. {f}")
    # User correction
    user = input("Press Enter to accept, or enter comma-separated corrections (or 'q' to quit): ")
    if user.strip().lower() == 'q':
        break
    if user.strip():
        parts = [x.strip() for x in user.split(",")]
        for idx, val in enumerate(parts):
            if idx < 7:
                fields[idx] = val
    parsed.append(fields)

# Write to CSV
with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["№", "Наименование", "Адрес", "Площадь", "Состояние", "Дата", "Кадастровый номер"])
    writer.writerows(parsed)

print(f"\nSaved {len(parsed)} rows to {OUTPUT_CSV}")
