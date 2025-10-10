# examples/units/example-spaCy-pipeline-component.py
# Run: python -m spacy download en_core_web_md
#      python examples/units/example-spaCy-pipeline-component.py

import spacy
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.lang.en.stop_words import STOP_WORDS
from seanox_ai_nlp.units import units

Span.set_extension("value", default=None, force=True)
Span.set_extension("unit", default=None, force=True)
Span.set_extension("categories", default=None, force=True)

@spacy.language.Language.component("units_detector")
def units_detector(doc):

    units_spans = []

    # Detecting entities in text
    for units_entity in units(doc.text):
        span = doc.char_span(
            units_entity.start,
            units_entity.end,
            label=units_entity.label)

        # Theoretically, if the start and end positions of the units entity do not
        # align with spaCy's token boundaries, doc.char_span will return None, and
        # no span will be created.
        if not span:
            continue

        if not span:
            continue

        # Without semantic analysis, units that are actually stop words are also
        # found. These can be filtered out in a language-specific manner.
        if units_entity.label == "UNIT" and units_entity.unit in STOP_WORDS:
            continue

        # Extension of the span
        span._.value = units_entity.value
        span._.unit = units_entity.unit
        span._.categories = list(units_entity.categories)
        units_spans.append(span)

    # Store unit spans separately (instead of merging into doc.ents)
    doc.spans["units"] = filter_spans(units_spans)
    return doc

# Loading model and text
# and adding the units detector as a pipe
nlp = spacy.load("en_core_web_md")
nlp.add_pipe("units_detector", last=True)
text = (
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph)."
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)
doc = nlp(text)

# Formatted output
for ent in doc.ents:
    if ent.label_ in ["UNIT", "MEASURE"]:
        print(f"{ent.text:{20}} | label: {ent.label_:{10}} | value: {ent._.value or '':{10}} | unit: {ent._.unit:{5}} | categories: {ent._.categories}")
    else:
        print(f"{ent.text:{20}} | label: {ent.label_}")

# Output:
# Boeing               | label: ORG
# 747                  | label: PRODUCT
# 900 - 950 km/h       | label: MEASURE    | value: 900 - 950  | unit: km/h  | categories: ['length', 'time']
# 559 mph              | label: MEASURE    | value: 559        | unit: mph   | categories: ['length', 'time']
# in                   | label: UNIT       | value:            | unit: in    | categories: ['length']
# kilometers per hour  | label: TIME
# km/h                 | label: UNIT       | value:            | unit: km/h  | categories: ['length', 'time']
# mph                  | label: UNIT       | value:            | unit: mph   | categories: ['length', 'time']
