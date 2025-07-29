# Mariupol Urbicide: Administrative Violence Documentation Pipeline

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![Forensics](https://img.shields.io/badge/type-forensic_evidence-red)

## 🎯 Project Overview

**Self-Documented War Crimes: How Occupiers Create Their Own Evidence**

This project demonstrates an unprecedented phenomenon in war crimes documentation: Russian occupation authorities in Mariupol systematically publish their own property seizures, demolitions, and redistributions on official websites, creating a comprehensive digital paper trail of administrative violence.

**The Innovation**: While most war crimes investigations struggle to find evidence, we've built an automated forensic pipeline to collect, verify, and map this self-incriminating bureaucratic evidence according to international legal standards.

### Core Philosophy: The Bureaucratic Paradox

Administrative systems both enable atrocity and generate evidence (Arendt, Derrida, Bauman). Our methodology treats metadata as systemic evidence of administrative violence, applying critical theory to interpret digital administrative archives as counter-forensic evidence.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git LFS (for large datasets)
- QGIS (optional, for geospatial analysis)

### Installation
```bash
# Clone repository
git clone https://github.com/Amethyst-Deceiver2001/mariupol_urbicide.git
cd mariupol_urbicide

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your PROJECT_ROOT and API keys
```

### Basic Usage
```bash
# Run forensic analysis on a single PDF
python analysis/extract_structured_from_pdf.py data/raw/downloaded_pdfs/example.pdf

# Generate comprehensive address enrichment
python analysis/enrich_addresses.py

# Create evidence report for specific address
python scripts/generate_morskoy46_pdf_report.py
```

---

## 📁 Project Structure

```
mariupol_urbicide/
├── 📂 data/                           # Evidence datasets (Git LFS)
│   ├── raw/downloaded_pdfs/           # 415+ occupation administration PDFs
│   ├── processed/                     # Cleaned, normalized datasets
│   │   ├── Morskoy46/                # Focused case study (299 files)
│   │   ├── seized_properties_combined.csv    # Master seizure database
│   │   └── damage_assessment_clean_en.csv    # Russian damage assessments
│   └── interim/                       # Temporary processing files
│
├── 📂 analysis/                       # Core forensic analysis (48 scripts)
│   ├── crawl_mariupol_pdfs.py        # Automated evidence collection
│   ├── extract_structured_from_pdf.py # Document parsing & extraction
│   ├── forensic_dissection_and_crossref.py # Cross-reference analysis
│   └── enrich_addresses.py           # Address normalization & enrichment
│
├── 📂 scripts/                        # Utilities & reporting
│   ├── build_asset_database.py       # Evidence catalog management
│   ├── generate_address_variants.py   # Address normalization
│   └── generate_morskoy46_pdf_report.py # Case study reporting
│
├── 📂 src/                           # Core implementation modules
│   ├── forensics/                    # Evidence chain validation
│   ├── processing/                   # Data processing pipelines
│   └── analysis/                     # Analysis frameworks
│
├── 📂 qgis/                          # Geospatial analysis & mapping
├── 📂 tests/                         # Test suite
├── 📂 docs/                          # Documentation
└── 📂 .vscode/                       # VSCode configuration (AI-ready)
```

---

## 🔬 Core Capabilities

### 1. **Automated Evidence Collection**
- **PDF Scraping**: Crawls official Mariupol administration websites
- **Document Parsing**: Extracts structured data from scanned/text PDFs
- **Metadata Preservation**: SHA-256 hashing, timestamps, source attribution
- **Deduplication**: Prevents evidence loss from filename collisions

### 2. **Forensic Analysis Pipeline**
- **Address Normalization**: Handles Cyrillic/Latin variants, OCR errors
- **Cross-Reference Matching**: Links seizures across multiple datasets
- **Actor Network Analysis**: Tracks officials, contractors, responsibility chains
- **Temporal Analysis**: Timeline reconstruction of administrative actions

### 3. **Evidence Integration**
- **Multi-Source Fusion**: PDFs, Telegram media, satellite imagery, OSM data
- **Geospatial Mapping**: QGIS integration for evidence visualization
- **Legal Documentation**: International law-compliant evidence chains
- **Public Reporting**: Automated PDF/web report generation

### 4. **Case Study: Morskoy 46**
- **Complete Evidence Package**: 299 files documenting single building
- **Apartment-Level Tracking**: 216 apartments, entrance mapping
- **Multi-Modal Evidence**: Documents, images, geospatial data
- **ML-Ready Dataset**: Curated for automated image classification

---

## 📊 Key Datasets

| Dataset | Size | Description | Status |
|---------|------|-------------|---------|
| `seized_properties_combined.csv` | 2.9MB | Master database of all seized properties | ✅ Complete |
| `damage_assessment_clean_en.csv` | 771KB | Russian occupation damage assessments | ✅ Complete |
| `pdf_metadata.csv` | 83KB | Metadata for 415+ official documents | ✅ Complete |
| `actor_roles_nominative.csv` | 11KB | Officials and contractors network | ✅ Complete |
| `asset_database_full.csv` | 7.2MB | Complete evidence catalog | ✅ Complete |

---

## 🛠️ Development

### VSCode Integration
The project is optimized for VSCode with AI assistance:
- **Auto-configured**: `.vscode/settings.json` and `launch.json` included
- **Python Environment**: Automatic `.venv` detection
- **Debugging Presets**: Forensic analysis configurations
- **Extension Recommendations**: Python, Jupyter, Git integration

### Code Quality
- **Forensic Standards**: SHA-256 validation for all file operations
- **Evidence Chain**: Complete source attribution and timestamps
- **Reproducibility**: Environment variables, containerization support
- **Testing**: Comprehensive test suite for data integrity

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/analysis-enhancement`
3. Follow forensic coding standards (see `CLAUDE_CODE_GUIDELINES.md`)
4. Add tests for new functionality
5. Submit pull request with evidence validation

---

## 📈 Current Status & Roadmap

### ✅ **Completed (v0.2.0)**
- **Codebase Optimization**: 243MB cleanup, VSCode migration
- **Evidence Pipeline**: 415+ PDFs processed, 683 unique addresses extracted
- **Morskoy 46 Case Study**: Complete evidence package assembled
- **Forensic Infrastructure**: SHA-256 validation, metadata preservation
- **Cross-Reference System**: Multi-dataset linkage and enrichment

### 🔄 **In Progress**
- **ML Image Classification**: Automated Telegram media sorting
- **Web Interface**: Public evidence browser and mapping tool
- **Legal Documentation**: International court-ready evidence packages
- **Temporal Analysis**: Administrative action timeline reconstruction

### 🎯 **Next Priorities**
- **Neighborhood Expansion**: Morskoy 40-48 complete evidence collection
- **Actor Network Analysis**: Official responsibility mapping
- **Financial Flow Tracking**: Budget and contractor analysis
- **Public Presentation**: Interactive evidence maps and reports

---

## 📚 Documentation

- **[VSCode Handover Report](VSCODE_HANDOVER_REPORT.md)**: Development environment setup
- **[Claude Code Guidelines](CLAUDE_CODE_GUIDELINES.md)**: Forensic coding standards
- **[Changelog](CHANGELOG.md)**: Version history and updates
- **[Forensic Evidence Pipeline](report_forensic_evidence_pipeline.md)**: Methodology overview

---

## 🔒 Legal & Ethical Framework

### Evidence Standards
- **Chain of Custody**: Complete source attribution and timestamps
- **Data Integrity**: SHA-256 validation for all evidence files
- **Reproducibility**: Environment variables and containerization
- **Legal Compliance**: International humanitarian law standards

### Ethical Considerations
- **Public Interest**: Evidence of systematic war crimes
- **Source Protection**: No personal data of victims exposed
- **Academic Standards**: Peer-reviewable methodology
- **Open Source**: Transparent, auditable evidence collection

---

## 🤝 Collaboration

### Academic Partners
- **Critical Theory**: Foucault, Mbembe, Weizman frameworks
- **Digital Forensics**: Counter-forensic methodology development
- **International Law**: War crimes documentation standards
- **Geospatial Analysis**: Satellite imagery and damage assessment

### Technical Integration
- **APIs**: Google Maps, OpenStreetMap, Telegram
- **Databases**: PostgreSQL with PostGIS extensions
- **ML Frameworks**: CLIP, computer vision for image classification
- **Visualization**: QGIS, web mapping, interactive reports

---

## 📞 Contact & Support

**Repository**: https://github.com/Amethyst-Deceiver2001/mariupol_urbicide

**Issues**: Use GitHub Issues for bug reports and feature requests

**Documentation**: See `docs/` directory for detailed guides

**Citation**: If using this work academically, please cite the repository and methodology papers

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**Note**: This is forensic evidence of war crimes. All data collection and analysis follows international humanitarian law and academic research standards.
