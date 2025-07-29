import pandas as pd
import re
from pathlib import Path

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
    fuzzy_path = project_root / 'data' / 'processed' / 'gosuslugi_seized_fuzzy_matches.csv'
    seized_path = project_root / 'data' / 'processed' / 'seized_properties_combined.csv'
    pdfmeta_path = project_root / 'data' / 'processed' / 'all_pdfs_structured_summary.csv'
    out_path = project_root / 'data' / 'processed' / 'gosuslugi_seized_fuzzy_matches_enriched.csv'

    fuzzy = pd.read_csv(fuzzy_path, dtype=str)
    seized = pd.read_csv(seized_path, dtype=str)
    pdfmeta = pd.read_csv(pdfmeta_path, dtype=str)

    # Normalize address columns for matching
    seized['orig_address_ru_norm'] = seized['orig_address_ru'].apply(normalize_addr)
    pdfmeta['addresses_flat_norm'] = pdfmeta['addresses_flat'].fillna('').apply(lambda s: [normalize_addr(a) for a in re.split(r';+|\n+', s) if a.strip()])

    # For each fuzzy match, find all PDFs mentioning the matched seized address
    enriched = []
    for i, row in fuzzy.iterrows():
        matched_addr = row['matched_seized_address']
        norm_addr = normalize_addr(matched_addr)
        # Find all PDFs where addresses_flat_norm contains norm_addr
        pdfs = pdfmeta[pdfmeta['addresses_flat_norm'].apply(lambda addrs: norm_addr in addrs)]
        pdf_links = pdfs['pdf_url'].tolist()
        pdf_filenames = pdfs['filename'].tolist()
        pdf_sha256 = pdfs['sha256'].tolist()
        pdf_abs = pdfs['absolute_path'].tolist()
        enriched.append({
            **row,
            'pdf_count': len(pdfs),
            'pdf_filenames': ';'.join(pdf_filenames),
            'pdf_urls': ';'.join(pdf_links),
            'pdf_sha256': ';'.join(pdf_sha256),
            'pdf_paths': ';'.join(pdf_abs),
        })
    pd.DataFrame(enriched).to_csv(out_path, index=False)
    print(f"Wrote enriched matches to {out_path}")

if __name__ == '__main__':
    main()
