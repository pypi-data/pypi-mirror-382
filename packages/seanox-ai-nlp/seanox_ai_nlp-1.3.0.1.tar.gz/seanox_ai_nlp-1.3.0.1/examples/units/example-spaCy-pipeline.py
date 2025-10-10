# examples/units/example-spaCy-pipeline.py
# Run: python -m spacy download en_core_web_md
#      python examples/units/example-spaCy-pipeline.py

import spacy
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.lang.en.stop_words import STOP_WORDS
from seanox_ai_nlp.units import units

Span.set_extension("value", default=None, force=True)
Span.set_extension("unit", default=None, force=True)
Span.set_extension("categories", default=None, force=True)

# Loading model and text
nlp = spacy.load("en_core_web_md")
text = (
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph)."
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)
doc = nlp(text)

# Detecting entities in text
units_entities = units(text)
for units_entity in units_entities:
    span = doc.char_span(
        units_entity.start,
        units_entity.end,
        label=units_entity.label
    )

    # Theoretically, if the start and end positions of the units entity do not
    # align with spaCy's token boundaries, doc.char_span will return None, and
    # no span will be created.
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
    # Remove any overlapping spaCy entities before adding new units entities.
    doc.ents = filter_spans([span] + list(doc.ents))
    # Optimization tip (see also example-spaCy-component.py):
    # First collect all new spans (e.g. from the EntityRuler) and then merge
    # them into doc.ents in a single step using filter_spans.
    # e.g. QUANTITY 559 mph  -> MEASURE 559 mph

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
