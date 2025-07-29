import json
import os
from typing import List, Dict

ADDRESS_VARIANT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'address_variants')
os.makedirs(ADDRESS_VARIANT_DIR, exist_ok=True)

def generate_variants_ru(street: str, number: str) -> List[str]:
    base = [
        f"бульвар {street}", f"б-р {street}", f"{street} бульвар", f"{street} б-р", f"{street} бул.", f"бул. {street}", f"{street}"
    ]
    numbered = []
    for b in base:
        numbered.extend([
            f"{b}, {number}", f"{b}, д. {number}", f"{b} д. {number}", f"{b}, д.{number}", f"{b} д.{number}",
            f"{b} дом {number}", f"{b} №{number}", f"{b}, дом {number}", f"{b}, №{number}", f"{b} {number}"
        ])
    # Add number-only variants
    numbered.extend([number, f"д. {number}", f"д.{number}", f"дом {number}", f"№{number}", f"{number}-й", f"{number}-ий"])
    # Add common sub-number formats
    for suffix in ["а", "А", "a", "A", "/1", "-1", " к.1", " корп.1"]:
        numbered.append(f"{number}{suffix}")
    return numbered

def generate_variants_uk(street: str, number: str) -> List[str]:
    base = [
        f"бульвар {street}", f"б-р {street}", f"{street} бульвар", f"{street} б-р", f"{street} бул.", f"бул. {street}", f"{street}"
    ]
    numbered = []
    for b in base:
        numbered.extend([
            f"{b}, {number}", f"{b}, буд. {number}", f"{b} буд. {number}", f"{b}, буд.{number}", f"{b} буд.{number}",
            f"{b} будинок {number}", f"{b} №{number}", f"{b}, будинок {number}", f"{b}, №{number}", f"{b} {number}"
        ])
    numbered.extend([number, f"буд. {number}", f"буд.{number}", f"будинок {number}", f"№{number}", f"{number}-й", f"{number}-ий"])
    for suffix in ["а", "А", "a", "A", "/1", "-1", " к.1", " корп.1"]:
        numbered.append(f"{number}{suffix}")
    return numbered

def generate_variants_en(street: str, number: str) -> List[str]:
    base = [
        f"{street} Boulevard", f"{street} Blvd.", f"{street} blvd", f"Blvd. {street}", f"{street}"]
    numbered = []
    for b in base:
        numbered.extend([
            f"{b}, {number}", f"{b} No. {number}", f"{b} Building {number}", f"{number} {b}", f"{number} {b}.", f"{number} {b}",
            f"{b} {number}", f"{b} #{number}", f"{b} {number}"
        ])
    numbered.extend([number, f"{number}a", f"{number}A", f"Building {number}", f"No. {number}", f"{number}th"])
    for suffix in ["/1", "-1", " bldg 1", " corp 1"]:
        numbered.append(f"{number}{suffix}")
    return numbered

def generate_address_variants(street_ru: str, street_uk: str, street_en: str, number: str, out_slug: str):
    variants = {
        "ru": generate_variants_ru(street_ru, number),
        "uk": generate_variants_uk(street_uk, number),
        "en": generate_variants_en(street_en, number)
    }
    out_path = os.path.join(ADDRESS_VARIANT_DIR, f"address_variants_{out_slug}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(variants, f, ensure_ascii=False, indent=2)
    print(f"Variants written to {out_path}")

if __name__ == "__main__":
    # Example usage:
    generate_address_variants(
        street_ru="Морской",
        street_uk="Морський",
        street_en="Morsky",
        number="46",
        out_slug="morsky_46"
    )
    generate_address_variants(
        street_ru="Комсомольский",
        street_uk="Комсомольський",
        street_en="Komsomolsky",
        number="46",
        out_slug="komsomolsky_46"
    )
