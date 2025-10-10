# tests/test_units_units.py

from seanox_ai_nlp.units import units
from typing import Optional, NamedTuple
from time import perf_counter
from pathlib import Path
from spacy.cli import download

import pytest
import os
import pathlib
import importlib

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")

if importlib.util.find_spec("en_core_web_md") is None:
    download("en_core_web_md")


class Unit(NamedTuple):
    label: str
    start: int
    end: int
    text: str
    categories: tuple[str, ...]
    unit: str
    value: Optional[str] = None


_TEST_CASE_01 = (
    " Die Batterie h\u00e4lt ca. 10h bei \u221220.5 \u00b0C."
    " Das Solarpanel produziert etwa 1.2 \u00d7 10^3W unter optimalen Bedingungen."
    " Mit einem Gewicht von \u223c2.3 kg ist das Ger\u00e4t leicht tragbar."
    " Der Reifendruck liegt bei 2500hPa, empfohlen sind aber nur 2.5 bar."
    " Die Entfernung zum n\u00e4chsten Ladepunkt betr\u00e4gt rund 18 km, bei einer Durchschnittsgeschwindigkeit von 50km/h."
    " Einige Nutzer berichten sogar von 21.5kWh Verbrauch auf 100km."

    " Die Verpackung hat Ma\u00dfe von 35\u00d722\u00d712 cm und ein Volumen von ca. 9.24 l."
    " Der L\u00fcfter erzeugt 34dB Ger\u00e4uschpegel unter Last."
    " Laut Hersteller betr\u00e4gt die Akkulaufzeit 12\u201314 h je nach Nutzung."
    " Das Ger\u00e4t arbeitet in einem Temperaturbereich zwischen \u221210 \u00b0C und +45 \u00b0C."
    " Der Stromverbrauch liegt bei max. 65 W, die Ladezeit bei 3.5h \u00fcber ein Netzteil mit 20V und 3.25A."
    " Die GPS-Genauigkeit betr\u00e4gt etwa \u00b15 m."
    " Bei Windst\u00e4rken \u00fcber 60 km/h sollte das Ger\u00e4t gesichert werden."

    " Das Plato befand sich auf 550 m H\u00f6he bei einem relativen Luftdruck von 960hPa."
    " Die Signalreichweite lag bei bis zu 120 m auf freier Fl\u00e4che."
    " Nach dem Update verbesserte sich die Bootzeit um 2.3 s, und die durchschnittliche CPU-Temperatur sank auf 36.5 \u00b0C."
    " Die Ladegeschwindigkeit wurde mit 0.8C angegeben."
    " Der Preis liegt aktuell bei etwa 299.99 \u20ac."

    " Das Display misst 15.6 \" bei einer Aufl\u00f6sung von 1920\u00d71080 px."
    " Ein Node vom Kubernetes-Cluster mind. benötigt 1vCore und 512MiB."

    " Das Produkt misst 10\u00d720\u00d730 cm und hat ein Volumen von 6 l."
    " Der Energiebedarf liegt bei ca. 5 - 10 kWh"
    " Der Durchmesser misst ca. 1\u002d11nm (Hyphen-Minus)"
    " Der Durchmesser misst ca. 2 \u2013 22nm (En Dash)"
    " Der Durchmesser misst ca. 3\u2014 33nm (Em Dash)"
    " Der Durchmesser misst ca. 4 \u221244nm (Minus Sign)"

    " Die Difference betr\u00e4gt ca. \u002d11nm (Hyphen-Minus)"
    " Die Difference betr\u00e4gt ca. \u2013 22nm (En Dash)"
    " Die Difference betr\u00e4gt ca. \u2014 33nm (Em Dash)"
    " Die Difference betr\u00e4gt ca. \u221244nm (Minus Sign)"
)


@pytest.mark.parametrize("text", [_TEST_CASE_01])
def test_units_01(text):
    expected = [
        Unit(label='MEASURE', start=23, end=26, text='10h', categories=('time',), unit='h', value='10'),
        Unit(label='UNIT', start=38, end=39, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='MEASURE', start=72, end=83, text='1.2 × 10^3W', categories=('power',), unit='W', value='1.2 × 10^3'),
        Unit(label='MEASURE', start=136, end=142, text='2.3 kg', categories=('mass',), unit='kg', value='2.3'),
        Unit(label='MEASURE', start=199, end=206, text='2500hPa', categories=('time',), unit='hPa', value='2500'),
        Unit(label='MEASURE', start=232, end=239, text='2.5 bar', categories=('pressure',), unit='bar', value='2.5'),
        Unit(label='MEASURE', start=292, end=297, text='18 km', categories=('length',), unit='km', value='18'),
        Unit(label='MEASURE', start=342, end=348, text='50km/h', categories=('length', 'time'), unit='km/h', value='50'),
        Unit(label='MEASURE', start=384, end=391, text='21.5kWh', categories=('energy',), unit='kWh', value='21.5'),
        Unit(label='MEASURE', start=406, end=411, text='100km', categories=('length',), unit='km', value='100'),
        Unit(label='MEASURE', start=441, end=452, text='35×22×12 cm', categories=('length',), unit='cm', value='35×22×12'),
        Unit(label='MEASURE', start=477, end=483, text='9.24 l', categories=('volume',), unit='l', value='9.24'),
        Unit(label='MEASURE', start=504, end=508, text='34dB', categories=('acoustics',), unit='dB', value='34'),
        Unit(label='MEASURE', start=576, end=583, text='12–14 h', categories=('time',), unit='h', value='12–14'),
        Unit(label='UNIT', start=620, end=622, text='in', categories=('length',), unit='in', value=None),
        Unit(label='UNIT', start=661, end=662, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT', start=672, end=673, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='MEASURE', start=709, end=713, text='65 W', categories=('power',), unit='W', value='65'),
        Unit(label='MEASURE', start=732, end=736, text='3.5h', categories=('time',), unit='h', value='3.5'),
        Unit(label='MEASURE', start=759, end=762, text='20V', categories=('electricity',), unit='V', value='20'),
        Unit(label='MEASURE', start=767, end=772, text='3.25A', categories=('electricity',), unit='A', value='3.25'),
        Unit(label='MEASURE', start=807, end=811, text='±5 m', categories=('length',), unit='m', value='±5'),
        Unit(label='MEASURE', start=834, end=841, text='60 km/h', categories=('length', 'time'), unit='km/h', value='60'),
        Unit(label='MEASURE', start=903, end=908, text='550 m', categories=('length',), unit='m', value='550'),
        Unit(label='MEASURE', start=948, end=954, text='960hPa', categories=('time',), unit='hPa', value='960'),
        Unit(label='MEASURE', start=992, end=997, text='120 m', categories=('length',), unit='m', value='120'),
        Unit(label='MEASURE', start=1066, end=1071, text='2.3 s', categories=('time',), unit='s', value='2.3'),
        Unit(label='UNIT', start=1129, end=1130, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='MEASURE', start=1166, end=1170, text='0.8C', categories=('electricity',), unit='C', value='0.8'),
        Unit(label='MEASURE', start=1243, end=1249, text='15.6 "', categories=('length',), unit='"', value='15.6'),
        Unit(label='MEASURE', start=1274, end=1286, text='1920×1080 px', categories=('graphics', 'it'), unit='px', value='1920×1080'),
        Unit(label='MEASURE', start=1335, end=1341, text='1vCore', categories=('amount', 'it', 'processing'), unit='vCore', value='1'),
        Unit(label='MEASURE', start=1346, end=1352, text='512MiB', categories=('acoustics', 'it', 'storage'), unit='MiB', value='512'),
        Unit(label='MEASURE', start=1372, end=1383, text='10×20×30 cm', categories=('length',), unit='cm', value='10×20×30'),
        Unit(label='MEASURE', start=1408, end=1411, text='6 l', categories=('volume',), unit='l', value='6'),
        Unit(label='MEASURE', start=1445, end=1455, text='5 - 10 kWh', categories=('energy',), unit='kWh', value='5 - 10'),
        Unit(label='MEASURE', start=1482, end=1488, text='1-11nm', categories=('length',), unit='nm', value='1-11'),
        Unit(label='MEASURE', start=1530, end=1538, text='2 – 22nm', categories=('length',), unit='nm', value='2 – 22'),
        Unit(label='MEASURE', start=1575, end=1582, text='3— 33nm', categories=('length',), unit='nm', value='3— 33'),
        Unit(label='UNIT', start=1584, end=1586, text='Em', categories=('length',), unit='Em', value=None),
        Unit(label='MEASURE', start=1619, end=1626, text='4 −44nm', categories=('length',), unit='nm', value='4 −44'),
        Unit(label='MEASURE', start=1667, end=1672, text='-11nm', categories=('length',), unit='nm', value='-11'),
        Unit(label='MEASURE', start=1717, end=1721, text='22nm', categories=('length',), unit='nm', value='22'),
        Unit(label='MEASURE', start=1761, end=1765, text='33nm', categories=('length',), unit='nm', value='33'),
        Unit(label='UNIT', start=1767, end=1769, text='Em', categories=('length',), unit='Em', value=None),
        Unit(label='MEASURE', start=1804, end=1808, text='44nm', categories=('length',), unit='nm', value='44')
    ]
    actual = [
        Unit(
            label=entity.label,
            start=entity.start,
            end=entity.end,
            text=entity.text,
            categories=entity.categories,
            unit=entity.unit,
            value=entity.value
        )
        for entity in units(text)
    ]
    print()
    print(f",{os.linesep}".join([str(unit) for unit in actual]))
    assert actual == expected, f"\nExpected:\n{expected}\n\nGot:\n{actual}"


_TEST_CASE_02 = (
    " The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph)."
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)


@pytest.mark.parametrize("text", [_TEST_CASE_02])
def test_units_02(text):
    expected = [
        Unit(label='MEASURE', start=55, end=69, text='900 - 950 km/h', categories=('length', 'time'), unit='km/h', value='900 - 950'),
        Unit(label='MEASURE', start=71, end=78, text='559 mph', categories=('length', 'time'), unit='mph', value='559'),
        Unit(label='UNIT', start=107, end=109, text='in', categories=('length',), unit='in', value=None),
        Unit(label='UNIT', start=131, end=135, text='km/h', categories=('length', 'time'), unit='km/h', value=None),
        Unit(label='UNIT', start=157, end=160, text='mph', categories=('length', 'time'), unit='mph', value=None)
    ]
    actual = [
        Unit(
            label=entity.label,
            start=entity.start,
            end=entity.end,
            text=entity.text,
            categories=entity.categories,
            unit=entity.unit,
            value=entity.value
        )
        for entity in units(text)
    ]
    print()
    print(f",{os.linesep}".join([str(unit) for unit in actual]))
    assert actual == expected, f"\nExpected:\n{expected}\n\nGot:\n{actual}"


def test_units_benchmark_01():
    text = _TEST_CASE_01 + _TEST_CASE_02
    start = perf_counter()
    entities = units(text)
    end = perf_counter()

    print()
    print(f"Benchmark text: {len(text)} characters")
    print(f"Benchmark detections: {len(entities)} units + measures")
    print(f"Benchmark duration: {(end - start) * 1000:.2f} ms")


def test_units_benchmark_02():
    text = _TEST_CASE_01 + _TEST_CASE_02
    text = text * 10
    start = perf_counter()
    entities = units(text)
    end = perf_counter()

    print()
    print(f"Benchmark text: {len(text)} characters")
    print(f"Benchmark detections: {len(entities)} units + measures")
    print(f"Benchmark duration: {(end - start) * 1000:.2f} ms")


def test_units_usage_01(monkeypatch):
    monkeypatch.chdir(EXAMPLES_PATH / "units")
    script_path = pathlib.Path("example-pandas.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")


def test_units_usage_02(monkeypatch):
    monkeypatch.chdir(EXAMPLES_PATH / "units")
    script_path = pathlib.Path("example-spaCy-component.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")


def test_units_usage_03(monkeypatch):
    monkeypatch.chdir(EXAMPLES_PATH / "units")
    script_path = pathlib.Path("example-spaCy-pipeline.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")
