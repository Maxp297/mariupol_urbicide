# Research Plan: Comprehensive Postgres-Powered Temporal Toponymic Database for Mariupol

**Date**: July 30, 2025  
**Project**: Mariupol Urbicide Documentation Pipeline  
**Target**: Claude Opus Instance Implementation  
**Credits Available**: 84 over 4 days  

---

## 📊 **Current Asset Inventory**

### **Existing Toponymic Data Sources**
1. **`mariupol_prewar_structures.csv`** (1.6MB) - Pre-invasion OSM data with address fields
2. **`mariupol_current_structures.csv`** (1.6MB) - Current/post-invasion OSM data  
3. **`seized_properties_combined.csv`** (2.9MB) - 50,000+ addresses with Russian/Ukrainian variants
4. **`commercial_clean.csv`** (83KB) - Commercial property addresses
5. **`damage_assessment_clean_en.csv`** (771KB) - Russian occupation damage assessments with addresses
6. **`p.1173_ownerless_table_clean.csv`** (21KB) - Ownerless property table with addresses
7. **`pdf_metadata.csv`** (83KB) - Document metadata with address references in link_text
8. **`morsky_komsomolsky_46_address_variants.json`** (3KB) - Sample address variant template

### **Untracked/Raw Assets**
- **415+ PDFs** in `data/raw/downloaded_pdfs/` containing address references
- **OSM historical data** in raw GeoJSON format
- **Telegram metadata** with location references
- **UNOSAT damage assessment** shapefiles with geographic data

---

## 🎯 **Research Plan for Opus Instance**

### **Phase 1: Database Schema Design (High Priority)**
**Objective**: Design PostgreSQL schema with PostGIS extensions for temporal toponymic data

**Key Tables**:
```sql
-- Core toponymic entities
CREATE TABLE streets (
    id SERIAL PRIMARY KEY,
    canonical_name_ua TEXT,
    canonical_name_ru TEXT,
    street_type TEXT, -- проспект, улица, бульвар, etc.
    geometry GEOMETRY(LINESTRING, 4326)
);

-- Temporal name variants
CREATE TABLE street_names (
    id SERIAL PRIMARY KEY,
    street_id INTEGER REFERENCES streets(id),
    name_variant TEXT,
    language CHAR(2), -- ua, ru, en
    name_type TEXT, -- official, colloquial, occupation, historical
    valid_from DATE,
    valid_to DATE,
    source TEXT,
    confidence_score FLOAT
);

-- Address normalization patterns
CREATE TABLE address_patterns (
    id SERIAL PRIMARY KEY,
    pattern_regex TEXT,
    replacement_template TEXT,
    pattern_type TEXT -- abbreviation, transliteration, number_format
);
```

### **Phase 2: Data Integration Pipeline (Critical)**
**Objective**: Extract, normalize, and harmonize all address variants from existing assets

**Priority Tasks**:
1. **Extract all unique addresses** from 8 core datasets
2. **Parse address components** (street type, name, number, apartment)
3. **Identify temporal variants** (pre/during/post-invasion)
4. **Map Russian ↔ Ukrainian equivalents**
5. **Generate abbreviation/number format variants**

**Methodology**:
- Use `rapidfuzz` for fuzzy matching across datasets
- Apply `transliterate` for Cyrillic/Latin variants
- Extract patterns from existing `address_variants` JSON template
- Cross-reference with OSM historical data for temporal validation

### **Phase 3: Temporal Layer Construction (High Value)**
**Objective**: Build comprehensive temporal mapping of street name changes

**Research Priorities**:
1. **Pre-invasion baseline** (2014-2022): Ukrainian official names
2. **Occupation period** (2022-present): Russian administrative renaming
3. **Decommunization period** (2015-2016): Previous Ukrainian renaming
4. **Soviet legacy names**: Historical Russian/Soviet variants still in use

**Data Sources to Investigate**:
- **OpenStreetMap full history** for Mariupol region
- **Ukrainian government decrees** on street renaming (2015-2016)
- **Russian occupation administration** renaming orders (in your PDFs)
- **Wikidata temporal mappings** for major streets

### **Phase 4: Variant Generation Engine (Technical Innovation)**
**Objective**: Automatically generate all possible address variants for robust matching

**Variant Categories**:
1. **Language variants**: Ukrainian ↔ Russian ↔ English
2. **Transliteration variants**: Multiple Cyrillic→Latin systems
3. **Abbreviation patterns**: ул. ↔ улица, пр-т ↔ проспект, б-р ↔ бульвар
4. **Number formats**: д.46 ↔ дом 46 ↔ 46, кв.12 ↔ квартира 12
5. **Temporal aliases**: Current ↔ historical ↔ occupation names

**Algorithm Design**:
```python
def generate_address_variants(canonical_address):
    variants = []
    # Language translation (UA→RU→EN)
    # Transliteration (multiple systems)
    # Abbreviation expansion/contraction
    # Number format standardization
    # Temporal name substitution
    return variants
```

---

## 🚀 **Implementation Strategy (84 Credits)**

### **Task 1: Database Schema & Core Pipeline (25-30 credits)**
- Design PostgreSQL schema with PostGIS extensions
- Create data ingestion pipeline for all 8 core datasets
- Implement address parsing and normalization functions
- Build variant generation engine

### **Task 2: Temporal Mapping Research (25-30 credits)**
- Extract street name changes from OSM history
- Mine occupation administration PDFs for renaming orders
- Research Ukrainian government decommunization decrees
- Cross-reference with Wikidata temporal data

### **Task 3: Comprehensive Variant Database (25-30 credits)**
- Generate all possible variants for existing addresses
- Implement fuzzy matching algorithms for cross-dataset linkage
- Create confidence scoring system for variant reliability
- Build API endpoints for address normalization queries

---

## 📈 **Expected Outcomes**

### **Immediate Forensic Value**
- **Perfect address matching** across all evidence datasets
- **Temporal tracking** of administrative renaming as evidence of systematic control
- **Variant resolution** for OCR errors and transliteration inconsistencies
- **Legal documentation** of toponymic violence and cultural erasure

### **Research Innovation**
- **First comprehensive temporal toponymic database** for a conflict zone
- **Automated variant generation** methodology for multilingual contexts
- **PostgreSQL/PostGIS framework** replicable for other occupied territories
- **Counter-forensic evidence** of systematic toponymic colonization

### **Technical Infrastructure**
- **Production-ready database** for all future address-based analysis
- **API endpoints** for real-time address normalization
- **Confidence scoring** for legal admissibility of address matches
- **Scalable framework** for expanding to other Ukrainian cities

---

## 🔍 **Detailed Asset Analysis**

### **Address Coverage Assessment**
Based on current asset review:
- **Total unique addresses**: ~50,000+ across all datasets
- **Temporal coverage**: Pre-war (OSM), occupation (seizure data), current (damage assessment)
- **Language variants**: Ukrainian, Russian, mixed transliterations
- **Geographic scope**: Full Mariupol city boundaries
- **Quality issues**: OCR errors, inconsistent formatting, missing normalization

### **Critical Gaps Identified**
1. **Missing temporal linkage** between pre/post-invasion address variants
2. **Incomplete abbreviation patterns** for address component normalization
3. **No systematic transliteration** mapping between Cyrillic/Latin variants
4. **Limited confidence scoring** for fuzzy address matches
5. **Fragmented storage** across multiple CSV/JSON files

### **Technical Requirements**
- **PostgreSQL 13+** with PostGIS 3.0+ extensions
- **Python 3.9+** with pandas, geopandas, rapidfuzz, transliterate
- **Storage**: ~10GB for full database with indexes and variants
- **Performance**: Sub-second address normalization queries
- **API**: RESTful endpoints for real-time address resolution

---

## 📋 **Implementation Checklist**

### **Phase 1 Deliverables**
- [ ] PostgreSQL database schema with PostGIS extensions
- [ ] Data ingestion scripts for all 8 core datasets
- [ ] Address parsing and component extraction functions
- [ ] Basic variant generation algorithms

### **Phase 2 Deliverables**
- [ ] OSM historical data extraction and temporal mapping
- [ ] PDF mining for occupation administration street renaming
- [ ] Ukrainian decommunization decree research and integration
- [ ] Wikidata temporal toponymic data integration

### **Phase 3 Deliverables**
- [ ] Complete address variant database with confidence scores
- [ ] Fuzzy matching algorithms for cross-dataset linkage
- [ ] API endpoints for address normalization and resolution
- [ ] Documentation and testing framework

### **Success Metrics**
- **Address match rate**: >95% across all datasets
- **Temporal coverage**: Complete pre/during/post-invasion mapping
- **Variant generation**: >90% coverage of observed address formats
- **Performance**: <1 second average query response time
- **Legal compliance**: Chain-of-custody documentation for all sources

---

## 🎯 **Priority Recommendations**

Given the 84 credit constraint and 4-day timeline, prioritize:

1. **Start with Task 1** (Database Schema & Core Pipeline) - Essential foundation
2. **Focus on existing assets** before external research - Maximize known data value
3. **Implement variant generation** early - Provides immediate matching improvements
4. **Document everything** - Critical for forensic chain-of-custody requirements

This research plan provides the framework for building the most comprehensive temporal toponymic database for a conflict zone, directly supporting the project's forensic and legal objectives while establishing replicable methodology for other occupied territories.

---

**Next Steps**: Begin with Phase 1 implementation, focusing on PostgreSQL schema design and core data ingestion pipeline for immediate forensic value.
