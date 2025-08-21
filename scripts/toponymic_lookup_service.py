#!/usr/bin/env python3
"""
Forensic Toponymic Lookup Service
Centralized database integration layer for address variant lookups across all scripts.

Usage:
    from toponymic_lookup_service import ToponymicLookup
    
    lookup = ToponymicLookup()
    variants = lookup.get_all_variants("Морской 46")
    normalized = lookup.normalize_address("б-р Комсомольский, д.46")
    matches = lookup.fuzzy_match("Morskoy Boulevard 46", threshold=0.8)
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from rapidfuzz import fuzz
from config import db_config

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AddressVariant:
    """Represents a single address variant with metadata"""
    name_text: str
    language_code: str
    script_code: str
    administrative_period: str
    confidence_score: float
    source_document: str
    evidence_type: str
    metadata: Dict

@dataclass
class StreetInfo:
    """Complete street information with all variants"""
    street_id: str
    osm_way_id: Optional[str]
    variants: List[AddressVariant]
    created_at: datetime
    source_hash: str
    confidence_score: float

class ToponymicLookup:
    """Centralized service for forensic toponymic database lookups"""
    
    def __init__(self, db_name: str = "mariupol_forensic_toponyms", schema: str = "forensic_toponymy"):
        self.db_name = db_name
        self.schema = schema
        self.conn = None
        self._cache = {}  # Simple in-memory cache for performance
        self._connect()
    
    def _connect(self):
        """Connect to forensic toponymic database"""
        try:
            self.conn = psycopg2.connect(
                host=db_config['host'],
                database=self.db_name,
                user=db_config['user'],
                password=db_config['password'],
                port=int(db_config['port'])
            )
            # Set search path to forensic schema
            with self.conn.cursor() as cur:
                cur.execute(f"SET search_path TO {self.schema}, public")
            self.conn.commit()
            logger.info(f"Connected to forensic toponymic database: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_all_variants(self, address: str, include_fuzzy: bool = True) -> List[AddressVariant]:
        """Get all variants for a given address (exact + fuzzy matches)"""
        cache_key = f"variants_{address}_{include_fuzzy}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        variants = []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Exact matches first
                cur.execute("""
                    SELECT sn.name_text, sn.language_code, sn.script_code, 
                           sn.administrative_period, sn.confidence_score,
                           sn.source_document, sn.evidence_type, sn.metadata,
                           s.street_id, s.osm_way_id, s.created_at, s.source_hash
                    FROM street_names sn
                    JOIN streets s ON sn.street_id = s.street_id
                    WHERE LOWER(sn.name_text) = LOWER(%s)
                    ORDER BY sn.confidence_score DESC
                """, (address,))
                
                for row in cur.fetchall():
                    variants.append(AddressVariant(
                        name_text=row['name_text'],
                        language_code=row['language_code'],
                        script_code=row['script_code'],
                        administrative_period=row['administrative_period'],
                        confidence_score=row['confidence_score'],
                        source_document=row['source_document'],
                        evidence_type=row['evidence_type'],
                        metadata=row['metadata'] or {}
                    ))
                
                # Fuzzy matches if requested and no exact matches
                if include_fuzzy and not variants:
                    fuzzy_matches = self.fuzzy_match(address, threshold=0.8, limit=5)
                    variants.extend([match[0] for match in fuzzy_matches])
        
        except Exception as e:
            logger.error(f"Failed to get variants for '{address}': {e}")
        
        self._cache[cache_key] = variants
        return variants
    
    def normalize_address(self, address: str) -> str:
        """Normalize address to canonical form using database variants"""
        variants = self.get_all_variants(address, include_fuzzy=True)
        
        if not variants:
            return address  # Return original if no variants found
        
        # Return the highest confidence variant
        best_variant = max(variants, key=lambda v: v.confidence_score)
        return best_variant.name_text
    
    def fuzzy_match(self, address: str, threshold: float = 0.8, limit: int = 10) -> List[Tuple[AddressVariant, float]]:
        """Fuzzy match address against all database variants"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all street names for fuzzy matching
                cur.execute("""
                    SELECT sn.name_text, sn.language_code, sn.script_code, 
                           sn.administrative_period, sn.confidence_score,
                           sn.source_document, sn.evidence_type, sn.metadata
                    FROM street_names sn
                    ORDER BY sn.confidence_score DESC
                    LIMIT 1000  -- Limit for performance
                """)
                
                candidates = []
                for row in cur.fetchall():
                    variant = AddressVariant(
                        name_text=row['name_text'],
                        language_code=row['language_code'],
                        script_code=row['script_code'],
                        administrative_period=row['administrative_period'],
                        confidence_score=row['confidence_score'],
                        source_document=row['source_document'],
                        evidence_type=row['evidence_type'],
                        metadata=row['metadata'] or {}
                    )
                    
                    # Calculate fuzzy similarity
                    similarity = fuzz.ratio(address.lower(), variant.name_text.lower()) / 100.0
                    
                    if similarity >= threshold:
                        candidates.append((variant, similarity))
                
                # Sort by similarity and return top matches
                candidates.sort(key=lambda x: x[1], reverse=True)
                return candidates[:limit]
        
        except Exception as e:
            logger.error(f"Failed to fuzzy match '{address}': {e}")
            return []
    
    def get_street_info(self, street_id: str) -> Optional[StreetInfo]:
        """Get complete street information by ID"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get street metadata
                cur.execute("""
                    SELECT street_id, osm_way_id, created_at, source_hash, confidence_score
                    FROM streets WHERE street_id = %s
                """, (street_id,))
                
                street_row = cur.fetchone()
                if not street_row:
                    return None
                
                # Get all variants for this street
                cur.execute("""
                    SELECT name_text, language_code, script_code, administrative_period,
                           confidence_score, source_document, evidence_type, metadata
                    FROM street_names WHERE street_id = %s
                    ORDER BY confidence_score DESC
                """, (street_id,))
                
                variants = []
                for row in cur.fetchall():
                    variants.append(AddressVariant(
                        name_text=row['name_text'],
                        language_code=row['language_code'],
                        script_code=row['script_code'],
                        administrative_period=row['administrative_period'],
                        confidence_score=row['confidence_score'],
                        source_document=row['source_document'],
                        evidence_type=row['evidence_type'],
                        metadata=row['metadata'] or {}
                    ))
                
                return StreetInfo(
                    street_id=street_row['street_id'],
                    osm_way_id=street_row['osm_way_id'],
                    variants=variants,
                    created_at=street_row['created_at'],
                    source_hash=street_row['source_hash'],
                    confidence_score=street_row['confidence_score']
                )
        
        except Exception as e:
            logger.error(f"Failed to get street info for '{street_id}': {e}")
            return None
    
    def search_by_language(self, language_code: str, limit: int = 100) -> List[AddressVariant]:
        """Get all variants for a specific language"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT name_text, language_code, script_code, administrative_period,
                           confidence_score, source_document, evidence_type, metadata
                    FROM street_names 
                    WHERE language_code = %s
                    ORDER BY confidence_score DESC
                    LIMIT %s
                """, (language_code, limit))
                
                variants = []
                for row in cur.fetchall():
                    variants.append(AddressVariant(
                        name_text=row['name_text'],
                        language_code=row['language_code'],
                        script_code=row['script_code'],
                        administrative_period=row['administrative_period'],
                        confidence_score=row['confidence_score'],
                        source_document=row['source_document'],
                        evidence_type=row['evidence_type'],
                        metadata=row['metadata'] or {}
                    ))
                
                return variants
        
        except Exception as e:
            logger.error(f"Failed to search by language '{language_code}': {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                stats = {}
                
                # Total streets
                cur.execute("SELECT COUNT(*) as count FROM streets")
                stats['total_streets'] = cur.fetchone()['count']
                
                # Total street names/variants
                cur.execute("SELECT COUNT(*) as count FROM street_names")
                stats['total_variants'] = cur.fetchone()['count']
                
                # By language
                cur.execute("""
                    SELECT language_code, COUNT(*) as count 
                    FROM street_names 
                    GROUP BY language_code 
                    ORDER BY count DESC
                """)
                stats['by_language'] = dict(cur.fetchall())
                
                # By evidence type
                cur.execute("""
                    SELECT evidence_type, COUNT(*) as count 
                    FROM street_names 
                    GROUP BY evidence_type 
                    ORDER BY count DESC
                """)
                stats['by_evidence_type'] = dict(cur.fetchall())
                
                # By administrative period
                cur.execute("""
                    SELECT administrative_period, COUNT(*) as count 
                    FROM street_names 
                    GROUP BY administrative_period 
                    ORDER BY count DESC
                """)
                stats['by_period'] = dict(cur.fetchall())
                
                return stats
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Convenience functions for easy import
def get_address_variants(address: str, include_fuzzy: bool = True) -> List[str]:
    """Get all address variants as simple string list"""
    with ToponymicLookup() as lookup:
        variants = lookup.get_all_variants(address, include_fuzzy)
        return [v.name_text for v in variants]

def normalize_address(address: str) -> str:
    """Normalize address to canonical form"""
    with ToponymicLookup() as lookup:
        return lookup.normalize_address(address)

def fuzzy_match_addresses(address: str, threshold: float = 0.8) -> List[str]:
    """Fuzzy match address and return matching strings"""
    with ToponymicLookup() as lookup:
        matches = lookup.fuzzy_match(address, threshold)
        return [match[0].name_text for match in matches]

if __name__ == "__main__":
    # Example usage and testing
    print("🎯 Forensic Toponymic Lookup Service")
    print("=" * 50)
    
    with ToponymicLookup() as lookup:
        # Get statistics
        stats = lookup.get_statistics()
        print(f"📊 Database Statistics:")
        print(f"   Total Streets: {stats.get('total_streets', 0)}")
        print(f"   Total Variants: {stats.get('total_variants', 0)}")
        print(f"   Languages: {stats.get('by_language', {})}")
        print()
        
        # Test address lookups
        test_addresses = [
            "Морской 46",
            "б-р Комсомольский, д.46", 
            "Komsomolsky Boulevard 46",
            "Морський бульвар, 46"
        ]
        
        for addr in test_addresses:
            print(f"🔍 Testing: '{addr}'")
            variants = lookup.get_all_variants(addr)
            print(f"   Found {len(variants)} variants:")
            for v in variants[:3]:  # Show top 3
                print(f"   - {v.name_text} ({v.language_code}, {v.confidence_score:.2f})")
            
            normalized = lookup.normalize_address(addr)
            print(f"   Normalized: '{normalized}'")
            print()
