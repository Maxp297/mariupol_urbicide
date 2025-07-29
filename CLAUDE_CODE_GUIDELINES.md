# Claude Code Generation Guidelines
**Mariupol Urbicide Project - Forensic Evidence Pipeline**

## 🎯 Project Context

This is a forensic documentation project analyzing administrative violence and property seizures in occupied Mariupol through:
- Occupation administration documents
- Telegram evidence
- Geospatial data

## 📋 Critical Requirements

### Forensic Integrity
- Maintain SHA-256 hashes for all generated files
- Include timestamps in all data processing steps
- Preserve source attribution chains
- Treat all output as potential legal evidence

### Data Standards
- **Address Format**: Use canonical format `б-р Комсомольский, д. 46, кв. [number]`
- **NO REGEX** for address normalization - use JSON templates from `data/processed/address_variants/`
- **Unicode Support**: Always use fpdf2 + DejaVuSans.ttf for Cyrillic text
- **Actor Names**: Normalize using `actor_roles_nominative.csv` with pymorphy2

## 🔧 Code Generation Rules

1. **Script Generation**
   - Generate but DO NOT auto-execute pandas operations
   - Include forensic metadata in script headers
   - Add SHA-256 hash validation where appropriate
   - Use absolute paths with BASE_DIR pattern

2. **Data Processing**
   - Preserve all metadata fields
   - Include source attribution comments
   - Maintain data provenance chains
   - Add validation checkpoints

3. **PDF Generation**
   ```python
   # Required imports
   from fpdf2 import FPDF
   import os

   # Font configuration
   FONT_PATH = os.path.join(BASE_DIR, "scripts/fonts/DejaVuSans.ttf")
   ```

4. **CSV Operations**
   - Always use UTF-8 encoding
   - Include metadata headers
   - Preserve timestamp columns
   - Add data source references

## 📁 Key Data Sources

1. **Seized Properties**
   - Location: `data/processed/seized_properties_combined.csv`
   - Size: 2.9MB
   - Format: CSV with addresses, dates, coordinates

2. **Damage Assessment**
   - Location: `data/processed/damage_assessment_clean_en.csv`
   - Size: 771KB
   - Content: Russian occupation damage records

3. **Morskoy 46 Collection**
   - Location: `data/processed/Morskoy46/`
   - Content: 299 files (images, metadata, geodata)

## ⚠️ Technical Constraints

1. **File Operations**
   ```python
   # Required pattern for file paths
   BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   file_path = os.path.join(BASE_DIR, "relative/path/to/file")
   ```

2. **Data Validation**
   ```python
   # Required validation pattern
   import hashlib
   
   def validate_file_integrity(file_path, expected_hash=None):
       sha256_hash = hashlib.sha256()
       with open(file_path, "rb") as f:
           for byte_block in iter(lambda: f.read(4096), b""):
               sha256_hash.update(byte_block)
       return sha256_hash.hexdigest()
   ```

## 🔍 Current Focus

1. Morskoy 46 Evidence Aggregation
   - Consolidate all data sources
   - Maintain forensic metadata
   - Preserve temporal sequence
   - Enable ML training preparation

2. Cross-Reference Validation
   - Address normalization verification
   - Temporal consistency checks
   - Source attribution validation

## 📊 Output Requirements

1. **CSV Files**
   - UTF-8 encoding
   - Forensic metadata headers
   - Source attribution columns
   - Timestamp preservation

2. **Analysis Scripts**
   - Documentation headers with purpose
   - Input validation
   - Data provenance tracking
   - Error handling with logging

3. **Reports**
   - Unicode support for Cyrillic
   - Embedded metadata
   - Source citations
   - Chain of custody markers

---

*This guide ensures code generation maintains forensic precision and methodological rigor while supporting the documentation of administrative violence in Mariupol.*
exit()