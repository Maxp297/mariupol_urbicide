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
