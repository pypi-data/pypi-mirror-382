# tests/test_synthetics_synthetics.py

from seanox_ai_nlp.synthetics import synthetics, TemplateConditionException
from time import perf_counter
from pathlib import Path
from spacy.cli import download

import pathlib
import random
import copy
import json
import pytest
import re
import importlib

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")

if importlib.util.find_spec("en_core_web_md") is None:
    download("en_core_web_md")


def test_synthetics_usage_07():
    synthetics(
        TESTS_PATH,
        "synthetics_de_annotate.yaml",
        {
            "planet": "",
            "type": "",
            "diameter": 0,
            "turnover": 0,
            "moons": 0,
            "atmosphere": [],
            "characteristics": []
        }
    )


def test_synthetics_usage_08():
    with pytest.raises(TemplateConditionException) as exception:
        synthetics(
                TESTS_PATH,
                "synthetics_de_annotate.yaml"
            )
    assert re.search(
        r"Condition error \(NameError\): name '.*' is not defined",
        str(exception.value)
    )


def test_synthetics_benchmark_01():

    with open(TESTS_PATH / "synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)

    count_text = 0
    start = perf_counter()
    for data in datas:
        result = synthetics(TESTS_PATH, "synthetics_de_annotate.yaml", data)
        count_text += len(result.text)
    end = perf_counter()

    print()
    print(f"Benchmark text: {count_text} characters")
    print(f"Benchmark iterations: {len(datas)} x")
    print(f"Benchmark duration: {(end - start) * 1000:.2f} ms")


def test_synthetics_benchmark_02():

    with open(TESTS_PATH / "synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)

    count_text = 0
    scaled_datas = []
    for data in datas:
        for _ in range(500):
            scaled_datas.append(copy.deepcopy(data))
    random.shuffle(scaled_datas)

    print(len(scaled_datas))
    start = perf_counter()
    for data in scaled_datas:
        result = synthetics(TESTS_PATH, "synthetics_de_annotate.yaml", data)
        count_text += len(result.text)
    end = perf_counter()

    print()
    print(f"Benchmark text: {count_text} characters")
    print(f"Benchmark iterations: {len(scaled_datas)} x")
    print(f"Benchmark duration: {(end - start) * 1000:.2f} ms")


def test_synthetics_usage_01():
    with open(TESTS_PATH / "synthetics-planets_en.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(TESTS_PATH, "synthetics_en_annotate.yaml", data)
        print(synthetic)
        assert "@" not in synthetic.text


def test_synthetics_usage_02():
    with open(TESTS_PATH / "synthetics-planets_en.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(TESTS_PATH, "synthetics_en.yaml", data)
        print(synthetic)
        assert "@" not in synthetic.text


def test_synthetics_usage_03():
    with open(TESTS_PATH / "synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(TESTS_PATH, "synthetics_de_annotate.yaml", data)
        print(synthetic)
        assert "@" not in synthetic.text


def test_synthetics_usage_04():
    with open(TESTS_PATH / "synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(TESTS_PATH, "synthetics_de.yaml", data)
        print(synthetic)
        assert "@" not in synthetic.text


def test_synthetics_usage_05(monkeypatch):
    monkeypatch.chdir(EXAMPLES_PATH / "synthetics")
    script_path = pathlib.Path("example-pandas.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")


def test_synthetics_usage_06(monkeypatch):
    monkeypatch.chdir(EXAMPLES_PATH / "synthetics")
    script_path = pathlib.Path("example-spaCy-pipeline.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")
