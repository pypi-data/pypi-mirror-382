# tests/test_synthetics_normalize.py

from seanox_ai_nlp.synthetics.synthetics import _normalize


def test_synthetics_normalize_01():
    assert "" == _normalize()
    assert "" == _normalize("")
    assert "" == _normalize(" ")
    assert "" == _normalize("  ")
    assert "A" == _normalize(" A ")
    assert "A b" == _normalize(" A b ")
    assert "A b" == _normalize(" A  b ")
    assert "A b" == _normalize("A  b ")
    assert "A b" == _normalize("A  b")
    assert "A b" == _normalize("A b")
    assert "Ab" == _normalize("Ab")
