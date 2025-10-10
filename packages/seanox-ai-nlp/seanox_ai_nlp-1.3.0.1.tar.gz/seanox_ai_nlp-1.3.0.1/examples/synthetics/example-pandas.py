# examples/synthetics/example-pandas.py
# Run: python examples/synthetics/example-pandas.py

import pandas as pd
from seanox_ai_nlp.synthetics import synthetics
import json

LABEL_COLORS = {
    "planet": ("\033[38;5;0m", "\033[48;5;117m"),  # white on blue
    "term": ("\033[38;5;0m", "\033[48;5;250m")  # black on light gray
}


def highlight_entities(text, entities):
    reset = '\033[0m'
    for start, end, label in sorted(entities, key=lambda x: -x[0]):
        if label not in LABEL_COLORS:
            label = "term"
        fg, bg = LABEL_COLORS[label]
        colored = f"{fg}{bg}{text[start:end]}{reset}"
        text = text[:start] + colored + text[end:]
    return text


# Load synthetic input data
with open("synthetics-planets_en.json", encoding="utf-8") as file:
    datas = json.load(file)

# Generate color-coded output for terms and planets
for data in datas:
    synthetic = synthetics(".", "synthetics_en_annotate.yaml", data)
    print(highlight_entities(synthetic.text, synthetic.entities))

    df = pd.DataFrame(synthetic.entities, columns=["start", "end", "label"])
    df["text"] = df.apply(lambda row: synthetic.text[row["start"]:row["end"]], axis=1)
    df = df[["start", "end", "label", "text"]]
    print(df.to_string(index=False))
