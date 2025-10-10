# tests/tests_synthetics_validation.py

from seanox_ai_nlp.synthetics import synthetics, TemplateException
from pathlib import Path

import re
import pytest

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")


def test_synthetics_validation_0x():
    pattern = re.compile(r'synthetics_validation_0\d\.yaml')
    for file in Path(TESTS_PATH).iterdir():
        if pattern.fullmatch(file.name):
            synthetics(TESTS_PATH, file.name)


def test_synthetics_validation_11():
    synthetics(TESTS_PATH, "synthetics_validation_11.yaml")


def test_synthetics_validation_12():
    with pytest.raises(TemplateException) as exception:
        synthetics(TESTS_PATH, "synthetics_validation_12.yaml")
    assert "ValidationError" in str(exception.value)
    assert "c: {'ö ö ö': None} is not valid under any of the given schemas" in str(exception.value)


def test_synthetics_validation_13():
    with pytest.raises(TemplateException) as exception:
        synthetics(TESTS_PATH, "synthetics_validation_13.yaml")
    assert "ValidationError" in str(exception.value)
    assert "{'xxx': None} is not of type 'array', 'null'" in str(exception.value)


def test_synthetics_validation_14():
    with pytest.raises(TemplateException) as exception:
        synthetics(TESTS_PATH, "synthetics_validation_14.yaml")
    assert "ValidationError" in str(exception.value)
    assert "{'xxx': [{'xxx': 1}]} is not of type 'array', 'null'" in str(exception.value)


def test_synthetics_validation_15():
    with pytest.raises(TemplateException) as exception:
        synthetics(TESTS_PATH, "synthetics_validation_15.yaml")
    assert "ValidationError" in str(exception.value)
    assert "templates[6].template: None is not of type 'string'" in str(exception.value)


def test_synthetics_validation_16():
    synthetics(TESTS_PATH, "synthetics_validation_16.yaml")


def test_synthetics_validation_17():
    synthetics(TESTS_PATH, "synthetics_validation_17.yaml")


def test_synthetics_validation_18():
    synthetics(TESTS_PATH, "synthetics_validation_18.yaml")
