# Forensic Evidence Pipeline Report: Administrative Violence in Occupied Mariupol

## Executive Summary

This report documents the forensic pipeline for evidence asset management, mapping, and analysis of administrative violence and property dispossession in occupied Mariupol. It integrates critical theory, digital forensics, and public-facing data visualization, with a focus on the systematic seizure, restoration, and transformation of property under occupation administration (2022–2025).

**Key goals:**
- Build a scalable, searchable, and forensic-grade asset database
- Extract, normalize, and map all evidence assets (documents, images, geodata)
- Enable critical, legal, and public accountability analysis

---

## 1. Evidence Asset Database

A comprehensive, recursively indexed database catalogs all files and evidence assets in the project, including:
- Filenames, relative paths, asset type, SHA-256 hash, file size, last modified date, extension, MIME type
- Deduplication and chain-of-custody tracking

**Sample:**

| filename | relative_path | asset_type | sha256 | size_bytes | last_modified |
|----------|--------------|------------|--------|------------|---------------|
| asset_database.csv | data/processed/Morskoy46/asset_database.csv | other | ... | ... | ... |
| p.1173.pdf | data/raw/downloaded_pdfs/p.1173.pdf | document | ... | ... | ... |

[Full asset database (CSV)](data/processed/Morskoy46/asset_database.csv)

---

## 2. Key Source Documents and Links

All official occupation decrees, administrative orders, and related PDFs are cataloged and linked for forensic mapping and analysis.

**Sample links:**
- [p.1173.pdf](https://mariupol-r897.gosweb.gosuslugi.ru/netcat_files/396/4721/p.1173.pdf)
- [p.1183.pdf](https://mariupol-r897.gosweb.gosuslugi.ru/netcat_files/396/4721/p.1183.pdf)
- [Full PDF link manifest (JSON)](data/raw/mariupol_pdf_links.json)

---

## 3. Visual Evidence: Building Facade Reference

Curated and historical images are used for ML training and public mapping. Below are sample visuals (see full folder for more):

![Morskoy 46 & 44 Facade](data/processed/Morskoy46/telegram_images_sorted/building_facade_reference/historical/44+46_outside.png)

![Morskoy 46 Damaged](data/processed/Morskoy46/telegram_images_sorted/building_facade_reference/historical/46_damaged_outside.png)

---

## 4. Data Tables and Analytical Files

**Apartment-entrance mapping:**
[Morskoy46_apartment_entrance_summary.csv](data/processed/Morskoy46/Morskoy46_apartment_entrance_summary.csv)

**Ownerless property (corrected):**
[p1173_ownerless_morskoy46_corrected.csv](data/processed/Morskoy46/p1173_ownerless_morskoy46_corrected.csv)

**Telegram media metadata:**
[telegram_media_metadata.csv](data/processed/Morskoy46/telegram_media_metadata.csv)

---

## 5. Methodology & Critical Findings

- All data processing uses robust normalization and hash-based deduplication for forensic integrity.
- Address normalization and dual-name matching enable robust cross-referencing across Russian/Ukrainian/English sources.
- Metadata (SHA-256, timestamps) is treated as systemic evidence of administrative violence (per Claude’s analysis).
- All extraction and analysis scripts are designed to support forensic, legal, and critical theory goals.

---

## 6. Appendix: Manifest and Further Links

- [asset_database.csv](data/processed/Morskoy46/asset_database.csv)
- [mariupol_pdf_links.json](data/raw/mariupol_pdf_links.json)
- [p.1173.pdf](data/raw/downloaded_pdfs/p.1173.pdf)
- [p.1183.pdf](data/raw/downloaded_pdfs/p.1183.pdf)
- [telegram_images_sorted/building_facade_reference/](data/processed/Morskoy46/telegram_images_sorted/building_facade_reference/)

---

*For questions or further analysis, see the README or contact the project maintainer.*
