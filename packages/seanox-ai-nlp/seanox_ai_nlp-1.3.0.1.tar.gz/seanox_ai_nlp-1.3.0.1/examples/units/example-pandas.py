# examples/units/example-pandas.py
# Run: python examples/units/example-pandas.py

import pandas as pd
from seanox_ai_nlp.units import units

# Loading text
texts = [
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph).",
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
]

# Init DataFrame and detecting entities in text
df = pd.DataFrame(texts, columns=["text"])
df["units"] = df["text"].apply(units)

# Access to extracted values
df["first_unit"] = df["units"].apply(lambda u: u[0].value if u else None)

# Formatted output
for index, row in df.iterrows():
    print(f"\nText: {row['text']}")
    print("Extracted units:")
    for unit in row["units"]:
        print(f"- {unit.label:{10}} | text: {unit.text:{15}} | value: {unit.value or '':{10}} | unit: {unit.unit or '':{5}} | categories: {', '.join(unit.categories)}")
