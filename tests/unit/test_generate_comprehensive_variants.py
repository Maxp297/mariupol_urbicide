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


@pytest.mark.parametrize(
    "address,expected_abbrevs",
    [
        ("бульвар Морской", ["б-р", "blvd"]),
        ("улица Ленина", ["ул.", "st"]),
        ("проспект Победы", ["пр-т", "ave"]),
        ("переулок Горького", ["пер.", "lane"]),
        ("площадь Свободы", ["пл.", "square"]),
        ("набережная Речная", ["наб.", "emb"]),
        ("шоссе Киевское", ["ш.", "hwy"]),
        ("тупик Лесной", ["туп.", "cul-de-sac"]),
        ("неизвестная дорога", []),
    ],
)
def test_generate_abbreviation_variants(generator, address, expected_abbrevs):
    variants = generator.generate_abbreviation_variants(address, "rus")

    assert address in variants

    for abbrev in expected_abbrevs:
        assert any(abbrev in v.lower() for v in variants)


@pytest.mark.parametrize(
    "address,expected_patterns",
    [
        ("ул. Ленина, 46", ["46а", "дом 46", "№46", "Building 46"]),
        ("ул. Ленина, 46а", ["46", "д. 46", "будинок 46а"]),
        ("ул. Ленина, 46/1", ["46", "46-й", "46/1-ий", "д. 46/1"]),
        ("ул. Ленина, 46-2", ["46", "46а"]),
        ("ул. Ленина, 46 к.1", ["46", "46-ий к.1"]),
        ("ул. Ленина, 46 корп.1", ["46", "корп."]),
    ],
)
def test_generate_number_variants(generator, address, expected_patterns):
    variants = generator.generate_number_variants(address)

    assert address in variants

    for pattern in expected_patterns:
        assert any(pattern.lower() in v.lower() for v in variants)


@pytest.mark.parametrize(
    "address,expected_keywords",
    [
        ("дом 12", ["д.", "house", "bldg"]),
        ("будинок 5", ["буд.", "house", "building"]),
        ("корпус 3", ["к.", "corp"]),
        ("строение 8", ["стр.", "structure"]),
        ("улица Свободы 15", []),
    ],
)
def test_generate_building_designator_variants(generator, address, expected_keywords):
    variants = generator.generate_building_designator_variants(address)

    assert address in variants

    for keyword in expected_keywords:
        assert any(keyword in v.lower() for v in variants)


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
