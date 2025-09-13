#!/usr/bin/env python3
"""
Forensic Address Variant Generation Engine
Implements comprehensive transliteration and normalization for Ukrainian/Russian toponyms
Based on Opus research report recommendations
"""

import json
import re
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import logging
from config import PROJECT_ROOT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForensicVariantGenerator:
    """Generates comprehensive address variants for forensic toponymic matching"""

    def _create_variants_dir(self):
        self.variants_dir.mkdir(parents=True, exist_ok=True)
    
    def __init__(self):
        self.project_root = Path(PROJECT_ROOT)
        self.variants_dir = self.project_root / 'data' / 'processed' / 'address_variants'
        self._create_variants_dir()
        
        # Ukrainian-specific transliteration rules (DSTU 9112:2021)
        self.uk_to_en_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
            'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i',
            'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
            'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'iu', 'я': 'ia'
        }
        
        # Russian transliteration rules (GOST 7.79)
        self.ru_to_en_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'iu', 'я': 'ia'
        }
        
        # Street type abbreviations (Russian/Ukrainian)
        self.street_abbreviations = {
            'бульвар': ['б-р', 'бул.', 'блвр', 'boulevard', 'blvd', 'blvd.'],
            'улица': ['ул.', 'у.', 'street', 'st.', 'st'],
            'проспект': ['пр-т', 'пр.', 'просп.', 'avenue', 'ave.', 'ave'],
            'переулок': ['пер.', 'п.', 'lane', 'ln.', 'ln'],
            'площадь': ['пл.', 'площ.', 'square', 'sq.', 'sq'],
            'набережная': ['наб.', 'embankment', 'emb.'],
            'шоссе': ['ш.', 'highway', 'hwy.', 'hwy'],
            'тупик': ['туп.', 'dead end', 'cul-de-sac']
        }
        
        # Building designators
        self.building_designators = {
            'дом': ['д.', 'д', 'house', 'building', 'bldg.', 'no.', '#'],
            'будинок': ['буд.', 'буд', 'house', 'building', 'bldg.'],
            'корпус': ['к.', 'корп.', 'corp.', 'building'],
            'строение': ['стр.', 'structure', 'bldg.']
        }
        
        # Number format patterns
        self.number_patterns = [
            r'(\d+)',           # Simple number: 46
            r'(\d+[а-яa-z])',   # Letter suffix: 46а, 46a
            r'(\d+/\d+)',       # Slash format: 46/1
            r'(\d+-\d+)',       # Dash format: 46-1
            r'(\d+\s*к\.\s*\d+)', # Korpus: 46 к.1
            r'(\d+\s*корп\.\s*\d+)' # Full korpus: 46 корп.1
        ]
    
    def transliterate_ukrainian(self, text: str) -> str:
        """Transliterate Ukrainian text to Latin using DSTU 9112:2021"""
        result = ""
        text = text.lower()
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Handle position-dependent rules
            if char == 'є':
                if i == 0 or text[i-1] in ' -':
                    result += 'ye'
                else:
                    result += 'ie'
            elif char == 'ї':
                if i == 0 or text[i-1] in ' -':
                    result += 'yi'
                else:
                    result += 'i'
            elif char == 'й':
                if i == 0 or text[i-1] in ' -':
                    result += 'y'
                else:
                    result += 'i'
            elif char in self.uk_to_en_map:
                result += self.uk_to_en_map[char]
            else:
                result += char
            
            i += 1
        
        return result.title()
    
    def transliterate_russian(self, text: str) -> str:
        """Transliterate Russian text to Latin using GOST 7.79"""
        result = ""
        for char in text.lower():
            if char in self.ru_to_en_map:
                result += self.ru_to_en_map[char]
            else:
                result += char
        
        return result.title()
    
    def generate_abbreviation_variants(self, address: str, language: str) -> List[str]:
        """Generate abbreviation variants for street types"""
        variants = {address,}
        address_lower = address.lower()
        
        for full_form, abbrevs in self.street_abbreviations.items():
            if full_form in address_lower:
                for abbrev in abbrevs:
                    # Replace with abbreviation
                    variant = re.sub(
                        rf'\b{re.escape(full_form)}\b', 
                        abbrev, 
                        address_lower, 
                        flags=re.IGNORECASE
                    )
                    variants.add(variant.title())
                    
                    # Also try with different capitalization
                    variants.add(variant.upper())
                    variants.add(variant.lower())
        
        return list(variants)
    
    def generate_number_variants(self, address: str) -> List[str]:
        """Generate number format variants"""
        variants = {address,}
        
        # Extract numbers and generate variants
        for pattern in self.number_patterns:
            matches = re.findall(pattern, address, re.IGNORECASE)
            for match in matches:
                base_num = re.sub(r'[^\d]', '', match)
                if base_num:
                    # Generate different formats
                    number_variants = [
                        base_num,
                        f"{base_num}а", f"{base_num}А", f"{base_num}a", f"{base_num}A",
                        f"д. {base_num}", f"д.{base_num}", f"дом {base_num}",
                        f"буд. {base_num}", f"буд.{base_num}", f"будинок {base_num}",
                        f"№{base_num}", f"No. {base_num}", f"Building {base_num}",
                        f"{base_num}-й", f"{base_num}-ий", f"{base_num}th"
                    ]
                    
                    for num_var in number_variants:
                        variant = address.replace(match, num_var)
                        variants.add(variant)
        
        return list(variants)
    
    def generate_building_designator_variants(self, address: str) -> List[str]:
        """Generate building designator variants"""
        variants = {address,}
        address_lower = address.lower()
        
        for full_form, abbrevs in self.building_designators.items():
            if full_form in address_lower:
                for abbrev in abbrevs:
                    variant = re.sub(
                        rf'\b{re.escape(full_form)}\b',
                        abbrev,
                        address_lower,
                        flags=re.IGNORECASE
                    )
                    variants.add(variant.title())
        
        return list(variants)
    
    def generate_comprehensive_variants(self, base_address: str, street_name: str, building_number: str) -> Dict[str, List[str]]:
        """Generate comprehensive variants for all languages"""
        variants = {
            'rus': [],
            'ukr': [],
            'eng': []
        }
        
        # Russian variants
        rus_base = f"{street_name}, {building_number}"
        rus_variants = [rus_base]
        rus_variants.extend(self.generate_abbreviation_variants(rus_base, 'rus'))
        rus_variants.extend(self.generate_number_variants(rus_base))
        rus_variants.extend(self.generate_building_designator_variants(rus_base))
        variants['rus'] = list(set(rus_variants))
        
        # Ukrainian variants (convert Russian street name to Ukrainian)
        ukr_street = self.convert_russian_to_ukrainian_street(street_name)
        ukr_base = f"{ukr_street}, {building_number}"
        ukr_variants = [ukr_base]
        ukr_variants.extend(self.generate_abbreviation_variants(ukr_base, 'ukr'))
        ukr_variants.extend(self.generate_number_variants(ukr_base))
        ukr_variants.extend(self.generate_building_designator_variants(ukr_base))
        variants['ukr'] = list(set(ukr_variants))
        
        # English variants (transliterate both Russian and Ukrainian)
        eng_variants = []
        for rus_var in variants['rus'][:10]:  # Limit to avoid explosion
            eng_variants.append(self.transliterate_russian(rus_var))
        for ukr_var in variants['ukr'][:10]:
            eng_variants.append(self.transliterate_ukrainian(ukr_var))
        variants['eng'] = list(set(eng_variants))
        
        return variants
    
    # FIXME: not very useful, just a bunch of hard-coded variants
    def convert_russian_to_ukrainian_street(self, russian_street: str) -> str:
        """Convert Russian street names to Ukrainian equivalents"""
        # Common Russian-Ukrainian street name conversions
        conversions = {
            'морской': 'морський',
            'комсомольский': 'комсомольський',
            'ленина': 'леніна',
            'советский': 'радянський',
            'красный': 'червоний',
            'новый': 'новий',
            'центральный': 'центральний',
            'мира': 'миру',
            'победы': 'перемоги'
        }
        
        result = russian_street.lower()
        for rus, ukr in conversions.items():
            result = result.replace(rus, ukr)
        
        return result.title()
    
    def generate_and_save_variants(self, street_name: str, building_number: str, output_filename: str) -> str:
        """Generate and save comprehensive variants to JSON file"""
        logger.info(f"Generating variants for {street_name}, {building_number}")
        
        base_address = f"{street_name}, {building_number}"
        variants = self.generate_comprehensive_variants(base_address, street_name, building_number)
        
        # Add metadata
        variant_data = {
            "metadata": {
                "base_address": base_address,
                "street_name": street_name,
                "building_number": building_number,
                "generation_method": "forensic_comprehensive_transliteration",
                "transliteration_standards": ["DSTU_9112_2021", "GOST_7_79"],
                "total_variants": sum(len(v) for v in variants.values())
            },
            "variants": variants
        }
        
        # Save to file
        output_path = self.variants_dir / f"{output_filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(variant_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Generated {variant_data['metadata']['total_variants']} variants, saved to {output_path}")
        return str(output_path)
    
    def batch_generate_from_seized_properties(self) -> List[str]:
        """Generate variants for all unique addresses in seized properties"""
        logger.info("Batch generating variants from seized properties dataset")
        
        # Load seized properties
        seized_props_path = self.project_root / 'data' / 'processed' / 'seized_properties_combined.csv'
        if not seized_props_path.exists():
            logger.error(f"Seized properties file not found: {seized_props_path}")
            return []
        
        import pandas as pd
        df = pd.read_csv(seized_props_path)
        
        # Extract unique street-building combinations
        unique_addresses = set()
        for _, row in df.iterrows():
            address = row.get('address', '') or row.get('normalized_address', '')
            if address and pd.notna(address):
                # Parse street and building
                street_name, building_num = self.parse_address(str(address))
                if street_name and building_num:
                    unique_addresses.add((street_name, building_num))
        
        logger.info(f"Found {len(unique_addresses)} unique address combinations")
        
        # Generate variants for each
        generated_files = []
        for street_name, building_num in unique_addresses:
            # Create safe filename
            safe_name = re.sub(r'[^\w\s-]', '', f"{street_name}_{building_num}").strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            
            try:
                output_file = self.generate_and_save_variants(
                    street_name, building_num, safe_name
                )
                generated_files.append(output_file)
            except Exception as e:
                logger.error(f"Failed to generate variants for {street_name}, {building_num}: {e}")
        
        return generated_files
    
    def parse_address(self, address: str) -> tuple[Optional[str], Optional[str]]:
        """Parse address into street name and building number"""
        if not address or pd.isna(address):
            return None, None
        
        address = str(address).strip()
        
        # Try to extract building number
        building_match = re.search(r',?\s*(?:д\.?\s*|дом\s*|буд\.?\s*)?(\d+[а-я]?)(?:\s|$|,)', address, re.IGNORECASE)
        if building_match:
            building_num = building_match.group(1)
            # Extract street name (everything before building number)
            street_name = address[:building_match.start()].strip().rstrip(',')
            return street_name, building_num
        
        return None, None

def main():
    """Main execution function"""
    generator = ForensicVariantGenerator()
    
    # Generate variants for Morskoy 46 (example)
    generator.generate_and_save_variants(
        "бульвар Морской", "46", "morskoy_boulevard_46_comprehensive"
    )
    
    # Generate variants for Komsomolsky 46 (dual name)
    generator.generate_and_save_variants(
        "бульвар Комсомольский", "46", "komsomolsky_boulevard_46_comprehensive"
    )
    
    # Batch generate from seized properties
    generated_files = generator.batch_generate_from_seized_properties()
    
    logger.info(f"Variant generation complete. Generated {len(generated_files)} variant files.")

if __name__ == "__main__":
    main()
