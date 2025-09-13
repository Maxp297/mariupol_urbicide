import pytest
from unittest.mock import patch, MagicMock
from scripts.toponymic_lookup_service import ToponymicLookup, AddressVariant

@pytest.fixture
def mocked_lookup():
    with patch('scripts.toponymic_lookup_service.psycopg2.connect')  as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        lookup_instance = ToponymicLookup()
        
        yield lookup_instance, mock_cursor


def test_get_all_variants(mocked_lookup):
    lookup, mock_cursor = mocked_lookup

    mock_data = [{
        'name_text': 'проспект мира', 'language_code': 'ru', 'script_code': 'Cyrl',
        'administrative_period': 'occupation', 'confidence_score': 0.9,
        'source_document': 'doc1.pdf', 'evidence_type': 'media_report', 'metadata': {}
    }]
    mock_cursor.fetchall.return_value = mock_data

    variants = lookup.get_all_variants('проспект мира')

    assert len(variants) == 1
    assert isinstance(variants[0], AddressVariant)
    assert variants[0].name_text == 'проспект мира'

def test_normalize_address(mocked_lookup):
    lookup, _ = mocked_lookup
    variants_data = [
        AddressVariant('пр. Мира', 'ru', 'Cyrl', 'soviet', 0.7, '', '', {}),
        AddressVariant('проспект Миру', 'uk', 'Cyrl', 'pre-war', 0.95, '', '', {}),
        AddressVariant('Peace Avenue', 'en', 'Latn', 'pre-war', 0.8, '', '', {})
    ]

    with patch.object(lookup, 'get_all_variants', return_value=variants_data) as mock_get_variants:
        normalized = lookup.normalize_address('пр. Мира')
        mock_get_variants.assert_called_once_with('пр. Мира', include_fuzzy=True)
        # highest confidence
        assert normalized == 'проспект Миру'

MOCK_DB_CANDIDATES = [
    {'name_text': 'проспект Миру', 'language_code': 'uk', 'script_code': 'Cyrl', 'administrative_period': 'pre-war', 'confidence_score': 0.9, 'source_document': '', 'evidence_type': '', 'metadata': {}},
    {'name_text': 'проспект Металлургов', 'language_code': 'ru', 'script_code': 'Cyrl', 'administrative_period': 'soviet', 'confidence_score': 0.8, 'source_document': '', 'evidence_type': '', 'metadata': {}},
    {'name_text': 'вулиця Зелінського', 'language_code': 'uk', 'script_code': 'Cyrl', 'administrative_period': 'pre-war', 'confidence_score': 0.9, 'source_document': '', 'evidence_type': '', 'metadata': {}},
    {'name_text': 'проспект Мира', 'language_code': 'ru', 'script_code': 'Cyrl', 'administrative_period': 'occupation', 'confidence_score': 0.85, 'source_document': '', 'evidence_type': '', 'metadata': {}},
]

@pytest.mark.parametrize(
    "search_term, threshold, limit, mock_db_data, expected_names",
    [
        ("Проспект Мир", 0.8, 5, MOCK_DB_CANDIDATES, ['проспект Миру', 'проспект Мира']),
        ("Проспект Мир", 0.8, 1, MOCK_DB_CANDIDATES, ['проспект Миру']),
        ("Проспект Мир", 0.98, 5, MOCK_DB_CANDIDATES, []),
        ("any address", 0.8, 5, [], []),
    ],
    ids=[
        "finds_and_sorts",
        "respects_limit",
        "respects_threshold",
        "no_db_candidates"
    ]
)
def test_fuzzy_match(mocked_lookup, search_term, threshold, limit, mock_db_data, expected_names):
    lookup, mock_cursor = mocked_lookup
    mock_cursor.fetchall.return_value = mock_db_data

    matches = lookup.fuzzy_match(search_term, threshold=threshold, limit=limit)

    result_names = [variant.name_text for variant, _ in matches]

    assert result_names == expected_names


def test_get_statistics(mocked_lookup):
    """Test fetching database statistics."""
    lookup, mock_cursor = mocked_lookup
    
    mock_cursor.fetchone.side_effect = [
        {'count': 1500}, # Total streets
        {'count': 4500}, # Total variants
    ]
    mock_cursor.fetchall.side_effect = [
        [('ru', 2000), ('uk', 2500)], # By language
        [('media_report', 3000), ('osm', 1500)], # By evidence type
        [('occupation', 3000), ('pre-war', 1500)] # By period
    ]

    stats = lookup.get_statistics()

    assert stats['total_streets'] == 1500
    assert stats['total_variants'] == 4500
    assert stats['by_language']['ru'] == 2000
    assert stats['by_evidence_type']['media_report'] == 3000
    assert stats['by_period']['occupation'] == 3000
