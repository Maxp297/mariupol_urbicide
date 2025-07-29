import os
import json
import csv
import re

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STRUCTURED_JSON = os.path.join(PROJECT_ROOT, "data", "processed", "p.1173_structured.json")
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "p.1173_ownerless_table_clean.csv")

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

# Find candidate pairs (row, address)
pairs = []
i = 0
while i < len(lines) - 1:
    row1 = lines[i]
    row2 = lines[i+1]
    # Heuristic: row1 must contain 'г. Мариуполь' and a date, row2 must contain street info
    if ("г. Мариуполь" in row1 and re.search(r"\d{2}\.\d{2}\.\d{4}", row1)):
        pairs.append((row1, row2))
        i += 2
    else:
        i += 1

print(f"Found {len(pairs)} property records.")

# Parse each pair
parsed = []
for idx, (row, addr) in enumerate(pairs):
    # Extract columns from row1
    # Example: '1 квартира г. Мариуполь, 53,0 требует ремонто- | 18.03.2025 | информация отсутствует'
    # Try splitting by | first
    parts = [p.strip() for p in re.split(r'\|', row)]
    # Fallback: split by multiple spaces
    if len(parts) < 3:
        parts = re.split(r'\s{2,}', row)
    # Assign fields
    number = ''
    type_ = ''
    city = ''
    area = ''
    condition = ''
    date = ''
    cadastral = ''
    restoration_status = ''
    # Extract number and type
    m = re.match(r'(\d+)\s+(\S+)', row)
    if m:
        number = m.group(1)
        type_ = m.group(2)
    # Area and condition
    area_match = re.search(r'(\d{2,3}[\.,]\d)', row)
    if area_match:
        area = area_match.group(1)
    # Condition
    if 'требует ремонто-восстановительных работ' in row or 'восстановительных работ' in addr:
        restoration_status = 'требует ремонто-восстановительных работ'
    elif 'требует' in row:
        restoration_status = 'требует ремонта'
    # Date
    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', row)
    if date_match:
        date = date_match.group(1)
    # Cadastral (if present)
    cad_match = re.search(r'(\d{2}:\d{2}:\d{7,}:\d+)', row+addr)
    if cad_match:
        cadastral = cad_match.group(1)
    parsed.append([
        number,
        type_,
        'г. Мариуполь',
        area,
        date,
        addr,
        restoration_status,
        cadastral
    ])

with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["№", "Тип", "Город", "Площадь", "Дата", "Адрес", "Статус восстановления", "Кадастровый номер"])
    writer.writerows(parsed)

print(f"Saved {len(parsed)} rows to {OUTPUT_CSV}")
