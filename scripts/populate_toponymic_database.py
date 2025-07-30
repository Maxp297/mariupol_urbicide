#!/usr/bin/env python3
"""
Forensic Toponymic Database Population Script
Integrates existing project assets into PostgreSQL/PostGIS database
Based on Opus research report recommendations
"""

import os
import sys
import json
import csv
import hashlib
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

# Add project root to path
PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/Users/alexeykovalev/Desktop/urbicide_project')
sys.path.append(PROJECT_ROOT)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'logs', 'toponymic_population.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ForensicToponymicPopulator:
    """Populates forensic toponymic database with existing project assets"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
        self.project_root = Path(PROJECT_ROOT)
        self.data_dir = self.project_root / 'data'
        
    def connect_database(self):
        """Establish database connection with forensic logging"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            logger.info("Connected to forensic toponymic database")
            # Explicitly set search_path for schema visibility
            with self.conn.cursor() as cur:
                cur.execute("SET search_path TO forensic_toponymy, public;")
                logger.info("Set search_path to forensic_toponymy, public")
                # Diagnostic: print current database and schema
                cur.execute("SELECT current_database(), current_schema();")
                logger.info(f"Connected to DB: {cur.fetchone()}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close_database(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash for forensic chain-of-custody"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed for {filepath}: {e}")
            return ""
    
    def load_evidence_sources(self):
        """Load evidence sources from pdf_metadata.csv with forensic metadata"""
        logger.info("Loading evidence sources from pdf_metadata.csv")
        
        pdf_metadata_path = self.data_dir / 'processed' / 'pdf_metadata.csv'
        if not pdf_metadata_path.exists():
            logger.warning(f"PDF metadata file not found: {pdf_metadata_path}")
            return
        
        with open(pdf_metadata_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            evidence_records = []
            
            for row in reader:
                evidence_record = {
                    'source_id': str(uuid.uuid4()),
                    'source_type': 'pdf_document',
                    'filename': row.get('filename', ''),
                    'file_path': row.get('absolute_path', ''),
                    'file_size_bytes': int(row.get('file_size_bytes', 0)) if row.get('file_size_bytes') else None,
                    'sha256_hash': row.get('sha256', ''),
                    'source_url': row.get('pdf_url', ''),
                    'parent_page': row.get('parent_page', ''),
                    'download_timestamp': None,  # Parse if available
                    'last_modified': row.get('last_modified', ''),
                    'mime_type': 'application/pdf',
                    'metadata': json.dumps({
                        'link_text': row.get('link_text', ''),
                        'forensic_chain': True,
                        'source_dataset': 'pdf_metadata.csv'
                    }),
                    'created_at': datetime.now(timezone.utc)
                }
                evidence_records.append(evidence_record)
        
        # Insert evidence sources
        with self.conn.cursor() as cur:
            insert_query = """
                INSERT INTO forensic_toponymy.evidence_sources 
                (source_id, source_type, filename, file_path, file_size_bytes, 
                 sha256_hash, source_url, parent_page, download_timestamp, 
                 last_modified, mime_type, metadata, created_at)
                VALUES %s
                ON CONFLICT (sha256_hash) DO NOTHING
            """
            
            values = [
                (r['source_id'], r['source_type'], r['filename'], r['file_path'],
                 r['file_size_bytes'], r['sha256_hash'], r['source_url'], 
                 r['parent_page'], r['download_timestamp'], r['last_modified'],
                 r['mime_type'], r['metadata'], r['created_at'])
                for r in evidence_records
            ]
            
            execute_values(cur, insert_query, values)
            self.conn.commit()
            logger.info(f"Loaded {len(evidence_records)} evidence sources")
    
    def load_address_variants(self):
        """Load address variants from existing JSON files"""
        logger.info("Loading address variants from JSON files")
        
        # Load Morskoy 46 variants
        morskoy_variants_path = self.data_dir / 'processed' / 'morsky_komsomolsky_46_address_variants.json'
        if morskoy_variants_path.exists():
            with open(morskoy_variants_path, 'r', encoding='utf-8') as f:
                variants_data = json.load(f)
            
            # Create a street record for Morskoy 46
            street_id = str(uuid.uuid4())
            
            with self.conn.cursor() as cur:
                # Insert street
                cur.execute("""
                    INSERT INTO forensic_toponymy.streets 
                    (street_id, osm_way_id, created_at, created_by, source_hash, confidence_score, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    street_id, None, datetime.now(timezone.utc), 'data_migration',
                    self.calculate_file_hash(str(morskoy_variants_path)), 0.95,
                    json.dumps({
                        'canonical_name': 'Морской бульвар / Комсомольский бульвар',
                        'building_number': '46',
                        'source_file': 'morsky_komsomolsky_46_address_variants.json'
                    })
                ))
                
                # Insert address variants
                variant_records = []
                for lang_code, variants in variants_data.items():
                    # Map language codes
                    lang_map = {'ru': 'rus', 'uk': 'ukr', 'en': 'eng'}
                    db_lang_code = lang_map.get(lang_code, lang_code)
                    
                    for variant in variants:
                        variant_records.append({
                            'variant_id': str(uuid.uuid4()),
                            'street_id': street_id,
                            'canonical_address': 'Морской бульвар, 46' if lang_code == 'ru' else 'Морський бульвар, 46',
                            'variant_text': variant,
                            'language_code': db_lang_code,
                            'variant_type': 'abbreviation',
                            'confidence_score': 0.9,
                            'created_at': datetime.now(timezone.utc),
                            'source_hash': self.calculate_file_hash(str(morskoy_variants_path))
                        })
                
                # Insert variants
                insert_query = """
                    INSERT INTO forensic_toponymy.address_variants 
                    (variant_id, street_id, canonical_address, variant_text, 
                     language_code, variant_type, confidence_score, created_at, source_hash)
                    VALUES %s
                """
                
                values = [
                    (r['variant_id'], r['street_id'], r['canonical_address'], 
                     r['variant_text'], r['language_code'], r['variant_type'],
                     r['confidence_score'], r['created_at'], r['source_hash'])
                    for r in variant_records
                ]
                
                execute_values(cur, insert_query, values)
                self.conn.commit()
                logger.info(f"Loaded {len(variant_records)} address variants for Morskoy 46")
    
    def load_seized_properties_toponyms(self):
        """Extract toponymic data from seized properties dataset"""
        logger.info("Loading toponymic data from seized properties")
        
        seized_props_path = self.data_dir / 'processed' / 'seized_properties_combined.csv'
        if not seized_props_path.exists():
            logger.warning(f"Seized properties file not found: {seized_props_path}")
            return
        
        # Read seized properties data
        df = pd.read_csv(seized_props_path)
        
        # Detect column names
        address_columns = self.detect_columns(df, 'address')
        street_columns = self.detect_columns(df, 'street')
        house_number_columns = self.detect_columns(df, 'house_number')
        apartment_columns = self.detect_columns(df, 'apartment')
        
        # Extract unique street names
        unique_streets = set()
        
        # Process all detected address and street columns
        all_columns_to_process = list(set(address_columns + street_columns))  # Remove duplicates
        
        for col in all_columns_to_process:
            if col in df.columns:
                addresses = df[col].dropna().unique()
                for addr in addresses:
                    # Extract street name (before building number)
                    street_name = self.extract_street_name(str(addr))
                    if street_name:
                        unique_streets.add(street_name)
        
        logger.info(f"Found {len(unique_streets)} unique street names in seized properties")
        logger.info(f"Processed columns: {all_columns_to_process}")
        
        # Insert street names with occupation period context
        with self.conn.cursor() as cur:
            for street_name in unique_streets:
                street_id = str(uuid.uuid4())
                
                # Insert street
                cur.execute("""
                    INSERT INTO forensic_toponymy.streets 
                    (street_id, created_at, created_by, source_hash, confidence_score, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    street_id, datetime.now(timezone.utc), 'seized_properties_migration',
                    self.calculate_file_hash(str(seized_props_path)), 0.8,
                    json.dumps({
                        'source_dataset': 'seized_properties_combined.csv',
                        'extraction_method': 'automated_street_name_extraction'
                    })
                ))
                
                # Insert street name with occupation context
                cur.execute("""
                    INSERT INTO forensic_toponymy.street_names 
                    (street_id, name_text, language_code, script_code, valid_from,
                     source_document, source_hash, evidence_type, administrative_period,
                     confidence_score, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    street_id, street_name, self.detect_language_code(street_name), 'Cyrl', 
                    datetime(2022, 2, 24, tzinfo=timezone.utc),  # Start of occupation
                    'seized_properties_combined.csv',
                    self.calculate_file_hash(str(seized_props_path)),
                    'media_report', 'occupation', 0.8,
                    json.dumps({
                        'extraction_context': 'property_seizure_documents',
                        'administrative_violence': True
                    })
                ))
        
        self.conn.commit()
        logger.info(f"Loaded {len(unique_streets)} street toponyms from seized properties")
    
    def detect_columns(self, df: pd.DataFrame, keyword: str) -> List[str]:
        """Detect column names containing the given keyword"""
        return [col for col in df.columns if keyword.lower() in col.lower()]
    
    def extract_street_name(self, address: str) -> Optional[str]:
        """Extract street name from full address using deterministic logic"""
        if not address or pd.isna(address):
            return None
        
        address = str(address).strip()
        
        # Common patterns for street extraction
        # Remove building numbers and apartment info
        import re
        
        # Remove apartment numbers (кв. X, квартира X)
        address = re.sub(r',?\s*кв\.?\s*\d+.*$', '', address, flags=re.IGNORECASE)
        address = re.sub(r',?\s*квартира\s*\d+.*$', '', address, flags=re.IGNORECASE)
        
        # Remove building numbers (д. X, дом X, буд. X)
        address = re.sub(r',?\s*д\.?\s*\d+[а-я]?.*$', '', address, flags=re.IGNORECASE)
        address = re.sub(r',?\s*дом\s*\d+[а-я]?.*$', '', address, flags=re.IGNORECASE)
        address = re.sub(r',?\s*буд\.?\s*\d+[а-я]?.*$', '', address, flags=re.IGNORECASE)
        
        # Remove standalone numbers at the end
        address = re.sub(r',?\s*\d+[а-я]?$', '', address)
        
        return address.strip() if address.strip() else None
    
    def generate_comprehensive_variants(self, base_name: str, language: str) -> List[str]:
        """Generate comprehensive address variants following Opus recommendations"""
        variants = [base_name]
        
        # Abbreviation patterns
        abbreviations = {
            'бульвар': ['б-р', 'бул.', 'блвр'],
            'улица': ['ул.', 'у.'],
            'проспект': ['пр-т', 'пр.', 'просп.'],
            'переулок': ['пер.', 'п.'],
            'площадь': ['пл.', 'площ.']
        }
        
        for full_form, abbrevs in abbreviations.items():
            if full_form in base_name.lower():
                for abbrev in abbrevs:
                    variants.append(base_name.lower().replace(full_form, abbrev))
        
        return list(set(variants))
    
    def load_structure_datasets(self):
        """Load street names from structure datasets for comprehensive coverage"""
        logger.info("Loading street names from structure datasets")
        
        structure_files = [
            ('mariupol_prewar_structures.geojson', 'prewar'),
            ('mariupol_current_structures.geojson', 'current'),
            ('commercial_clean.geojson', 'commercial')
        ]
        
        for filename, dataset_type in structure_files:
            file_path = self.data_dir / 'processed' / filename
            if file_path.exists():
                try:
                    import geopandas as gpd
                    gdf = gpd.read_file(file_path)
                    logger.info(f"Processing {len(gdf)} features from {filename}")
                    
                    # Extract street names from address fields using flexible detection
                    address_columns = self.detect_columns(gdf, 'address') + self.detect_columns(gdf, 'street')
                    extracted_streets = set()
                    
                    for field in address_columns:
                        if field in gdf.columns:
                            addresses = gdf[field].dropna().unique()
                            for addr in addresses:
                                street_name = self.extract_street_name(str(addr))
                                if street_name and len(street_name) > 2:  # Filter out very short names
                                    extracted_streets.add(street_name)
                    
                    logger.info(f"Extracted {len(extracted_streets)} unique street names from {filename}")
                    
                    # Insert unique streets not already in database
                    new_streets_count = 0
                    with self.conn.cursor() as cur:
                        for street_name in extracted_streets:
                            # Check if street already exists
                            cur.execute("""
                                SELECT COUNT(*) FROM forensic_toponymy.street_names 
                                WHERE LOWER(name_text) = LOWER(%s)
                            """, (street_name,))
                            
                            if cur.fetchone()[0] == 0:  # Street doesn't exist
                                street_id = str(uuid.uuid4())
                                
                                # Insert street
                                cur.execute("""
                                    INSERT INTO forensic_toponymy.streets 
                                    (street_id, created_at, created_by, source_hash, confidence_score, metadata)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (
                                    street_id, datetime.now(timezone.utc), f'{dataset_type}_structures_migration',
                                    self.calculate_file_hash(str(file_path)), 0.85,
                                    json.dumps({
                                        'source_dataset': filename,
                                        'dataset_type': dataset_type,
                                        'extraction_method': 'structure_address_parsing'
                                    })
                                ))
                                
                                # Insert street name
                                cur.execute("""
                                    INSERT INTO forensic_toponymy.street_names 
                                    (street_id, name_text, language_code, script_code, valid_from,
                                     source_document, source_hash, evidence_type, administrative_period,
                                     confidence_score, metadata)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    street_id, street_name, self.detect_language_code(street_name), 'Cyrl',
                                    datetime(2014, 1, 1, tzinfo=timezone.utc) if dataset_type == 'prewar' else datetime(2022, 2, 24, tzinfo=timezone.utc),
                                    filename, self.calculate_file_hash(str(file_path)),
                                    'media_report', 'ukrainian' if dataset_type == 'prewar' else 'occupation', 0.85,
                                    json.dumps({
                                        'structure_derived': True,
                                        'dataset_type': dataset_type
                                    })
                                ))
                                new_streets_count += 1
                    
                    self.conn.commit()
                    logger.info(f"Added {new_streets_count} new streets from {filename}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {filename}: {e}")
                    # Rollback transaction to prevent cascade failures
                    self.conn.rollback()
            else:
                logger.warning(f"Structure file not found: {file_path}")

    def load_osm_data(self):
        """Load comprehensive OSM street network for complete Mariupol coverage"""
        logger.info("Loading comprehensive OSM street network")
        
        osm_streets_path = self.data_dir / 'raw' / 'osm' / 'mariupol_streets.geojson'
        if osm_streets_path.exists():
            try:
                # Use direct JSON parsing to bypass GeoPandas OGR type issues
                import json
                
                with open(osm_streets_path, 'r', encoding='utf-8') as f:
                    osm_data = json.load(f)
                
                logger.info(f"Loaded {len(osm_data['features'])} OSM street features for comprehensive import")
                
                # Track processed streets to avoid duplicates
                processed_streets = set()
                new_streets_count = 0
                
                with self.conn.cursor() as cur:
                    for feature in osm_data['features']:
                        try:
                            properties = feature.get('properties', {})
                            
                            # Extract street name from properties
                            street_name = properties.get('name')
                            
                            if not street_name or street_name in processed_streets:
                                continue
                            
                            # Check if street already exists in database
                            cur.execute("""
                                SELECT COUNT(*) FROM forensic_toponymy.street_names 
                                WHERE LOWER(name_text) = LOWER(%s)
                            """, (street_name,))
                            
                            if cur.fetchone()[0] > 0:  # Street already exists
                                processed_streets.add(street_name)
                                continue
                            
                            processed_streets.add(street_name)
                            street_id = str(uuid.uuid4())
                            
                            # Extract OSM metadata from properties
                            osm_id = properties.get('osmid')
                            highway_type = str(properties.get('highway', ''))
                            surface_type = str(properties.get('surface', '')) if properties.get('surface') else ''
                            maxspeed_val = str(properties.get('maxspeed', '')) if properties.get('maxspeed') else ''
                            lanes_val = str(properties.get('lanes', '')) if properties.get('lanes') else ''
                            
                            # Insert street with comprehensive OSM metadata
                            cur.execute("""
                                INSERT INTO forensic_toponymy.streets 
                                (street_id, osm_way_id, created_at, created_by, source_hash, confidence_score, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                street_id, osm_id, datetime.now(timezone.utc), 
                                'osm_comprehensive_import', self.calculate_file_hash(str(osm_streets_path)), 0.95,
                                json.dumps({
                                    'source_dataset': 'mariupol_streets.geojson',
                                    'highway': highway_type,
                                    'surface': surface_type,
                                    'maxspeed': maxspeed_val,
                                    'lanes': lanes_val,
                                    'comprehensive_import': True,
                                    'json_parsed': True
                                })
                            ))
                            
                            # Detect language and insert street name
                            lang_code = self.detect_language_code(street_name)
                            
                            cur.execute("""
                                INSERT INTO forensic_toponymy.street_names 
                                (street_id, name_text, language_code, script_code, valid_from,
                                 source_document, source_hash, evidence_type, administrative_period,
                                 confidence_score, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                street_id, street_name, lang_code, 'Cyrl', 
                                datetime(2014, 1, 1, tzinfo=timezone.utc),  # Pre-war baseline
                                'mariupol_streets.geojson', self.calculate_file_hash(str(osm_streets_path)),
                                'osm_data', 'ukrainian', 0.95,
                                json.dumps({
                                    'osm_source': True,
                                    'name_type': 'primary',
                                    'highway_class': highway_type,
                                    'comprehensive_import': True,
                                    'json_parsed': True
                                })
                            ))
                            
                            new_streets_count += 1
                            
                        except Exception as e:
                            logger.debug(f"Failed to process OSM feature: {e}")
                            continue
                
                self.conn.commit()
                logger.info(f"Added {new_streets_count} new unique OSM streets with multilingual variants")
                logger.info(f"Total processed OSM street names: {len(processed_streets)}")
                
            except Exception as e:
                logger.error(f"Failed to load comprehensive OSM data: {e}")
                # Rollback transaction to prevent cascade failures
                self.conn.rollback()
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"OSM streets file not found: {osm_streets_path}")
    
    def detect_language_code(self, street_name: str) -> str:
        """Detect language code based on street name content"""
        if not street_name:
            return 'rus'  # Default to Russian for empty strings
        
        street_lower = street_name.lower()
        
        # Ukrainian-specific characters
        ukrainian_chars = set('ґєії')
        
        # Check for Ukrainian-specific characters
        if any(char in ukrainian_chars for char in street_lower):
            return 'ukr'
        
        # Check for Cyrillic characters (Russian/Ukrainian common)
        cyrillic_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        if any(char in cyrillic_chars for char in street_lower):
            return 'rus'  # Default to Russian for common Cyrillic
        
        # Check for Latin characters
        latin_chars = set('abcdefghijklmnopqrstuvwxyz')
        if any(char in latin_chars for char in street_lower):
            return 'eng'
        
        # Default fallback
        return 'rus'
    
    def run_population(self):
        """Execute complete database population workflow"""
        logger.info("Starting forensic toponymic database population")
        
        try:
            self.connect_database()
            
            # Load data in comprehensive forensic order
            self.load_evidence_sources()
            self.load_address_variants()
            self.load_seized_properties_toponyms()
            self.load_structure_datasets()
            self.load_osm_data()
            
            logger.info("Comprehensive database population completed successfully")
            
        except Exception as e:
            logger.error(f"Population failed: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            self.close_database()

def main():
    """Main execution function"""
    # Database configuration
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432'),
        'database': os.environ.get('DB_NAME', 'mariupol_forensic_toponyms'),
        'user': os.environ.get('DB_USER', 'alexeykovalev'),
        'password': os.environ.get('DB_PASSWORD', '')
    }
    
    # Create logs directory
    logs_dir = Path(PROJECT_ROOT) / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Initialize and run populator
    populator = ForensicToponymicPopulator(db_config)
    populator.run_population()

if __name__ == "__main__":
    main()
