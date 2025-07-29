import csv
import pandas as pd

# Path to your input and output files
INPUT_CSV = 'analysis/damage_assessment_with_features.csv'
OUTPUT_CSV = 'analysis/damage_assessment_with_features_normalized.csv'

# List of possible address-like columns (adjust as needed)
# We'll search for the column containing the full address string
ADDRESS_COLUMN_CANDIDATES = [
    'address', 'full_address', 'building_address', 'Адрес', 'адрес',
]

def normalize_address(addr):
    """
    Normalize a single address string: strip, lower, remove extra spaces, standardize commas, etc.
    """
    if not isinstance(addr, str):
        return ''
    addr = addr.lower().strip()
    addr = ' '.join(addr.split())
    addr = addr.replace(' ,', ',').replace(', ', ',').replace(' , ', ',')
    # Remove leading/trailing commas
    addr = addr.strip(',')
    return addr

# Robustly parse the CSV and collect all rows
with open(INPUT_CSV, encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Try to auto-detect the address column
address_col_idx = None
for candidate in ADDRESS_COLUMN_CANDIDATES:
    if candidate in header:
        address_col_idx = header.index(candidate)
        break
if address_col_idx is None:
    # Fallback: find the first column containing 'бульвар Комсомольский' or similar in any row
    for i, cell in enumerate(header):
        for row in rows:
            if 'бульвар комсомольский' in row[i].lower():
                address_col_idx = i
                break
        if address_col_idx is not None:
            break
if address_col_idx is None:
    raise Exception('Could not auto-detect address column. Please specify manually.')

# Normalize all addresses
normalized_addresses = [normalize_address(row[address_col_idx]) for row in rows]

# Write output as a new DataFrame with normalized address column
out_header = header + ['address_normalized']
out_rows = [row + [norm_addr] for row, norm_addr in zip(rows, normalized_addresses)]
df_out = pd.DataFrame(out_rows, columns=out_header)
df_out.to_csv(OUTPUT_CSV, index=False)
print(f"Exported {len(df_out)} rows with normalized addresses to {OUTPUT_CSV}")
