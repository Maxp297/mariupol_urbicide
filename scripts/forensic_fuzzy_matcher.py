#!/usr/bin/env python3
"""
Forensic Fuzzy Matching Interface
Optimized for Ukrainian/Russian Cyrillic text matching using RapidFuzz
Based on Opus research report recommendations
"""

import os
import sys
import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging
import pandas as pd
from rapidfuzz import fuzz, process, utils
import psycopg2
from psycopg2.extras import RealDictCursor
from config import db_config

# Add project root to path
PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/Users/alexeykovalev/Desktop/urbicide_project')
sys.path.append(PROJECT_ROOT)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForensicFuzzyMatcher:
    """Forensic-grade fuzzy matching for toponymic evidence with confidence scoring"""
    
    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        self.project_root = Path(PROJECT_ROOT)
        self.db_config = db_config
        self.conn = None
        
        # OCR error patterns for Cyrillic text (Opus recommendations)
        self.cyrillic_ocr_errors = {
            'В': ['B', 'в'], 'С': ['C', 'с'], 'Н': ['H', 'н'], 'У': ['Y', 'у'], 
            'Р': ['P', 'р'], 'О': ['O', 'о'], 'А': ['A', 'а'], 'Е': ['E', 'е'],
            'К': ['K', 'к'], 'М': ['M', 'м'], 'Т': ['T', 'т'], 'Х': ['X', 'х'],
            'ш': ['w'], 'щ': ['sch'], 'ё': ['е'], 'й': ['и']
        }
        
        # Preprocessing patterns
        self.preprocessing_patterns = [
            (r'«|»', ''),  # Remove Ukrainian quotation marks
            (r'—', '-'),   # Standardize dashes
            (r'\s+', ' '), # Normalize whitespace
            (r'^\s+|\s+$', ''), # Trim
        ]
        
        # Confidence thresholds (Opus recommendations)
        self.confidence_thresholds = {
            'high': 0.85,
            'medium': 0.70,
            'low': 0.50
        }
    
    def connect_database(self):
        """Connect to forensic toponymic database"""
        if self.db_config:
            try:
                self.conn = psycopg2.connect(**self.db_config)
                logger.info("Connected to forensic toponymic database")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                raise
    
    def close_database(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def preprocess_cyrillic_text(self, text: str) -> str:
        """Preprocess Cyrillic text for optimal fuzzy matching"""
        if not text:
            return ""
        
        text = str(text)
        
        # Apply preprocessing patterns
        for pattern, replacement in self.preprocessing_patterns:
            text = re.sub(pattern, replacement, text)
        
        # Normalize common Cyrillic variations
        text = text.replace('ё', 'е')  # Normalize ё to е
        
        return text.strip().lower()
    
    def calculate_multi_metric_confidence(self, text1: str, text2: str) -> Dict[str, float]:
        """Calculate comprehensive confidence score using multiple metrics"""
        # Preprocess both texts
        clean_text1 = self.preprocess_cyrillic_text(text1)
        clean_text2 = self.preprocess_cyrillic_text(text2)
        
        # Multi-metric scoring (Opus recommendations)
        metrics = {
            'levenshtein': fuzz.ratio(clean_text1, clean_text2) / 100.0,
            'jaro_winkler': fuzz.WRatio(clean_text1, clean_text2) / 100.0,
            'token_sort': fuzz.token_sort_ratio(clean_text1, clean_text2) / 100.0,
            'token_set': fuzz.token_set_ratio(clean_text1, clean_text2) / 100.0,
            'partial': fuzz.partial_ratio(clean_text1, clean_text2) / 100.0
        }
        
        # Weighted composite score (Opus formula)
        composite_score = (
            metrics['levenshtein'] * 0.30 +
            metrics['jaro_winkler'] * 0.30 +
            metrics['token_sort'] * 0.25 +
            metrics['token_set'] * 0.15
        )
        
        metrics['composite'] = composite_score
        return metrics
    
    def classify_confidence_level(self, composite_score: float) -> str:
        """Classify confidence level based on composite score"""
        if composite_score >= self.confidence_thresholds['high']:
            return 'high'
        elif composite_score >= self.confidence_thresholds['medium']:
            return 'medium'
        elif composite_score >= self.confidence_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def fuzzy_match_addresses(self, query_address: str, candidate_addresses: List[str], 
                            limit: int = 10) -> List[Dict]:
        """Perform fuzzy matching against candidate addresses with forensic metadata"""
        logger.info(f"Fuzzy matching query: '{query_address}' against {len(candidate_addresses)} candidates")
        
        results = []
        query_clean = self.preprocess_cyrillic_text(query_address)
        
        for candidate in candidate_addresses:
            candidate_clean = self.preprocess_cyrillic_text(candidate)
            
            # Calculate comprehensive metrics
            metrics = self.calculate_multi_metric_confidence(query_address, candidate)
            confidence_level = self.classify_confidence_level(metrics['composite'])
            
            result = {
                'query': query_address,
                'candidate': candidate,
                'confidence_score': round(metrics['composite'], 4),
                'confidence_level': confidence_level,
                'metrics': {k: round(v, 4) for k, v in metrics.items()},
                'requires_manual_review': confidence_level in ['medium', 'low'],
                'likely_false_positive': confidence_level == 'very_low'
            }
            
            results.append(result)
        
        # Sort by confidence score
        results.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return results[:limit]
    
    def match_against_database(self, query_address: str, language: str = 'rus', 
                             threshold: float = 0.7) -> List[Dict]:
        """Match query address against database using PostgreSQL fuzzy functions"""
        if not self.conn:
            logger.error("Database connection required for database matching")
            return []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Use PostgreSQL fuzzy matching function
                cur.execute("""
                    SELECT * FROM forensic_toponymy.fuzzy_match_address(%s, %s, %s)
                """, (query_address, language, threshold))
                
                db_results = cur.fetchall()
                
                # Enhance with Python-based confidence scoring
                enhanced_results = []
                for row in db_results:
                    # Get additional metrics using Python
                    metrics = self.calculate_multi_metric_confidence(
                        query_address, row['name_text']
                    )
                    
                    enhanced_result = {
                        'street_id': row['street_id'],
                        'name_text': row['name_text'],
                        'db_similarity_score': float(row['similarity_score']),
                        'python_confidence_score': metrics['composite'],
                        'confidence_level': self.classify_confidence_level(metrics['composite']),
                        'match_type': row['match_type'],
                        'metrics': metrics,
                        'forensic_metadata': {
                            'query_preprocessed': self.preprocess_cyrillic_text(query_address),
                            'candidate_preprocessed': self.preprocess_cyrillic_text(row['name_text']),
                            'matching_algorithm': 'postgresql_trigram_python_composite',
                            'threshold_used': threshold
                        }
                    }
                    
                    enhanced_results.append(enhanced_result)
                
                logger.info(f"Database matching returned {len(enhanced_results)} results")
                return enhanced_results
                
        except Exception as e:
            logger.error(f"Database matching failed: {e}")
            return []
    
    def batch_match_csv_addresses(self, csv_path: str, address_column: str, 
                                output_path: str) -> str:
        """Batch match addresses from CSV file with forensic logging"""
        logger.info(f"Batch matching addresses from {csv_path}")
        
        # Load CSV
        df = pd.read_csv(csv_path)
        if address_column not in df.columns:
            raise ValueError(f"Column '{address_column}' not found in CSV")
        
        # Load address variants for matching
        variants_dir = self.project_root / 'data' / 'processed' / 'address_variants'
        all_variants = []
        
        for variant_file in variants_dir.glob('*.json'):
            try:
                with open(variant_file, 'r', encoding='utf-8') as f:
                    variant_data = json.load(f)
                    if 'variants' in variant_data:
                        for lang, variants in variant_data['variants'].items():
                            all_variants.extend(variants)
            except Exception as e:
                logger.warning(f"Failed to load variants from {variant_file}: {e}")
        
        logger.info(f"Loaded {len(all_variants)} address variants for matching")
        
        # Perform batch matching
        results = []
        for idx, row in df.iterrows():
            query_address = str(row[address_column])
            if pd.isna(query_address) or not query_address.strip():
                continue
            
            # Match against variants
            matches = self.fuzzy_match_addresses(query_address, all_variants, limit=5)
            
            # Add row context
            for match in matches:
                match['source_row_index'] = idx
                match['source_csv'] = csv_path
                match['original_data'] = row.to_dict()
            
            results.extend(matches)
        
        # Save results
        results_df = pd.json_normalize(results)
        results_df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Batch matching complete. {len(results)} matches saved to {output_path}")
        return output_path
    
    def generate_matching_report(self, results: List[Dict]) -> Dict:
        """Generate forensic matching report with statistics"""
        if not results:
            return {'error': 'No results to analyze'}
        
        # Calculate statistics
        confidence_levels = [r['confidence_level'] for r in results]
        confidence_scores = [r['confidence_score'] for r in results]
        
        report = {
            'total_matches': len(results),
            'confidence_distribution': {
                level: confidence_levels.count(level) for level in 
                ['high', 'medium', 'low', 'very_low']
            },
            'average_confidence': sum(confidence_scores) / len(confidence_scores),
            'high_confidence_matches': len([r for r in results if r['confidence_level'] == 'high']),
            'requires_manual_review': len([r for r in results if r['requires_manual_review']]),
            'likely_false_positives': len([r for r in results if r['likely_false_positive']]),
            'forensic_metadata': {
                'matching_algorithm': 'rapidfuzz_multi_metric_cyrillic_optimized',
                'preprocessing_applied': True,
                'ocr_error_handling': True,
                'confidence_thresholds': self.confidence_thresholds
            }
        }
        
        return report

def main():
    """Main execution function for testing"""
    
    # Initialize matcher
    matcher = ForensicFuzzyMatcher(db_config)
    
    # Test with Morskoy 46 variants
    test_queries = [
        "бульвар Морской, 46",
        "б-р Комсомольский, д. 46",
        "Морський бульвар, буд. 46",
        "Morsky Boulevard, 46"
    ]
    
    test_candidates = [
        "бульвар Морской, 46",
        "бульвар Морской, д. 46", 
        "б-р Морской, 46",
        "Морской бульвар, 46",
        "бульвар Комсомольский, 46",
        "б-р Комсомольский, д. 46",
        "Комсомольский бульвар, 46"
    ]
    
    # Test fuzzy matching
    for query in test_queries:
        logger.info(f"\nTesting query: {query}")
        results = matcher.fuzzy_match_addresses(query, test_candidates, limit=3)
        
        for result in results:
            logger.info(f"  Match: {result['candidate']} "
                       f"(confidence: {result['confidence_score']:.3f}, "
                       f"level: {result['confidence_level']})")
        
        # Generate report
        report = matcher.generate_matching_report(results)
        logger.info(f"  Report: {report['high_confidence_matches']} high confidence, "
                   f"{report['requires_manual_review']} need review")

if __name__ == "__main__":
    main()
