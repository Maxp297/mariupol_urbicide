import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process

# Load core dataset
main = pd.read_csv('data/processed/damage_assessment_clean_en.csv', low_memory=False)



# Load cross-reference assets
seized = pd.read_csv('data/processed/seized_properties_combined.csv', low_memory=False)
ownerless = pd.read_csv('data/processed/p.1173_ownerless_table_clean.csv', low_memory=False)
gosu_fuzzy = pd.read_csv('data/processed/gosuslugi_seized_fuzzy_matches_enriched.csv', low_memory=False)
prewar = pd.read_csv('data/processed/mariupol_prewar_structures.csv', low_memory=False)
current = pd.read_csv('data/processed/mariupol_current_structures.csv', low_memory=False)
actors = pd.read_csv('data/processed/actor_roles_nominative.csv', low_memory=False)
pdf_signatures = pd.read_csv('data/processed/pdf_actor_signatures.csv', low_memory=False)
pdf_metadata = pd.read_csv('data/processed/pdf_metadata.csv', low_memory=False)

# --- 1. Dataset Dissection ---

# Map repair_group to color/severity
repair_map = {
    1: 'Cosmetic Repair (Green)',
    2: 'Current Repair (Light Green)',
    3: 'Major Repair (Yellow)',
    4: 'Demolition (Red)'
}
def map_repair_group(val):
    try:
        return repair_map[int(val)]
    except Exception:
        return 'Unknown'
main['repair_group_label'] = main['repair_group'].apply(map_repair_group)

# Repair group frequency (numeric and label)
repair_group_freq = main['repair_group'].value_counts(dropna=False).sort_index()
repair_group_freq.to_csv('analysis/repair_group_frequency.csv')
repair_group_label_freq = main['repair_group_label'].value_counts(dropna=False)
repair_group_label_freq.to_csv('analysis/repair_group_label_frequency.csv')

# Cross-tabulation: repair_group vs district
crosstab = pd.crosstab(main['district'], main['repair_group_label'])
crosstab.to_csv('analysis/repair_group_by_district.csv')

# Flag and summarize severe cases (group 3 and 4)
severe = main[main['repair_group'].isin([3,4])]
severe.to_csv('analysis/severe_damage_cases.csv', index=False)

# Contractor/Executor network
contractor_network = main.groupby(['contractor', 'responsible_executor']).size().reset_index(name='count')
contractor_network.to_csv('analysis/contractor_executor_network.csv', index=False)

# --- Narrative Extraction: Actionable Features ---
import re

def extract_damage_features(text):
    features = {
        'burned_down': 0,
        'partially_burned': 0,
        'collapse': 0,
        'windows_broken': 0,
        'corpses_present': 0,
        'rubble': 0,
        'roof_destroyed': 0,
        'balcony_destroyed': 0,
        'danger_of_collapse': 0,
        'urgent_clearance': 0,
    }
    if not isinstance(text, str):
        return features
    t = text.lower()
    if 'сгорел полностью' in t or 'burned down' in t:
        features['burned_down'] = 1
    if 'частично сгорел' in t or 'partially burned' in t:
        features['partially_burned'] = 1
    if 'обвал' in t or 'collapsed' in t:
        features['collapse'] = 1
    if 'выбиты окна' in t or 'windows broken' in t:
        features['windows_broken'] = 1
    if 'труп' in t or 'corpse' in t:
        features['corpses_present'] = 1
    if 'уборка территории' in t or 'rubble' in t:
        features['rubble'] = 1
    if 'повреждения кровли' in t or 'roof' in t:
        features['roof_destroyed'] = 1
    if 'балкон' in t or 'balcony' in t:
        features['balcony_destroyed'] = 1
    if 'опасность обрушения' in t or 'danger of collapse' in t:
        features['danger_of_collapse'] = 1
    if 'требуется уборка' in t or 'urgent clearance' in t:
        features['urgent_clearance'] = 1
    return features

damage_features = main['damage_notes'].apply(extract_damage_features).apply(pd.Series)
notes_features = main['notes'].apply(extract_damage_features).apply(pd.Series)
for col in damage_features.columns:
    main[col] = damage_features[col] | notes_features[col]

main.to_csv('analysis/damage_assessment_with_features.csv', index=False)

# District/Microdistrict clustering
geo_cluster = main.groupby(['district', 'microdistrict']).size().reset_index(name='count')
geo_cluster.to_csv('analysis/district_microdistrict_clustering.csv', index=False)

# Address uniqueness (exclude empty/malformed)
valid_addr_mask = main['full_address'].apply(lambda x: isinstance(x, str) and x.strip() not in ('', ',') and len(x.strip()) > 2)
addr_dupes = main.loc[valid_addr_mask, 'full_address'].value_counts()
addr_dupes[addr_dupes > 1].to_csv('analysis/duplicate_addresses.csv')

# --- 2. Address Cross-Reference (direct/fuzzy) ---
def fuzzy_match_addresses(address_series, ref_col, ref_df):
    matches = []
    ref_choices = ref_df[ref_col].dropna().unique().tolist()  # ensure list, not numpy array
    for addr in address_series:
        # Skip empty or trivial addresses
        if not isinstance(addr, str) or addr.strip() == '' or addr.strip() == ',':
            matches.append(('', 0))
            continue
        try:
            best, score = process.extractOne(addr, ref_choices, scorer=fuzz.token_sort_ratio)
        except Exception as e:
            best, score = ('', 0)
        matches.append((best, score))
    return matches

# Example: crossref with seized properties
main['seized_match'], main['seized_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'orig_address_ru', seized))
main['ownerless_match'], main['ownerless_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'Адрес', ownerless))
main['gosu_match'], main['gosu_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'gosuslugi_address', gosu_fuzzy))
# Combine street and housenumber for prewar address matching
if 'addr:street' in prewar.columns and 'addr:housenumber' in prewar.columns:
    prewar['prewar_address'] = prewar['addr:street'].astype(str) + ', ' + prewar['addr:housenumber'].astype(str)
    main['prewar_match'], main['prewar_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'prewar_address', prewar))
elif 'addr:street' in prewar.columns:
    main['prewar_match'], main['prewar_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'addr:street', prewar))
else:
    raise KeyError('No suitable address columns found in prewar dataset')
# Combine street and housenumber for current address matching
if 'addr:street' in current.columns and 'addr:housenumber' in current.columns:
    current['current_address'] = current['addr:street'].astype(str) + ', ' + current['addr:housenumber'].astype(str)
    main['current_match'], main['current_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'current_address', current))
elif 'addr:street' in current.columns:
    main['current_match'], main['current_match_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'addr:street', current))
else:
    raise KeyError('No suitable address columns found in current dataset')

main.to_csv('analysis/damage_assessment_with_crossrefs.csv', index=False)

# --- 3. Actor/Signature Cross-Reference ---
# Direct string match on contractor and responsible_executor
main['actor_role_match'] = main['contractor'].isin(actors['name_nominative']) | main['responsible_executor'].isin(actors['name_nominative'])

# PDF signatures: fuzzy match responsible_executor to signature names
main['pdf_signature_match'], main['pdf_signature_score'] = zip(*fuzzy_match_addresses(main['responsible_executor'], 'name_match', pdf_signatures))

main.to_csv('analysis/damage_assessment_with_all_crossrefs.csv', index=False)

# --- 4. PDF Metadata Cross-Reference ---
# Fuzzy match address to pdf_metadata address/title fields
# Synthesize address candidate for fuzzy matching
if 'pdf_address_candidate' not in pdf_metadata.columns:
    pdf_metadata['pdf_address_candidate'] = pdf_metadata['filename'].astype(str) + ' ' + pdf_metadata['link_text'].astype(str)
main['pdf_meta_match'], main['pdf_meta_score'] = zip(*fuzzy_match_addresses(main['full_address'], 'pdf_address_candidate', pdf_metadata))

main.to_csv('analysis/damage_assessment_fully_crossreferenced.csv', index=False)

print("Forensic dissection and cross-reference complete. Outputs in analysis/.")
