# tests/test_synthetics_random_range.py

from seanox_ai_nlp.synthetics.synthetics import _random_range

import itertools

PATTERN_SYMBOLS = ['a', 'b', 'c', 'd']
PATTERN_COMBINATIONS = []
for index in range(1, len(PATTERN_SYMBOLS) + 1):
    perms = itertools.permutations(PATTERN_SYMBOLS, index)
    for perm in perms:
        PATTERN_COMBINATIONS.append(list(perm))


def test_synthetics_random_range_01():
    results = [_random_range(PATTERN_SYMBOLS) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS) for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS) for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_range_02():
    results = [_random_range(PATTERN_SYMBOLS, -1) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS) for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS) for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_range_03():
    results = [_random_range(PATTERN_SYMBOLS, -2) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS) for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS) for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_range_04():
    results = [_random_range(PATTERN_SYMBOLS, 0) for _ in range(15)]
    # Each entry must be empty lists
    assert all(len(result) == 0 for result in results)


def test_synthetics_random_range_05():
    results = [_random_range(PATTERN_SYMBOLS, 1) for _ in range(15)]
    # Each entry must be 1 long
    assert all(len(result) == 1 for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_range_06():
    results = [_random_range(PATTERN_SYMBOLS, 2) for _ in range(15)]
    # Each entry must be 1 or 2 long
    assert all(len(result) in [1, 2] for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_range_07():
    results = [_random_range(PATTERN_SYMBOLS, 20) for _ in range(15)]
    # Each entry is at most as long as PATTERN_SYMBOLS
    assert all(len(result) <= len(PATTERN_SYMBOLS) for result in results)
    # At least one entry is shorter than PATTERN_SYMBOLS
    assert any(len(item) < len(PATTERN_SYMBOLS) for item in results)
    # Each entry is longer than 0
    assert all(len(item) > 0 for item in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1
