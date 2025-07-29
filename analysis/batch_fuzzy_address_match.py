import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz, process
import re

def normalize_addr(addr):
    if pd.isna(addr):
        return ''
    addr = addr.lower()
    addr = addr.replace('.', '')
    addr = re.sub(r'\s+', ' ', addr)
    addr = addr.replace(' ,', ',').replace(', ', ',')
    addr = addr.replace('д ', 'д').replace('кв ', 'кв')
    addr = addr.replace('д,', 'д').replace('кв,', 'кв')
    addr = addr.replace(' ,', ',').replace(',,', ',')
    addr = addr.strip(' ,')
    return addr

def main():
    project_root = Path(__file__).parent.parent
    gosu_path = project_root / 'data' / 'processed' / 'unique_gosuslugi_addresses_normalized.txt'
    seized_path = project_root / 'data' / 'processed' / 'seized_properties_combined.csv'
    out_path = project_root / 'data' / 'processed' / 'gosuslugi_seized_fuzzy_matches.csv'

    # Load Gosuslugi addresses
    with open(gosu_path, encoding='utf-8') as f:
        gosu_addrs = [normalize_addr(line.strip()) for line in f if line.strip()]

    # Load seized properties
    df = pd.read_csv(seized_path, dtype=str)
    df['all_addr_norm'] = df['orig_address_ru'].apply(normalize_addr)

    results = []
    for addr in gosu_addrs:
        match, score, idx = process.extractOne(addr, df['all_addr_norm'], scorer=fuzz.token_sort_ratio)
        row = df.iloc[idx]
        results.append({
            'gosuslugi_address': addr,
            'matched_seized_address': row['orig_address_ru'],
            'match_score': score,
            'lat': row.get('lat', ''),
            'lon': row.get('lon', ''),
            'seized_fid': row.get('fid', ''),
            'seized_source': row.get('source', ''),
        })
    pd.DataFrame(results).to_csv(out_path, index=False)
    print(f"Wrote fuzzy matches for {len(results)} addresses to {out_path}")

if __name__ == '__main__':
    main()
