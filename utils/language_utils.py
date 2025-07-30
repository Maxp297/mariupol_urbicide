import re
import langdetect
from typing import Dict, List, Tuple, Optional

class ToponymMapper:
    """Maps place names across different periods and political regimes"""
    
    def __init__(self, toponyms_file: Optional[str] = None):
        self.toponyms = self._load_toponyms(toponyms_file)
    
    def _load_toponyms(self, toponyms_file: Optional[str]) -> Dict[str, Dict[str, str]]:
        """Load toponyms from file or use default mapping"""
        if toponyms_file:
            import yaml
            with open(toponyms_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Default minimal mapping of known toponymic changes
        return {
            "mariupol": {
                "uk_2022": "Маріуполь",
                "ru_2022": "Мариуполь",
                "ru_2023": "Жданов",  # Russian re-naming attempt
                "canonical": "Mariupol",
                "coordinates": "47.097133, 37.543367"
            },
            "morskoy": {
                "uk_2022": "Морський проспект",
                "ru_2022": "Морской проспект", 
                "ru_2023": "проспект Ленина",
                "canonical": "Morskoy Avenue",
                "coordinates": "47.096673, 37.554131"
            },
            # Add more toponyms as needed
        }
    
    def identify_toponyms(self, text: str) -> List[Dict[str, str]]:
        """Identify all possible toponyms in text"""
        found_toponyms = []
        
        for base_name, variants in self.toponyms.items():
            for period, name_variant in variants.items():
                if period != "canonical" and period != "coordinates":
                    # Search for this variant in the text
                    if re.search(r'\b' + re.escape(name_variant) + r'\b', text, re.IGNORECASE):
                        found_toponyms.append({
                            "matched_text": name_variant,
                            "canonical_name": variants["canonical"],
                            "period": period,
                            "coordinates": variants.get("coordinates", "")
                        })
        
        return found_toponyms
    
    def normalize_toponym(self, toponym: str) -> Dict:
        """Try to normalize a toponym to its canonical form"""
        for base_name, variants in self.toponyms.items():
            for period, name_variant in variants.items():
                if period != "canonical" and period != "coordinates":
                    if toponym.lower() == name_variant.lower():
                        return {
                            "input": toponym,
                            "canonical": variants["canonical"],
                            "period": period,
                            "coordinates": variants.get("coordinates", "")
                        }
        
        return {"input": toponym, "canonical": toponym, "normalized": False}

class LanguageDetector:
    """Detects and processes multilingual content"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect the language of text"""
        try:
            # Handle common detection issues with Ukrainian/Russian
            text_sample = text[:5000]  # Use a sample for efficiency
            
            # Custom logic to differentiate between Russian and Ukrainian
            # This is a simplistic approach - in production use more sophisticated methods
            uk_specific = ['є', 'ї', 'і', 'ґ']
            ru_specific = ['ы', 'ъ', 'э']
            
            for char in uk_specific:
                if char in text_sample.lower():
                    return "uk"
            
            for char in ru_specific:
                if char in text_sample.lower():
                    return "ru"
            
            # Fall back to langdetect
            return langdetect.detect(text_sample)
        except:
            return "unknown"
    
    @staticmethod
    def get_transcript_languages(video_id: str) -> List[str]:
        """Get available transcript languages for a YouTube video"""
        # In production, implement with YouTube API or yt-dlp
        # For now, we'll just return common languages for the region
        return ["ru", "uk", "en"]