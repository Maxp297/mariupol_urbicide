import pytest
from scripts.forensic_fuzzy_matcher import ForensicFuzzyMatcher

@pytest.fixture
def matcher():
    return ForensicFuzzyMatcher()

@pytest.mark.parametrize(
    "input_text,expected_output",
    [
        # None
        (None, ""),
        # Empty string
        ("", ""),
        # Basic Cyrillic text, lowercase normalization
        ("Привет", "привет"),
        # Normalize ё -> е
        ("ёлка", "елка"),
        # Remove Ukrainian quotes
        ("«Привет»", "привет"),
        # Standardize dashes
        ("Привет — мир", "привет - мир"),
        # Normalize whitespace
        ("  Привет   мир  ", "привет мир"),
        # String with only spaces
        ("    ", ""),
        # Already normalized text
        ("привет мир", "привет мир"),
        # Mixed case and punctuation
        ("  «Ёжик—малый»  ", "ежик-малый"),
        # Non-string input (int, should convert to string)
        (12345, "12345"),
    ]
)
def test_preprocess_cyrillic_text(matcher, input_text, expected_output):
    result = matcher.preprocess_cyrillic_text(input_text)
    assert result == expected_output


@pytest.mark.parametrize(
    "text1,text2,expected_composite,tolerance",
    [
        # Exact match
        ("Морской бульвар, 46", "Морской бульвар, 46", 1.0, 0.01),
        # Small numeric difference
        ("Морской бульвар, 46", "Морской бульвар, 45", 0.9, 0.05),
        # Different street
        ("Морской бульвар, 46", "Комсомольский бульвар, 99", 0.6, 0.1),
        # Mixed Latin/Cyrillic
        ("Morsky Boulevard, 46", "Морской бульвар, 46", 0.2, 0.15),
        # Reordered tokens
        ("46 Морской бульвар", "Морской бульвар, 46", 0.9, 0.05),
    ]
)
def test_calculate_multi_metric_confidence(matcher, text1, text2, expected_composite, tolerance):
    metrics = matcher.calculate_multi_metric_confidence(text1, text2)
    assert 'composite' in metrics
    # Check composite score approximately
    assert metrics['composite'] == pytest.approx(expected_composite, abs=tolerance)


def test_classify_confidence_level(matcher):
    assert matcher.classify_confidence_level(0.9) == 'high'
    assert matcher.classify_confidence_level(0.75) == 'medium'
    assert matcher.classify_confidence_level(0.6) == 'low'
    assert matcher.classify_confidence_level(0.4) == 'very_low'


@pytest.mark.parametrize(
    "query,candidates,expected_top_score,expected_top_level",
    [
        # Exact match
        ("Морской бульвар, 46", ["Морской бульвар, 46"], 1, "high"),
        # Partial match
        ("Морской бульвар, 46", ["Морской бульвар, 45"], 0.95, "high"),
        # No match
        ("Морской бульвар, 46", ["Комсомольский бульвар, 99"], 0.65, "low"),
        # Multiple candidates, best match first
        ("Морской бульвар, 46", ["Комсомольский бульвар, 46", "Морской бульвар, 46"], 1, "high"),
        # Mixed Cyrillic/Latin
        ("Morsky Boulevard, 46", ["Морской бульвар, 46"], 0.25, "very_low"),
        # Reordered tokens
        ("Морской бульвар, 46", ["46 Морской бульвар"], 0.9, "high"),
    ]
)
def test_fuzzy_match_addresses_single(matcher, query, candidates, expected_top_score, expected_top_level):
    results = matcher.fuzzy_match_addresses(query, candidates, limit=1)
    assert len(results) == 1
    score = results[0]['confidence_score']
    assert score == pytest.approx(expected_top_score, abs=0.04)
    assert results[0]['confidence_level'] == expected_top_level


@pytest.mark.parametrize(
    "query,candidates,expected_levels,expected_scores",
    [
        # 3 candidates, all exact matches
        (
            "Морской бульвар, 46",
            ["Морской бульвар, 46", "Морской бульвар, 46", "Морской бульвар, 46"],
            ["high", "high", "high"],
            [1, 1, 1]
        ),
        # 4 candidates: exact, partial, no match, partial
        (
            "Морской бульвар, 46",
            ["Морской бульвар, 46", "Морской бульвар, 45", "Комсомольский бульвар, 99", "Морской бульвар, 45"],
            ["high", "high", "high"],
            [1, 0.95, 0.95]
        ),
        # 2 candidates, limit 3 (should only return 2)
        (
            "Морской бульвар, 46",
            ["Морской бульвар, 46", "Комсомольский бульвар, 99"],
            ["high", "low"],
            [1, 0.65]
        ),
        # 5 candidates, mixed
        (
            "Морской бульвар, 46",
            [
                "Комсомольский бульвар, 99",
                "Морской бульвар, 45",
                "Морской бульвар, 46",
                "Комсомольский бульвар, 46",
                "Морской бульвар, 46"
            ],
            ["high", "high", "high"],
            [1, 1, 0.95]
        ),
    ]
)
def test_fuzzy_match_addresses_top3(matcher, query, candidates, expected_levels, expected_scores):
    results = matcher.fuzzy_match_addresses(query, candidates, limit=3)
    assert len(results) == len(expected_levels)
    for i, result in enumerate(results):
        score = result['confidence_score']
        assert score == pytest.approx(expected_scores[i], abs=0.04)
        assert result['confidence_level'] == expected_levels[i]
    # Ensure results are sorted by confidence_score descending
    scores = [r['confidence_score'] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_generate_matching_report(matcher):
    results = [
        {'confidence_level': 'high', 'confidence_score': 0.9, 'requires_manual_review': False, 'likely_false_positive': False},
        {'confidence_level': 'medium', 'confidence_score': 0.75, 'requires_manual_review': True, 'likely_false_positive': False},
        {'confidence_level': 'low', 'confidence_score': 0.6, 'requires_manual_review': True, 'likely_false_positive': False},
        {'confidence_level': 'very_low', 'confidence_score': 0.4, 'requires_manual_review': False, 'likely_false_positive': True},
    ]
    report = matcher.generate_matching_report(results)
    assert report['total_matches'] == 4
    assert report['confidence_distribution']['high'] == 1
    assert report['requires_manual_review'] == 2
    assert report['likely_false_positives'] == 1
