# tests/test_synthetics_empty.py

from pathlib import Path

from seanox_ai_nlp.synthetics import synthetics

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")


def test_synthetics_empty_01():
    synthetic = synthetics(
        TESTS_PATH, "synthetics_empty_1.yaml", {}, {}
    )
    assert synthetic is not None
    assert synthetic.text == ""


def test_synthetics_empty_02():
    synthetic = synthetics(
        TESTS_PATH, "synthetics_empty_2.yaml", {}, {}
    )
    assert synthetic is not None
    assert synthetic.text == ""
