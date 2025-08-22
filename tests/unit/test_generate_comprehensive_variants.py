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
        ("ёлка целиком", "Elka Tselikom"),
        ("Отъявленный", "Otiavlennyi"),
        ("щастья хочется", "Shchastia Khochetsia"),
        ("абwгдеёжz", "Abwgdeezhz")
    ]
)
def test_transliterate_russian(generator, input, expected):
    result = generator.transliterate_russian(input)
    assert result == expected