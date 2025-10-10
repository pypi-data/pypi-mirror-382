# tests/test_synthetics_custom_filters.py

from seanox_ai_nlp.synthetics import synthetics, TemplateException
from pathlib import Path

import pytest
import re

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")


def _a(text: str = "") -> str:
    return "_A_"


def _b(text: str = "") -> str:
    return "_B_"


def _c(text: str = "") -> str:
    return "_C_"


def test_synthetics_custom_filters_01():
    with pytest.raises(TemplateException) as exception:
        synthetics(
            TESTS_PATH,
            "synthetics_custom_filters.yaml",
            {},
            {}
        )
    assert "Template error (TemplateAssertionError): No filter named 'a'." in str(exception.value)


def test_synthetics_custom_filters_02():
    with pytest.raises(TemplateException) as exception:
        synthetics(
            TESTS_PATH,
            "synthetics_custom_filters.yaml",
            {},
            {"a": _a}
        )
    assert "Template error (TemplateAssertionError): No filter named 'b'." in str(exception.value)


def test_synthetics_custom_filters_03():
    synthetic = synthetics(
        TESTS_PATH,
        "synthetics_custom_filters.yaml",
        {},
        {"a": _a, "b": _b}
    )
    assert re.search(
        r"A: _A_ B: _B_ C: \[[\d, ]+\] D: \[[\d, ]+\]",
        str(synthetic.text)
    )


def test_synthetics_custom_filters_04():
    synthetic = synthetics(
        TESTS_PATH,
        "synthetics_custom_filters.yaml",
        {},
        {"a": _a, "b": _b, "random_range": _c}
    )
    assert re.search(
        r"A: _A_ B: _B_ C: \[[\d, ]+\] D: _C_",
        str(synthetic.text)
    )


def test_synthetics_custom_filters_05():
    synthetic = synthetics(
        TESTS_PATH,
        "synthetics_custom_filters.yaml",
        {},
        {"a": _a, "b": _b, " random_range": _c}
    )
    assert re.search(
        r"A: _A_ B: _B_ C: \[[\d, ]+\] D: \[[\d, ]+\]",
        str(synthetic.text)
    )


def test_synthetics_custom_filters_06():
    synthetic = synthetics(
        TESTS_PATH,
        "synthetics_custom_filters.yaml",
        {},
        {"a": _a, "b": _b, "random_range ": _c}
    )
    assert re.search(
        r"A: _A_ B: _B_ C: \[[\d, ]+\] D: \[[\d, ]+\]",
        str(synthetic.text)
    )
