# tests/test_synthetics_annotate.py

from seanox_ai_nlp.synthetics.synthetics import _annotate


def test_synthetics_annotate_01():
    assert "" == _annotate()
    assert "" == _annotate("")
    assert "" == _annotate("", "")
    assert "A" == _annotate("A")
    assert "A" == _annotate("A", "")
    assert "" == _annotate("", "b")
    assert "[[[b]]]A[[[-]]]" == _annotate("A", "b")
    assert "[[[B]]] A[[[-]]]" == _annotate(" A", "B")
    assert "[[[B]]] a[[[-]]]" == _annotate(" a", " B")
    assert "[[[B]]] a [[[-]]]" == _annotate(" a ", " B ")
    assert "[[[B]]]a [[[-]]]" == _annotate("a ", "B ")
    assert " " == _annotate(" ", "b")
    assert "  " == _annotate("  ", "b")
    assert "\t" == _annotate("\t", "b")
    assert "\r" == _annotate("\r", "b")
    assert "\n" == _annotate("\n", "b")
