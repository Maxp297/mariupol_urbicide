# 🔄 VSCode Migration Handover Report
**Mariupol Urbicide Project - Forensic Evidence Pipeline**

---

## 📋 **Project Overview**

**Mission:** Document administrative violence and property seizures in occupied Mariupol through forensic analysis of occupation administration documents, Telegram evidence, and geospatial data.

**Philosophy:** Bureaucratic Paradox - administrative systems both enable atrocity and generate evidence (Arendt, Derrida, Bauman). Focus on counter-forensics and evidentiary self-incrimination.

**Current Status:** ✅ Codebase cleaned and optimized for VSCode development

---

## 🎯 **Current Project State**

### **Recently Completed (2025-07-29)**
- ✅ **Comprehensive codebase cleanup**: Freed 243.2MB disk space, removed redundant venvs
- ✅ **Requirements.txt optimization**: Removed duplicates (shapely, geopandas), updated fpdf→fpdf2
- ✅ **VSCode configuration**: Created `.vscode/settings.json` and `launch.json` with forensic analysis presets
- ✅ **File organization**: Moved session files to cache, asset database to proper location
- ✅ **Duplicate removal**: Cleaned 3 obsolete analysis CSVs, removed 6 .DS_Store files

### **Active Focus: Morskoy 46 Evidence Aggregation**
- **Goal**: Generate comprehensive, machine-readable CSV consolidating all available data for Morskoy 46
- **Status**: Data sources identified, scripts ready, awaiting final aggregation

---

## 📁 **Critical Directory Structure**

```
urbicide_project/
├── .venv/                          # ACTIVE Python environment
├── .vscode/                        # VSCode config (ready for AI assistance)
├── data/
│   ├── raw/downloaded_pdfs/        # 415 occupation administration PDFs
│   └── processed/
│       ├── Morskoy46/              # 299 files - focused evidence collection
│       ├── seized_properties_combined.csv  # 2.9MB - all seized properties
│       └── damage_assessment_clean_en.csv  # 771KB - Russian damage assessment
├── analysis/                       # 48 analysis scripts + results
├── scripts/                        # 4 utility scripts + fonts
└── cache/                          # Session files, temporary data
```

---

## 🔑 **Key Files for AI Assistant**

### **Primary Data Sources**
1. **`data/processed/seized_properties_combined.csv`** (2.9MB)
   - All seized properties with addresses, dates, coordinates
   - Canonical format: `б-р Комсомольский, д. 46, кв. [number]`

2. **`data/processed/damage_assessment_clean_en.csv`** (771KB)
   - Russian occupation damage assessment (1,946 records)
   - Self-incriminating bureaucratic evidence
   - Columns: contractor, damage_category, building_type, repair_status, etc.

3. **`data/processed/Morskoy46/`** (299 files)
   - Focused evidence collection for building 46
   - Telegram images, metadata, enriched CSVs, OSM geodata

### **Analysis Scripts (Ready to Run)**
- **`analysis/forensic_dissection_and_crossref.py`** - Cross-reference all datasets
- **`analysis/enrich_addresses.py`** - Address normalization and enrichment
- **`analysis/normalize_addresses.py`** - Canonical address formatting
- **`scripts/generate_morskoy46_pdf_report.py`** - Unicode PDF generation (fpdf2)

### **Configuration Files**
- **`requirements.txt`** - Clean, deduplicated dependencies
- **`.vscode/settings.json`** - Python paths, CSV preview, linting configured
- **`.vscode/launch.json`** - Debugging presets for forensic analysis

---

## 🧠 **Critical Context & Memories**

### **Technical Constraints**
- **User prefers pandas scripts**: Generate but don't auto-run, let user execute manually
- **No regex for address normalization**: User has better approach in mind
- **Unicode support required**: All PDFs use fpdf2 + DejaVuSans.ttf for Cyrillic text
- **Forensic chain of custody**: SHA-256 hashes, timestamps as legal infrastructure

### **Data Normalization Standards**
- **Address variants**: JSON templates in `data/processed/address_variants/`
- **Actor normalization**: `actor_roles_nominative.csv` with pymorphy2 patch
- **PDF metadata**: No 'address' column - use synthesized fields for matching

### **Key Achievements**
- 683 unique seized addresses extracted
- 110 unique (role, name) pairs from actor signatures
- Telegram images curated for ML training (46_only, historical folders)
- OSM geodata integrated for buildings 42, 44, 48

---

## 🚀 **VSCode Setup Instructions**

### **1. Environment Activation**
```bash
cd /Users/alexeykovalev/Desktop/urbicide_project
source .venv/bin/activate
```

### **2. VSCode Launch**
```bash
code .
```

### **3. Recommended Extensions**
- **Python** (Microsoft) - Already configured
- **CSV Viewer** - For data inspection
- **Jupyter** - For analysis notebooks
- **GitLens** - For forensic commit history

### **4. Python Interpreter**
- Should auto-select: `./.venv/bin/python`
- If not: `Cmd+Shift+P` → "Python: Select Interpreter" → Choose `.venv`

---

## 📊 **Current Priorities**

### **Immediate Tasks**
1. **Complete Morskoy 46 aggregation**: Run `scripts/aggregate_morskoy46_image_metadata.py`
2. **Generate comprehensive CSV**: All available data for Morskoy 46 from all databases
3. **Cross-reference validation**: Ensure all address normalization is consistent

### **Next Phase Goals**
- Train ML algorithm on Morskoy 46 Telegram data
- Expand to adjacent buildings (40, 42, 44, 48)
- Generate public-facing evidence maps in QGIS

---

## ⚠️ **Important Notes for AI Assistant**

### **User Workflow Preferences**
- **Generate scripts, don't auto-run**: Especially pandas operations
- **Prompt for ambiguity**: User values informed decision-making
- **Forensic precision**: Every edit should maintain evidence chain
- **Memory integration**: Use project memories for context

### **Technical Gotchas**
- **pdf_metadata.csv**: No 'address' column - use 'link_text' or synthesized fields
- **Address normalization**: Use canonical JSON variants, not regex
- **Unicode PDFs**: Always use fpdf2 + DejaVuSans.ttf
- **Virtual environment**: Must be activated for all Python operations

### **Data Sensitivity**
- **War crimes evidence**: Treat all data as potential legal evidence
- **Metadata preservation**: SHA-256 hashes, timestamps are forensically critical
- **Source attribution**: Every CSV should trace back to original documents

---

## 🔄 **Return Migration Path**

### **To Return to Windsurf**
1. **Commit all changes**: `git add . && git commit -m "VSCode experimental work"`
2. **Export key findings**: Update project memories with new insights
3. **Document new scripts**: Add to analysis/ or scripts/ directories
4. **Update requirements.txt**: If new dependencies added

### **Handover Assets**
- All `.vscode/` configurations preserved
- Clean codebase structure maintained
- No redundant files or environments
- Updated .gitignore for version control

---

## 📞 **Contact & Continuity**

**Project Maintainer**: alexeykovalev  
**Workspace**: `/Users/alexeykovalev/Desktop/urbicide_project`  
**Environment**: `.venv` (Python 3.13)  
**Last Cleanup**: 2025-07-29 14:38 UTC+2  

**Key Command for AI Assistant**:
```bash
source .venv/bin/activate && python analysis/forensic_dissection_and_crossref.py
```

---

*This handover report ensures seamless continuity between AI assistants while maintaining the forensic integrity and methodological rigor of the Mariupol urbicide documentation project.*
