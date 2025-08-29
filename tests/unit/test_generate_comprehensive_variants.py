import pytest
from unittest.mock import patch
from scripts.generate_comprehensive_variants import ForensicVariantGenerator

@pytest.fixture
def generator():
    # skip useless stuff in __init__
    with patch.object(ForensicVariantGenerator, '_create_variants_dir'):
        instance = ForensicVariantGenerator()
    return instance


@pytest.mark.parametrize(
    "input,expected",
    [
        ("привет", "Privet"),
        ("моль", "Mol"),
        ("ёлка целиком", "Elka Tselikom"),
        ("Отъявленный", "Otiavlennyi"),
        ("щастья хочется", "Shchastia Khochetsia"),
        ("абwгдеёжz", "Abwgdeezhz"),
        ("123 улица", "123 Ulitsa"),
    ]
)
def test_transliterate_russian(generator, input, expected):
    result = generator.transliterate_russian(input)
    assert result == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("єнот", "Yenot"),
        ("моє", "Moie"),
        ("моє життя", "Moie Zhyttia"),
        ("їжак", "Yizhak"),
        ("країна", "Kraina"),
        ("моя їжа", "Moia Yizha"),
        ("йога", "Yoha"),
        ("край", "Krai"),
        ("мой йогурт", "Moi Yohurt"),
        ("подъезд", "Podъezd"),  # Russian ъ should pass through unchanged
    ]
)
def test_transliterate_ukrainian(generator, input, expected):
    result = generator.transliterate_ukrainian(input)
    assert result == expected


def test_generate_abbreviation_variants(generator):
    address = "бульвар Морской"
    variants = generator.generate_abbreviation_variants(address, "rus")
    
    # Must include original
    assert address in variants
    # Must include common abbreviation
    assert any("б-р" in v.lower() for v in variants)
    assert any("blvd" in v.lower() for v in variants)


def test_generate_number_variants(generator):
    address = "ул. Ленина, 46"
    variants = generator.generate_number_variants(address)

    # Original retained
    assert address in variants
    # Some generated forms
    assert any("46а" in v.lower() for v in variants)
    assert any("дом 46" in v.lower() for v in variants)
    assert any("building 46" in v.lower() for v in variants)


def test_generate_building_designator_variants(generator):
    address = "дом 12"
    variants = generator.generate_building_designator_variants(address)

    assert address in variants
    assert any("house 12" in v.lower() for v in variants)
    assert any("bldg." in v.lower() for v in variants)


def test_generate_comprehensive_variants(generator):
    variants = generator.generate_comprehensive_variants(
        base_address="бульвар Морской, 46",
        street_name="бульвар Морской",
        building_number="46"
    )
    assert "rus" in variants
    assert "ukr" in variants
    assert "eng" in variants

    # Must generate some transliterated English variant
    assert any("Morskoi" in v or "Morskyi" in v for v in variants["eng"])


@pytest.mark.parametrize(
    "address,expected_street,expected_number",
    [
        ("ул. Ленина, 46", "ул. Ленина", "46"),
        ("дом 25", "", "25"),
        ("проспект Победы, д. 12а", "проспект Победы", "12а"),
        ("no building here", None, None),
    ]
)
def test_parse_address(generator, address, expected_street, expected_number):
    street, number = generator.parse_address(address)
    assert street == expected_street
    assert number == expected_number
