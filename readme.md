# Mariupol Urbicide: Administrative Violence Documentation Pipeline

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![Forensics](https://img.shields.io/badge/type-forensic_evidence-red)

## 🎯 Project Overview

**Self-Documented War Crimes: How Occupiers Create Their Own Evidence**

This project documents Russian occupation authorities' systematic publication of property seizures, demolitions, and redistributions in Mariupol, creating a comprehensive digital paper trail of administrative violence.

### Core Philosophy: The Bureaucratic Paradox

Administrative systems both enable atrocity and generate evidence (Arendt, Derrida, Bauman). Our methodology treats metadata as systemic evidence of administrative violence, applying critical theory to interpret digital administrative archives as counter-forensic evidence.

---

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Git LFS (for large datasets)
- 8GB+ RAM recommended

### 🐳Docker Deployment (Recommended)

```bash
# Clone repository
git clone https://github.com/Amethyst-Deceiver2001/mariupol_urbicide.git
cd mariupol_urbicide

# Deploy the platform
./deploy-forensic-platform.sh # ./deploy-forensic-platform.ps1 for Windows

# Access services:
# - JupyterLab: http://localhost:8888 (token: forensic_analysis_2024)
# - Streamlit Dashboard: http://localhost:8501
```

### Manual Installation (Development)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Service Architecture

| Service      | Description                                 |
|--------------|---------------------------------------------|
| PostgreSQL/PostGIS | Forensic database with temporal tracking |
| JupyterLab   | Interactive analysis                        |
| Streamlit    | Evidence visualization                      |
| Nginx        | Reverse proxy                              |

### Management Commands

```bash
# Start services
./deploy-forensic-platform.sh start

# Stop services
./deploy-forensic-platform.sh stop

# View logs
./deploy-forensic-platform.sh logs
```

### Data Persistence

| Resource   | Storage Location (Docker volume) |
|------------|----------------------------------|
| Database   | `mariupol-forensic-db-data`      |
| Notebooks  | `mariupol-forensic-notebooks`    |
| Logs       | `mariupol-forensic-logs`         |

### 📁 Project Structure

```
mariupol_urbicide/  
├── 📂 analysis/                       # Forensic analysis
├── 📂 config/                         # Configuration files
├── 📂 data/                           # Evidence datasets
├── 📂 docker/                         # Container configs
├── 📂 docs/                           # Documentation
├── 📂 logs/                           # System logs
├── 📂 notebooks/                      # Jupyter notebooks
├── 📂 output/                         # Reports  
├── 📂 qgis/                           # QGIS project files  
├── 📂 scripts/                        # Utilities & reporting  
├── 📂 src/                            # Core library  
├── 📂 templates/                      # HTML/report templates  
├── 📂 tests/                          # Unit and integration tests  
├── 📂 tools/                          # CLI and helper tools  
├── 📂 utils/                          # Utility modules  
```

### 🔍 Core Features

1. Automated Evidence Collection
   - Web scraping of occupation sites
   - PDF extraction and analysis
   - Chain-of-custody documentation
2. Forensic Analysis
   - Address normalization
   - Temporal analysis
   - Cross-document linking
3. Visualization & Reporting
   - Interactive maps
   - Timeline visualization
   - Automated reports

### 🤝 Support & Contact

For inquiries and partnership opportunities, please contact: kovalever@gmail.com

### Support Our Work

Your contributions help sustain this important work:

- **PayPal Donations:** kovalever@googlemail.com
- **U.S. Tax-Deductible Donations** through Building Democracy Foundation (501c3):  
  [Donate via PayPal Giving Fund](https://www.paypal.com/donate/?hosted_button_id=TQ6VZ7CFSHTHW) or directly to igors@buildingdemocracy.foundation

#### In-Kind Donations

We also welcome:

- Equipment donations
- Pro subscriptions for development tools
- Computational tokens and cloud credits
- Other professional services

Your support helps us continue documenting these critical human rights violations.

### 📄 License

GNU General Public License v3.0 - See [LICENSE](./LICENSE)

**Note**: This is forensic evidence of war crimes. All data collection follows international humanitarian law.
