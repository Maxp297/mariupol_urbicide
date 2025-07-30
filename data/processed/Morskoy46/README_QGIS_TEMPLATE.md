# Morskoy46 QGIS Evidence Mapping Project Template

This template describes the structure and workflow for mapping, linking, and scaling forensic evidence for Morskoy/Komsolmolsky 46 in QGIS.

---

## 1. Spatial Layer (Building Point/Polygon)
- **File:** `maps/morskoy46_osm.geojson`
- **Purpose:** Main spatial representation of the building.
- **Key Field:** `osm_id` or custom `building_id`

## 2. Attribute Table (Forensic/Administrative Data)
- **File:** `docs/gosuslugi_seized_fuzzy_matches_enriched_Morskoy46.csv`
- **Purpose:** Enriched property/administrative data for the building and apartments.
- **Key Fields:**
  - `address_normalized`
  - `pdf_filename` (for evidence linkage)
  - `pdf_hash` (future: for legal chain-of-custody)
  - `status` (e.g., ownerless, seized, repair required)
  - `source_url`
  - `notes`

## 3. Media/Document Evidence (Popups/Future Linking)
- **Folders:**
  - `telegram_images_raw/`
  - `telegram_docs_raw/`
  - `vk_images/`
  - `other_open_source_images/`
- **Future Columns (to add to CSV):**
  - `image_hashes` (SHA-256)
  - `media_file_paths` (relative paths for QGIS popups)
  - `media_type`, `media_caption`

## 4. Hashing & Provenance
- **Current:** Not yet implemented.
- **Future:** Compute SHA-256 hashes for all evidence files and store in CSV for each row.
- **Fields:** `pdf_hash`, `media_hashes`

## 5. QGIS Project File
- **File:** `Morskoy46.qgz`
- **Purpose:** Stores all layers, styles, joins, and popup configs.

---

## QGIS Layer Loading Workflow
1. **Add Vector Layer:**
   - Load `maps/morskoy46_osm.geojson` as spatial layer.
2. **Add Attribute Table:**
   - Load `docs/gosuslugi_seized_fuzzy_matches_enriched_Morskoy46.csv` as table.
3. **Join Table to Layer:**
   - Use address or ID field to join CSV to geojson.
4. **Configure Popups:**
   - Use HTML popups to show status, links, thumbnails (see below).

---

## Example QGIS Popup HTML Template
```html
<b>Address:</b> [% "address_normalized" %]<br>
<b>Status:</b> [% "status" %]<br>
<b>Source PDF:</b> <a href="file:///[% "pdf_filename" %]">Open PDF</a><br>
<b>PDF Hash:</b> [% "pdf_hash" %]<br>
<b>Images:</b>
<ul>
  <!-- In future: iterate over linked images -->
  <li><img src="file:///[% "media_file_paths" %]" width="100"></li>
</ul>
```

---

## For Future Scaling
- **Hashing:** Use a script to compute hashes for all media and docs.
- **Media Linking:** Add logic or manual curation to associate images/docs to property rows in CSV.
- **Open Source Enrichment:** Add new columns for additional sources, actors, or legal metadata as needed.

---

## Directory Structure
```
Morskoy46/
├── Morskoy46.qgz
├── maps/
│   └── morskoy46_osm.geojson
├── docs/
│   ├── gosuslugi_seized_fuzzy_matches_enriched_Morskoy46.csv
│   ├── morskoy_bulvar_metadata.md
│   └── street_vocabulary.pdf
├── telegram_images_raw/
├── telegram_videos_raw/
├── telegram_docs_raw/
├── vk_images/
├── other_open_source_images/
```

---

## Notes
- All evidence files should be referenced by relative path for portability.
- Save QGIS project in this folder to keep all links valid.
- For legal/forensic use, always preserve original hashes and filenames.
- Update this template as the project scales or new asset types are added.
