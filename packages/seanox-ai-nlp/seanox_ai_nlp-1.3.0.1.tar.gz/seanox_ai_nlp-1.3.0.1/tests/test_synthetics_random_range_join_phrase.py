# tests/test_synthetics_random_range_join_phrase.py

from seanox_ai_nlp.synthetics.synthetics import _random_range_join_phrase

import itertools

PATTERN_SYMBOLS = ['a', 'b', 'c', 'd']
PATTERN_SYMBOLS_DEFAULT = ", ".join(PATTERN_SYMBOLS)
PATTERN_SYMBOLS_CUSTOM = "_".join(PATTERN_SYMBOLS)
PATTERN_COMBINATIONS_DEFAULT = []
PATTERN_COMBINATIONS_CUSTOM = []
for index in range(1, len(PATTERN_SYMBOLS) + 1):
    perms = itertools.permutations(PATTERN_SYMBOLS, index)
    for perm in perms:
        PATTERN_COMBINATIONS_DEFAULT.append(", ".join(perm))
        PATTERN_COMBINATIONS_CUSTOM.append("_".join(perm))


def test_synthetics_random_range_join_phrase_01():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS_DEFAULT) for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS_DEFAULT) for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item.replace(" ! ", "_") in PATTERN_COMBINATIONS_DEFAULT for item in results)
    # At least one entry differs from another
    assert len(set(results)) > 1


def test_synthetics_random_range_join_phrase_02():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS, "_", " ! ", -1) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS_CUSTOM) + 3 for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS_CUSTOM) + 3 for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item.replace(" ! ", "_") in PATTERN_COMBINATIONS_CUSTOM for item in results)
    # At least one entry differs from another
    assert len(set(results)) > 1


def test_synthetics_random_range_join_phrase_03():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS, "_", " ! ", -2) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS_CUSTOM) + 3 for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS_CUSTOM) + 3 for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item.replace(" ! ", "_") in PATTERN_COMBINATIONS_CUSTOM for item in results)
    # At least one entry differs from another
    assert len(set(results)) > 1


def test_synthetics_random_range_join_phrase_04():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS, "_", " ! ", 0) for _ in range(15)]
    # Each entry must be empty lists
    assert all(len(result) == 0 for result in results)


def test_synthetics_random_range_join_phrase_05():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS, "_", " ! ", 1) for _ in range(15)]
    # Each entry must be 1 long
    assert all(len(result) == 1 for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS_CUSTOM for item in results)
    # At least one entry differs from another
    assert len(set(results)) > 1


def test_synthetics_random_range_join_phrase_06():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS, "_", " ! ", 2) for _ in range(15)]
    # Each entry must be 1 (a) or 3 (a_b) long
    assert all(len(result) in [1, 2 + 3] for result in results)
    assert any(len(item) == 1 for item in results)
    assert any(len(item) == 2 + 3 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item.replace(" ! ", "_") in PATTERN_COMBINATIONS_CUSTOM for item in results)
    # At least one entry differs from another
    assert len(set(results)) > 1


def test_synthetics_random_range_join_phrase_07():
    results = [_random_range_join_phrase(PATTERN_SYMBOLS, "_", " ! ", 20) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS_CUSTOM) + 3 for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS_CUSTOM) + 3 for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item.replace(" ! ", "_") in PATTERN_COMBINATIONS_CUSTOM for item in results)
    # At least one entry differs from another
    assert len(set(results)) > 1
