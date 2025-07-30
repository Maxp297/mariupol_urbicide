#!/usr/bin/env python3
"""
Toponymic Lookup Integration Helper
Demonstrates how to integrate the forensic toponymic database into existing scripts.

This script shows common integration patterns and can be used to retrofit existing scripts
to automatically consult the forensic database for address variants.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Set
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.toponymic_lookup_service import ToponymicLookup, get_address_variants, normalize_address

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AddressProcessor:
    """Enhanced address processor that uses the forensic toponymic database"""
    
    def __init__(self):
        self.lookup = ToponymicLookup()
        self.stats = {'normalized': 0, 'variants_found': 0, 'fuzzy_matches': 0}
    
    def process_csv_with_addresses(self, csv_path: str, address_columns: List[str], 
                                 output_path: str = None) -> pd.DataFrame:
        """
        Process a CSV file by normalizing addresses and adding variant columns.
        
        Args:
            csv_path: Path to input CSV
            address_columns: List of column names containing addresses
            output_path: Optional output path for enhanced CSV
        
        Returns:
            Enhanced DataFrame with normalized addresses and variants
        """
        logger.info(f"Processing CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        
        for col in address_columns:
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found in CSV")
                continue
            
            logger.info(f"Processing address column: {col}")
            
            # Add normalized address column
            normalized_col = f"{col}_normalized"
            df[normalized_col] = df[col].apply(self._normalize_address_safe)
            
            # Add variants column (JSON string of all variants)
            variants_col = f"{col}_variants"
            df[variants_col] = df[col].apply(self._get_variants_json)
            
            # Add confidence score column
            confidence_col = f"{col}_confidence"
            df[confidence_col] = df[col].apply(self._get_confidence_score)
        
        if output_path:
            df.to_csv(output_path, index=False)
            logger.info(f"Enhanced CSV saved to: {output_path}")
        
        logger.info(f"Processing stats: {self.stats}")
        return df
    
    def _normalize_address_safe(self, address: str) -> str:
        """Safely normalize address with error handling"""
        if pd.isna(address) or not isinstance(address, str):
            return address
        
        try:
            normalized = self.lookup.normalize_address(address.strip())
            if normalized != address.strip():
                self.stats['normalized'] += 1
            return normalized
        except Exception as e:
            logger.debug(f"Failed to normalize '{address}': {e}")
            return address
    
    def _get_variants_json(self, address: str) -> str:
        """Get all variants as JSON string"""
        if pd.isna(address) or not isinstance(address, str):
            return "[]"
        
        try:
            variants = self.lookup.get_all_variants(address.strip())
            if variants:
                self.stats['variants_found'] += 1
            variant_names = [v.name_text for v in variants]
            return str(variant_names)  # Simple string representation
        except Exception as e:
            logger.debug(f"Failed to get variants for '{address}': {e}")
            return "[]"
    
    def _get_confidence_score(self, address: str) -> float:
        """Get confidence score for address normalization"""
        if pd.isna(address) or not isinstance(address, str):
            return 0.0
        
        try:
            variants = self.lookup.get_all_variants(address.strip())
            if variants:
                return max(v.confidence_score for v in variants)
            return 0.0
        except Exception as e:
            logger.debug(f"Failed to get confidence for '{address}': {e}")
            return 0.0
    
    def find_matching_addresses(self, target_addresses: List[str], 
                              search_addresses: List[str], 
                              threshold: float = 0.8) -> Dict[str, List[str]]:
        """
        Find matching addresses between two lists using fuzzy matching.
        
        Args:
            target_addresses: Addresses to find matches for
            search_addresses: Pool of addresses to search in
            threshold: Fuzzy matching threshold (0.0 to 1.0)
        
        Returns:
            Dictionary mapping target addresses to lists of matches
        """
        matches = {}
        
        for target in target_addresses:
            if pd.isna(target) or not isinstance(target, str):
                continue
            
            target_matches = []
            
            # Get all variants for the target address
            target_variants = get_address_variants(target)
            all_target_forms = [target] + target_variants
            
            # Check each search address against all target forms
            for search_addr in search_addresses:
                if pd.isna(search_addr) or not isinstance(search_addr, str):
                    continue
                
                # Get variants for search address too
                search_variants = get_address_variants(search_addr)
                all_search_forms = [search_addr] + search_variants
                
                # Cross-compare all forms
                for target_form in all_target_forms:
                    for search_form in all_search_forms:
                        try:
                            fuzzy_matches = self.lookup.fuzzy_match(target_form, threshold)
                            match_names = [m[0].name_text for m in fuzzy_matches]
                            
                            if search_form in match_names and search_addr not in target_matches:
                                target_matches.append(search_addr)
                                self.stats['fuzzy_matches'] += 1
                        except Exception as e:
                            logger.debug(f"Fuzzy match error: {e}")
            
            if target_matches:
                matches[target] = target_matches
        
        return matches
    
    def close(self):
        """Close database connection"""
        self.lookup.close()

def integrate_existing_script_example():
    """
    Example of how to integrate toponymic lookup into an existing script.
    This shows the before/after pattern for common address processing tasks.
    """
    print("🔧 Integration Example: Before and After")
    print("=" * 50)
    
    # BEFORE: Manual address matching (error-prone)
    def old_address_matching(addr1: str, addr2: str) -> bool:
        """Old way: simple string comparison"""
        return addr1.lower().strip() == addr2.lower().strip()
    
    # AFTER: Database-powered matching (robust)
    def new_address_matching(addr1: str, addr2: str) -> bool:
        """New way: use forensic database for variants and fuzzy matching"""
        with ToponymicLookup() as lookup:
            # Normalize both addresses
            norm1 = lookup.normalize_address(addr1)
            norm2 = lookup.normalize_address(addr2)
            
            # Check if normalized forms match
            if norm1.lower() == norm2.lower():
                return True
            
            # Check if either address has variants that match the other
            variants1 = [v.name_text.lower() for v in lookup.get_all_variants(addr1)]
            variants2 = [v.name_text.lower() for v in lookup.get_all_variants(addr2)]
            
            return (addr2.lower() in variants1 or 
                    addr1.lower() in variants2 or
                    bool(set(variants1) & set(variants2)))
    
    # Test both approaches
    test_pairs = [
        ("Морской 46", "б-р Комсомольский, д.46"),
        ("Komsomolsky Boulevard 46", "Морський бульвар, 46"),
        ("Металургів проспект", "Metallurgists Avenue")
    ]
    
    for addr1, addr2 in test_pairs:
        old_result = old_address_matching(addr1, addr2)
        new_result = new_address_matching(addr1, addr2)
        
        print(f"'{addr1}' vs '{addr2}':")
        print(f"  Old method: {old_result}")
        print(f"  New method: {new_result}")
        print(f"  Improvement: {'✅' if new_result and not old_result else '➖'}")
        print()

def retrofit_seized_properties_analysis():
    """
    Example of retrofitting the seized properties analysis to use the database.
    """
    print("🔧 Retrofitting Seized Properties Analysis")
    print("=" * 50)
    
    # Path to seized properties CSV
    seized_csv = PROJECT_ROOT / "data" / "processed" / "seized_properties_combined.csv"
    
    if not seized_csv.exists():
        print(f"❌ Seized properties CSV not found: {seized_csv}")
        return
    
    # Process with enhanced address handling
    processor = AddressProcessor()
    
    try:
        # Identify address columns in the seized properties data
        df = pd.read_csv(seized_csv)
        address_columns = [col for col in df.columns if 'address' in col.lower()]
        
        print(f"📊 Found address columns: {address_columns}")
        print(f"📊 Processing {len(df)} records...")
        
        # Process and enhance the data
        enhanced_df = processor.process_csv_with_addresses(
            str(seized_csv),
            address_columns,
            str(PROJECT_ROOT / "data" / "processed" / "seized_properties_enhanced.csv")
        )
        
        print(f"✅ Enhanced data saved with {len(enhanced_df.columns)} columns")
        print(f"📈 Processing statistics: {processor.stats}")
        
    except Exception as e:
        logger.error(f"Failed to process seized properties: {e}")
    finally:
        processor.close()

def demonstrate_fuzzy_matching():
    """
    Demonstrate fuzzy matching capabilities for address reconciliation.
    """
    print("🔍 Fuzzy Matching Demonstration")
    print("=" * 50)
    
    # Example: matching addresses from different sources
    gosuslugi_addresses = [
        "б-р Комсомольский, д.46, кв.15",
        "ул. Металлургов, д.123",
        "пр. Мира, д.45"
    ]
    
    seized_addresses = [
        "Морской 46",
        "Metallurgists Street 123", 
        "Peace Avenue 45",
        "Komsomolsky Boulevard 46"
    ]
    
    processor = AddressProcessor()
    
    try:
        matches = processor.find_matching_addresses(
            gosuslugi_addresses, 
            seized_addresses, 
            threshold=0.7
        )
        
        print("🎯 Address Matching Results:")
        for target, match_list in matches.items():
            print(f"  '{target}' matches:")
            for match in match_list:
                print(f"    - '{match}'")
        
        print(f"\n📈 Total fuzzy matches found: {processor.stats['fuzzy_matches']}")
        
    except Exception as e:
        logger.error(f"Fuzzy matching failed: {e}")
    finally:
        processor.close()

if __name__ == "__main__":
    print("🎯 Toponymic Database Integration Helper")
    print("=" * 60)
    
    # Test database connection
    try:
        with ToponymicLookup() as lookup:
            stats = lookup.get_statistics()
            print(f"✅ Database connected successfully")
            print(f"📊 {stats.get('total_streets', 0)} streets, {stats.get('total_variants', 0)} variants")
            print()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Run integration examples
    integrate_existing_script_example()
    retrofit_seized_properties_analysis()
    demonstrate_fuzzy_matching()
    
    print("🎯 Integration Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Import 'from scripts.toponymic_lookup_service import ToponymicLookup' in your scripts")
    print("2. Replace manual address matching with database lookups")
    print("3. Use normalize_address() for consistent address forms")
    print("4. Use fuzzy_match() for cross-dataset reconciliation")
    print("5. Use get_all_variants() for comprehensive address coverage")
