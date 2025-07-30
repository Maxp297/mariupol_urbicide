# Building Forensic Toponymic Evidence Systems

Based on comprehensive technical research across six specialized domains, here's a complete solution for building a temporal toponymic database to document Russian occupation street renaming in Mariupol as evidence of administrative violence and cultural erasure.

## PostgreSQL/PostGIS database architecture delivers forensic-grade temporal tracking

The foundation requires a **bitemporal PostgreSQL schema** that maintains both valid-time (when street names were actually in use) and transaction-time (when changes were recorded in the database). This approach, following the Asserted Versioning Framework, creates an immutable audit trail essential for legal evidence.

### Schema design for multilingual toponymy

The core architecture uses a normalized translation table approach with separate entities for streets and their names across languages. Each street name record includes language codes ('ukr', 'rus', 'eng'), script codes ('Cyrl', 'Latn'), and transliterated values. The bitemporal model employs PostgreSQL's **tstzrange** types to track both when street names were valid in reality and when they were recorded in the database, creating overlapping time periods that capture the uncertainty inherent in conflict documentation.

**Critical implementation**: Use EXCLUDE constraints with GIST indexes to prevent temporal overlaps for the same street in the same language, ensuring data integrity. The confidence scoring system weights source reliability (0.4), fuzzy match accuracy (0.3), temporal proximity (0.2), and spatial proximity (0.1) to create forensically defensible quality assessments.

### Memory optimization for 8GB constraints

PostgreSQL configuration should allocate **2GB shared_buffers** (25% of RAM), **6GB effective_cache_size** (75% of RAM), and conservative **32MB work_mem** for multilingual text processing. Implement time-based partitioning with monthly partitions and archive old data to separate tablespaces. Use materialized views for frequently accessed current data, reducing memory pressure during complex temporal queries.

The indexing strategy combines GiST indexes for temporal ranges, GIN indexes for multilingual text search using pg_trgm extension, and composite indexes for common query patterns. Partial indexes on current records (WHERE valid_to = 'infinity') significantly improve performance for present-day queries.

## Historical OSM data extraction maximizes efficiency within memory limits

**Osmium time-filter** provides the most memory-efficient approach for extracting street data from February 23, 2022. The optimal workflow processes Ukraine region history files using streaming operations to avoid loading entire datasets into memory.

### Temporal extraction workflow

```bash
# Extract Ukrainian region with minimal memory usage
osmium extract --bbox 22.0,44.0,40.5,52.5 --strategy simple \
  --with-history planet-history.osh.pbf -o ukraine-history.osh.pbf

# Extract specific date snapshot
osmium time-filter ukraine-history.osh.pbf 2022-02-23T00:00:00Z \
  -o ukraine-2022-02-23.osm.pbf

# Filter for streets with Ukrainian names
osmium tags-filter ukraine-2022-02-23.osm.pbf \
  "w/highway,name or w/highway,name:uk" -o mariupol-streets.osm.pbf
```

The key is processing data in single passes using piped workflows to avoid intermediate files. For Mariupol specifically, focus the bounding box on coordinates 37.5,47.0,37.6,47.2 to minimize data volume while capturing the entire city.

### Cyrillic text handling in OSM

OSM historical data contains multilingual name tags: `name:uk` (Ukrainian), `name:ru` (Russian), and `name:en` (English transliterations). PyOsmium handles UTF-8 encoding automatically, but implement custom preprocessing to normalize Ukrainian-specific characters (ґ, є, і, ї) and remove common formatting artifacts from crowdsourced data.

## Ukrainian decommunization data establishes forensic baseline

The **Ukrainian Institute of National Memory** documented **51,493 street renamings** between 2014-2016, providing authoritative before/after mappings essential for establishing pre-occupation toponymy. Mariupol underwent significant renaming in 2016, including Catherine II Street → Vladimir Lenin Avenue → Peace Avenue, creating a documented sequence that Russian occupation authorities later disrupted.

### Official data sources

The most reliable sources combine Verkhovna Rada legislative resolutions (providing legal authority), UINM implementation records (providing execution details), and municipal council decisions (providing local specifics). Academic databases from institutions like ResearchGate contain comprehensive before/after mappings with 2,202 streets in complete historical sequence from first historical data through June 2023.

**Critical for legal evidence**: Cross-reference multiple authoritative sources to establish unambiguous pre-occupation baselines. The temporal sequence (Soviet → Ukrainian decommunization → Russian occupation) creates three distinct toponymic layers that can be forensically verified.

## Address variant generation algorithms handle transliteration complexity

Ukrainian and Russian place names can be transliterated using multiple systems, creating legitimate variants that fuzzy matching must account for. The **CyrTranslit library** provides the most efficient Python implementation, supporting bidirectional transliteration with multiple standard systems (ISO 9, UNGEGN, ALA-LC, BGN-PCGN).

### Comprehensive variant generation

The algorithmic approach generates variants across four dimensions: transliteration systems (Ukrainian National 2010, DSTU 9112:2021, Russian GOST 7.79), abbreviation patterns (вул./вулиця → St./Street), number formats (15а, 15-17, 15/17), and historical versus modern standards. Critical Ukrainian-specific patterns include position-dependent rules where initial Є- becomes "Ye-" but mid-word becomes "ie-".

For memory efficiency, implement caching and memoization for repeated text segments, pre-compile regular expressions for abbreviation patterns, and use trie structures for efficient prefix matching. This reduces computational overhead when processing thousands of address variants.

## RapidFuzz configurations optimize Cyrillic text matching

**RapidFuzz** outperforms FuzzyWuzzy significantly while handling Unicode natively. For Ukrainian/Russian text, the optimal configuration uses **fuzz.WRatio()** for general matching, **token_sort_ratio()** for word order variations, and **token_set_ratio()** for subset matching scenarios common in address fragments.

### OCR error handling

Common Cyrillic OCR errors include character ambiguities (В↔B, С↔C, Н↔H, У↔Y, Р↔P) and multi-character substitutions ("ш" → "w", "щ" → "sch"). Implement weighted edit distances with custom substitution costs for visually similar characters, combined with context-aware validation using language models.

The preprocessing pipeline normalizes Cyrillic-specific characters (ё↔е), removes Ukrainian quotation marks (guillemets «»), standardizes dashes (— → -), and extracts address components separately. This significantly improves matching accuracy by reducing noise and focusing algorithms on meaningful content.

### Confidence scoring methodology

Multi-metric approaches combine Levenshtein distance (30%), Jaro-Winkler similarity (30%), token-based matching (25%), and phonetic similarity (15%) to create comprehensive confidence scores. Threshold-based classification defines high confidence (>85%), medium confidence (70-85% requiring manual review), and low confidence (<70% likely false positives).

## Legal precedents establish toponymic evidence frameworks

The **International Criminal Tribunal for Yugoslavia** established crucial precedents for using cultural destruction as evidence of persecution and genocidal intent. The **Constitutional Court of Bosnia and Herzegovina** specifically addressed systematic renaming, finding that "symbolism of a name can be as important, both practically and constitutionally, as an act of direct discrimination."

### Forensic evidence standards

**ICC digital evidence guidelines** require complete chain of custody documentation, technical authentication through cryptographic hash analysis, metadata preservation (location, timestamps, device information), and expert testimony for validation. The new **OTPLink platform** provides tamper-proof record collection with blockchain verification.

For toponymic evidence specifically, documentation must establish: (1) historical naming patterns through official records, maps, and census data; (2) systematic nature of changes through administrative orders and legal documents; (3) community impact through witness testimony; and (4) pattern analysis demonstrating systematic rather than isolated changes.

### Administrative violence framework

Systematic renaming constitutes "administrative violence" under international law—the use of legal and bureaucratic systems to achieve discriminatory outcomes. When conducted as part of ethnic cleansing campaigns, toponymic erasure evidences intent to permanently alter territorial identity. ICTY precedent established that administrative measures targeting group identity constitute persecution when systematic and discriminatory.

## Implementation strategy within budget constraints

The entire system can be implemented within the $20 budget constraint using open-source tools and free data sources. **PostgreSQL/PostGIS** provides enterprise-grade capabilities without licensing costs. **Geofabrik Ukraine extracts** supply current and historical OSM data for free. **CyrTranslit and RapidFuzz** libraries offer production-ready text processing without fees.

### Resource allocation

Dedicate the primary effort to database schema implementation and temporal data modeling, as this foundation determines the entire system's forensic validity. Secondary priorities include OSM data extraction workflows and fuzzy matching optimization. The legal framework research provides context but requires no additional technical implementation beyond proper documentation standards.

Deploy the system using **Docker containers** to ensure reproducibility across different environments. Implement **automated backup strategies** with cryptographic verification to maintain chain of custody. Use **monitoring dashboards** to track data quality metrics and confidence score distributions over time.

## Forensic validation and quality assurance

The system generates self-documenting evidence through comprehensive logging, confidence scoring, and multi-source validation. Every toponymic change is recorded with timestamp, source reliability, fuzzy matching scores, and manual verification status. This creates an audit trail suitable for international court proceedings.

**Critical success metrics**: (1) Complete temporal coverage from Ukrainian decommunization through Russian occupation; (2) Multi-source corroboration for all name changes; (3) Confidence scores above 85% for court-ready evidence; (4) Complete metadata preservation for digital evidence authentication; and (5) Expert forensic validation of technical methodologies.

This technical framework provides a robust foundation for exposing systematic cultural erasure through toponymic violence, creating legally admissible evidence of administrative violence while remaining within practical resource constraints. The combination of temporal database design, historical data extraction, multilingual text processing, and legal precedent integration delivers a comprehensive solution for documenting occupation-driven cultural destruction.