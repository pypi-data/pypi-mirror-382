# examples/synthetics/example-spaCy-pipeline.py
# Run: python -m spacy download en_core_web_md
#      python examples/synthetics/example-spaCy-pipeline.py

from spacy.tokens import DocBin
from seanox_ai_nlp.synthetics import synthetics

import spacy
import json

# Load synthetic data
with open("synthetics-planets_en.json", encoding="utf-8") as file:
    datas = json.load(file)

# Load pre-trained spaCy model with vectors
nlp = spacy.load("en_core_web_md")
doc_bin = DocBin()

for data in datas:
    synthetic = synthetics(".", "synthetics_en_annotate.yaml", data)
    doc = nlp.make_doc(synthetic.text)
    ents = []
    for start, end, label in synthetic.entities:
        span = doc.char_span(start, end, label=label)
        if span:
            ents.append(span)
        else:
            print(f"Invalid entity: ({start}, {end}, {label}) in text: {synthetic.text}")
    doc.ents = ents
    doc_bin.add(doc)

# Save for spaCy training
doc_bin.to_disk("synthetics_training.spacy")

docs = list(doc_bin.get_docs(nlp.vocab))
for index, doc in enumerate(docs):
    if index > 0:
        print()
    print(f"Doc {index + 1}:")
    print(f"{doc.text}")
    for ent in doc.ents:
        print(
            f"Label: {ent.label_:<18}"
            f"Start: {ent.start_char:<6}"
            f"End: {ent.end_char:<6}"
            f"{ent.text}"
        )
