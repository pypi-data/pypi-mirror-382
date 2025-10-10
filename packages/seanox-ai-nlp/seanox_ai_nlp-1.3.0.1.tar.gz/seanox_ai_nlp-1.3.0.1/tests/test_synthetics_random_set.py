# tests/test_synthetics_random_set.py

from seanox_ai_nlp.synthetics.synthetics import _random_set

import itertools

PATTERN_SYMBOLS = ['a', 'b', 'c', 'd']
PATTERN_COMBINATIONS = []
for index in range(1, len(PATTERN_SYMBOLS) + 1):
    perms = itertools.permutations(PATTERN_SYMBOLS, index)
    for perm in perms:
        PATTERN_COMBINATIONS.append(list(perm))


def test_synthetics_random_set_01():
    results = [_random_set(PATTERN_SYMBOLS) for _ in range(15)]
    # All entries must be as long as PATTERN_SYMBOLS
    assert all(len(result) == len(PATTERN_SYMBOLS) for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_set_02():
    results = [_random_set(PATTERN_SYMBOLS, -1) for _ in range(15)]
    # All entries must be as long as PATTERN_SYMBOLS
    assert all(len(result) == len(PATTERN_SYMBOLS) for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_set_03():
    results = [_random_set(PATTERN_SYMBOLS, -2) for _ in range(15)]
    # All entries must be as long as PATTERN_SYMBOLS
    assert all(len(result) == len(PATTERN_SYMBOLS) for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_set_04():
    results = [_random_set(PATTERN_SYMBOLS, 0) for _ in range(15)]
    # Each entry must be empty lists
    assert all(len(result) == 0 for result in results)


def test_synthetics_random_set_05():
    results = [_random_set(PATTERN_SYMBOLS, 1) for _ in range(15)]
    # Each entry must be 1 long
    assert all(len(result) == 1 for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_set_06():
    results = [_random_set(PATTERN_SYMBOLS, 2) for _ in range(15)]
    # Each entry must be 2 long
    assert all(len(result) == 2 for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1


def test_synthetics_random_set_07():
    results = [_random_set(PATTERN_SYMBOLS, 20) for _ in range(15)]
    # All entries must be as long as PATTERN_SYMBOLS
    assert all(len(result) == len(PATTERN_SYMBOLS) for result in results)
    # Each entry must appear in PATTERN_COMBINATIONS
    assert all(item in PATTERN_COMBINATIONS for item in results)
    # At least one entry differs from another
    results = [''.join(result) for result in results]
    assert len(set(results)) > 1
