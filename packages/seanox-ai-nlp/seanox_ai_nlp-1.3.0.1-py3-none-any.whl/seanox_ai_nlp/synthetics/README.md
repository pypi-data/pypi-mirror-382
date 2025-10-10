# Introduction

Processing structured data with NLP models in domain-specific contexts -- such
as industry, e-commerce, medicine, or meteorology -- remains challenging. Models
trained on general corpora often struggle to interpret specialized terminology
correctly or place it in the appropriate semantic context. Structured data is
typically precise but lacks linguistic form and semantic depth, which limits its
usefulness for tasks like natural language generation and semantic retrieval.

Synthetic sentences with annotated domain-specific content offer a way to make
structured input linguistically more accessible. By recombining lexical,
syntactic, and semantic elements in a controlled manner, these sentences
introduce systematic variation. Introduces broader semantic coverage and
supports model adaptation to specific domains.

The __synthetics__ module provides a generator based on templates and
transformation rules. It introduces variation through stochastic selection and
controlled recombination, producing annotated sentences from structured input.
These outputs can be used to create training data for fine-tuning, evaluation,
or augmentation in domain-specific NLP workflows.

# Features

- __Template-Based Text Generation__  
  The module uses YAML-defined templates with Jinja2 syntax to generate
  controlled natural language from structured input. It supports conditional
  template selection based on input attributes, enabling flexible and
  context-sensitive generation.

- __Stochastic Variation__  
  Lexical and syntactic diversity is introduced through built-in filters such as
  __random_range__, __random_range_join__, __random_range_join_phrase__ and
  __random_set__ allowing the generation of semantically varied sentences from
  identical data structures.

- __Domain-Specific Annotation__  
  Entities are annotated using structured markers which facilitates precise
  extraction and provides fine-grained control over entity types and their
  placement within the text.

- __Rule-Based Span Detection__  
  The module applies regular expressions to identify semantic spans in annotated
  text, enabling the definition of complex patterns independently of
  tokenization or linguistic parsing.

- __Interpretation-Free Generation__  
  No semantic interpretation or analysis is performed during generation, which
  results in output that is deterministic and transparent, and suitable for use
  in controlled NLP workflows.

- __Compatibility with NLP Workflows__  
  The output object __Synthetic__ includes raw text, annotated text, entity
  spans with labels and positions, and RegEx-based semantic spans. This
  structure supports fine-tuning, evaluation, and data augmentation in
  domain-specific NLP pipelines, including spaCy-style frameworks.

# Table Of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Template](#template)
  - [Schema](#schema)
  - [Field Details](#field-details)
  - [Segments](#segments)
  - [Additional Jinja2 filters](#additional-jinja2-filters)
    - [`annotate`](#annotatevalue-any-label-str-----str)
    - [`random_range`](#random_rangeitems-listany-limit-int---1---listany)
    - [`random_range_join`](#random_range_joinitems-listany-separator-str----limit-int---1---str)
    - [`random_range_join_phrase`](#random_range_join_phraseitems-listany-separator-str----word-str----limit-int---1---str)
    - [`random_set`](#random_setitems-listany-count-int---1---listany)
    - [`normalize`](#normalizetext-str---str)
  - [Example Template File](#example-template-file)
- [Known Limitations](#known-limitations)
- [Usage](#usage)
  - [Integration in NLP-Workflows](#integration-in-nlp-workflows)
  - [Downstream Processing with pandas](#downstream-processing-with-pandas)
- [Benchmark](#benchmark)
  - [Single-Pass Evaluation](#single-pass-evaluation)
  - [Scaled Evaluation (×500)](#scaled-evaluation-500)
- [API Reference](#api-reference)
  - [`synthetics`](#syntheticsdatasource-str-template-str-data-dictstr-any-filters-dictstr-callable--none---synthetic)
  - [`Synthetic`](#synthetic)
  - [`TemplateException`](#templateexception)
  - [`TemplateConditionException`](#templateconditionexception)
  - [`TemplateExpressionException`](#templateexpressionexception)
  - [`TemplateSyntxException`](#templatesyntxexception)
- [System Design](#system-design)
  - [Components Overview](#components-overview)
  - [Processing Workflow](#processing-workflow)
- [Sources & References](#sources--references)

# Template

Templates composed of recombinable sentence fragments transform structured input
data into annotated natural language. This modular design enables variation,
reuse, and adaptability across different contexts. Each template includes
rendering logic, inline annotation markers, and optional conditions that guide
selection. Based on these conditions, templates are chosen dynamically and
contextually -- which makes the output both relevant and varied.

## Schema

```Yaml
segments:                      # Optional reusable segments
  ...                          # The sub-structure can be defined individually.

templates:
  - name: <string>             # Optional Unique identifier for the template
    condition: <expression>    # Optional condition to activate the template
    template: <string>         # Sentence with annotated placeholders
    spans:                     # Optional: custom span definitions
      - label: <string>        # Name of the span (e.g. "planet", "moon")
        pattern: <string>      # RegEx pattern to extract the span
```

## Field Details
- __name__: A unique identifier for the template, used for referencing and
  debugging.
- __condition__: A string representing a logical expression. It must evaluate to
  `True` for the template to be used. Example: `planet != "Earth"`.
- __template__: A sentence string containing placeholders, expressions,
  functions, and optional annotations via (`annotate`).
- __spans__:
  - Each span defines a __label__ and a RegEx __pattern__.
  - The span's position is determined by the full match of the regular
    expression -- from the start to the end of the match.
  - Useful for extracting relationships or nested entities not covered by inline
    annotations (`annotate`).
  - RegEx pattern may also contain case-sensitive `{$label}` placeholders,
    which are expanded at runtime into an OR alternation of all values collected
    for that label. Non-existent labels cause an inapplicable span label, as if
    the pattern does not match, and so the label is skipped. Syntax errors cause
    the TemplateExpressionException.

## Segments

The __segments__ section defines reusable, semantically annotated text fragments
that can be referenced within templates. These segments act as modular building
blocks for dynamic content generation.

There are two supported syntaxes for referencing segments in templates:

- `@data:planet` Inline syntax for direct references
- `{@data:planet}` Bracketed syntax for embeddings in complex or nested
  contexts

Both syntaxes resolve to the same segment definition and can be used
interchangeably depending on the formatting needs.

```Yaml
segments:
  term:
    planet: '(planet | annotate("term"))'
    diameter: '(diameter | annotate("term"))'
  data:
    planet: '(planet | annotate("planet"))'
    diameter: '((diameter ~ " km") | annotate("diameter"))'

templates:
  - name: Example
    condition: True
    template: The {{ @term:planet }} {{ @data:planet }} has a {{ {@term:diameter} }} of {{ {@data:diameter} }}.
```

The structure and depth below the section __segment__ is individual.

## Additional Jinja2 filters

### `annotate(value: Any, label: str = "") -> str`

<details>
  <summary>
Marks a value with a structured entity label for downstream processing (e.g.
entity extraction).
  </summary>

<br/>

```
{{ value | annotate("LABEL") }}
produce: [[[LABEL]]]value[[[-]]]
```

__Parameters__:
- `value (Any)`: The value to annotate. Will be converted to a string.
- `label (str)`: The entity label to apply. The same conventions apply as for
   variable names. In addition, the minus sign is permitted between word
   characters.

__Returns__:
- `str`: The annotated string if the label is valid, otherwise the original
  value.

__Behavior__
- Wraps the string representation of `value` with custom entity markers.
- Returns the original value if the label is invalid or empty.

__Purpose__
Enables inline annotation of entities in generated text.
</details>

### `random_range(items: list[Any], limit: int = -1) -> list[Any]`

<details>
  <summary>
Randomly selects and shuffles a subset of items from the provided list.
  </summary>

<br/>

```
{{ random_range(["apple", "banana", "cherry"], 2) }}
might return: ["banana", "apple"]
```

__Parameters__:
- `items (list[Any])`: The list of items to choose from.
- `limit (int)`: Maximum number of items to include. If negative, all items are
  considered.

__Returns__:
- `list[Any]`: A randomly selected and shuffled subset of the input list.

__Behavior__:
- Picks between 1 and `limit` items from the list.
- Shuffles the result before returning.
- Returns an empty list if input is empty or limit is zero.

__Purpose__:
Provides controlled variation in template-generated content.
</details>

### `random_range_join(items: list[Any], separator: str = ", ", limit: int = -1) -> str`

<details>
  <summary>
Randomly selects and joins a subset of items into a single string.
  </summary>

<br/>

```
{{ ["apple", "banana", "cherry"] | random_range_join(",", 2) }}
might produce: "cherry, apple"
```

__Parameters__:
- `items (list[Any])`: List of strings to choose from.
- `separator (str)`: Separator used between selected items.
- `limit (int)`: Maximum number of items to include. If negative, all items are
  considered.

__Returns__:
- `str`: Joined string of randomly selected items, or an empty string if input
  is empty.

__Behavior__:
- Selects between 1 and `limit` items from the list.
- Shuffles the selection and joins it using the specified separator.
- Returns an empty string if the input list is empty.

__Purpose__:
Generates dynamic, varied list expressions for use in template-generated text.
</details>

### `random_range_join_phrase(items: list[Any], separator: str = ", ", word: str = ", ", limit: int = -1) -> str`

<details>
  <summary>
Randomly selects and joins items into a natural-language-like phrase.
  </summary>

<br/>

```
{{ ["apple", "banana", "cherry"] | random_range_join_phrase(", ", " and ", 3) }}
might produce: "banana, cherry and apple"
```

__Parameters__:
- `items (list[Any])`: List of strings to choose from.
- `separator (str)`: Separator used between items before the final one.
- `word (str)`: Conjunction word before the last item (e.g., `"and"`, `"or"`).
- `limit (int)`: Maximum number of items to include. If negative, all items are
  considered.

__Returns__:
- `str`: Natural-language-like phrase of randomly selected items, or an empty string
  if input is empty.

__Behavior__:
- Selects between 1 and `limit` items from the list.
- Shuffles the selection and formats it as:
  - One item → returned as-is.
  - Two items → joined with the conjunction word.
  - Three or more → joined with separator, and the last item prefixed by the conjunction word.

__Purpose__:
Creates a natural-language-like phrase for use in template-generated text
</details>

### `random_set(items: list[Any], count: int = -1) -> list[Any]`

<details>
  <summary>
Randomly selects a subset of items from a list.
  </summary>

<br/>

```
{{ ["apple", "banana", "cherry"] | random_set(2) }}
might return: ["banana", "apple"]
```

__Parameters__:
- `items (list[Any])`: List of items to choose from.
- `count (int)`: Number of items to select. If negative or exceeds list length,
  all items are returned in random order.

__Returns__:
- `list[Any]`: A randomly selected subset of items, or an empty list if input is
  empty.

__Behavior__:
- Returns up to `count` randomly selected items.
- If `count` is negative → returns all items in random order.
- If `count` is zero or list is empty → returns an empty list.

__Purpose__:
Provides raw access to a randomized subset of items for further use in templates
or logic.
</details>

### `normalize(text: str) -> str`

<details>
  <summary>
Normalizes whitespace in a string.
  </summary>

<br/>

```
{{ " apple    banana    cherry "] | normalize }}
might return: "apple banana cherry"
```

__Parameters__:
- `text (str)`: The input string to be cleaned.

__Returns__:
- `str`: A string with normalized whitespace.

__Behavior__:
- Removes leading and trailing whitespace.
- Replaces any sequence of one or more whitespace characters (spaces, tabs,
  newlines) with a single space.
- Preserves the original word order and content.

__Purpose__:
Provides a clean and consistent string format for use in templates, especially
when dealing with user input or dynamically generated content.
</details>

## Example Template File
See a working example in [synthetics_en_annotate.yaml](
    ../../tests/synthetics_en_annotate.yaml)

# Known Limitations

No limitations have been documented in current usage scenarios.

# Usage

```python
from seanox_ai_nlp.synthetics import synthetics
import json

with open("synthetics-planets_en.json", encoding="utf-8") as file:
  datas = json.load(file)

for data in datas:
  synthetic = synthetics(".", "synthetics_en_annotate.yaml", data)
  print(synthetic)
```

Example Output:
```python
Synthetic(
    text='Closest planet to the Sun as well as Many impact craters are characteristic of Mercury.',
    annotation='[[[characteristics]]]Closest planet to the Sun[[[-]]] as well as [[[characteristics]]]Many impact craters[[[-]]] are characteristic of [[[planet]]]Mercury[[[-]]].',
    entities=[
        (0, 25, 'characteristics'),
        (37, 56, 'characteristics'),
        (79, 86, 'planet')
    ],
    spans=[]
),
Synthetic(
    text="'planet: Earth', 'type: terrestrial planet', 'diameter: 12742', ...",
    annotation="'[[[terms]]]planet[[[-]]]: [[[planet]]]Earth[[[-]]]', ...",
    entities=[
        (1, 7, 'terms'),
        (9, 14, 'planet'),
        ...
    ],
    spans=[
        (1, 14, 'PAIR'),
        (18, 42, 'PAIR'),
        ...
    ]
),
...
```

## Integration in NLP-Workflows

Example for a spaCy pipeline.  
see also [example-spaCy-pipeline.py](
    ../../examples/synthetics/example-spaCy-pipeline.py) with comments

```python
from spacy.tokens import DocBin
from seanox_ai_nlp.synthetics import synthetics

import spacy
import json

with open("synthetics-planets_en.json", encoding="utf-8") as file:
    datas = json.load(file)

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
```

Example Output:
```text
Doc 1:
What can you tell me about "Volcanically active" in our solar system?
Volcanically active is a feature of Venus.
It is a terrestrial planet.
The planet does not have any moons and has a diameter of 12104 km.
Label: characteristics   Start: 28    End: 47    Volcanically active
Label: term              Start: 56    End: 68    solar system
Label: characteristics   Start: 70    End: 89    Volcanically active
Label: planet            Start: 106   End: 111   Venus
Label: type              Start: 121   End: 139   terrestrial planet
Label: term              Start: 186   End: 194   diameter
Label: diameter          Start: 198   End: 206   12104 km
```

## Downstream Processing with pandas

Example for downstream processing with pandas.  
see also [example-pandas.py](
    ../../examples/synthetics/example-pandas.py) with comments.

```python
from seanox_ai_nlp.synthetics import synthetics
import json
import pandas as pd

LABEL_COLORS = {
    "planet": ("\033[38;5;0m", "\033[48;5;117m"),
    "term":   ("\033[38;5;0m", "\033[48;5;250m")
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

with open("synthetics-planets_en.json", encoding="utf-8") as file:
    datas = json.load(file)

for data in datas:
    synthetic = synthetics(".", "synthetics_en_annotate.yaml", data)
    print(highlight_entities(synthetic.text, synthetic.entities))

    df = pd.DataFrame(synthetic.entities, columns=["start", "end", "label"])
    df["text"] = df.apply(lambda row: synthetic.text[row["start"]:row["end"]], axis=1)
    df = df[["start", "end", "label", "text"]]
    print(df.to_string(index=False))    
```

Example Output:
```text
Compared to Earth, Mars takes 322 more days to complete its orbit.
 start  end    label          text
    12   17     term         Earth
    19   23   planet          Mars
    30   43 turnover 322 more days
    60   65     term         orbit
```

> [!NOTE]
> The entity highlighting in this script uses ANSI escape codes to render
> colored text in the terminal. While this works well on most Unix-based systems
> (e.g. macOS, Linux) and modern terminal emulators, it may not display
> correctly on all platforms. 

# Benchmark

The benchmark tests were conducted on a system running Windows 11 with an Intel
Core i5-12400 and 16 GB of RAM. The templates used for evaluation included
conditional logic, loops, randomization, and annotated entities, representing a
moderately complex structure typical for synthetic text generation. The focus
was on measuring text throughput during large-scale data generation, excluding
I/O and external dependencies.

## Single-Pass Evaluation

[test_synthetics_benchmark_01](../../tests/test_synthetics_synthetics.py)

| Metric                         | Value              |
|--------------------------------|--------------------|
| Varied text without repetition | 1,813 characters   |
| Iterations                     | 8 x                |
| Processing time                | 0.94 ms            |
| Avg. time per iteration        | ~0.1175 ms         |
| Theoretical throughput         | ~1,928,723 chars/s |

## Scaled Evaluation (&times;500)

[test_synthetics_benchmark_02](../../tests/test_synthetics_synthetics.py)

| Metric                               | Value              |
|--------------------------------------|--------------------|
| Scaled Data (500&times; single test) | 848,888 characters |
| Iterations                           | 4000 x             |
| Processing time                      | 346.10 ms          |
| Avg. time per iteration              | ~0.0865 ms         |
| Theoretical throughput               | ~2,452,724 chars/s |

# API Reference

The __synthetic__ module offers a compact API for synthetic text generation. It
is suitable for NLP pipelines, annotation workflows, or automated content
generation tools. 

## `synthetics(datasource: str, template: str, data: dict[str, Any], filters: dict[str, Callable] = None) -> Synthetic`

<details>
  <summary>
Generates synthetic text using predefined YAML templates.

The function loads template definitions from a YAML file located in the
datasource directory (e.g. synthetics_en.yaml). It evaluates the conditions
specified for each template, filters the matching entries, randomly selects one
of them, and renders the final output using the Jinja2 templating engine.
  </summary>

Templates are cached internally to improve performance on repeated invocations.

__Parameters:__
- `datasource (str)`: Path to the directory containing template files.
- `template (str)`: Name of the template file.
- `data (dict)`: Contextual data used to evaluate conditions and render the
  template.
- `filters (dict, optional)`: Additional custom filters for template rendering.
  Keys are filter names (str), and values are callable objects (callables) that
  implement the filter.

__Returns:__
- `Synthetic`: A dataclass containing the generated synthetic text, its 
  annotated version, and metadata about entities and spans.

__Raises:__
- `FileNotFoundError`: If the YAML template file for the given language cannot
  be found at the specified path.
- `TemplateException`: If the template file cannot be loaded or parsed.
- `TemplateConditionException`: If a condition expression in the template is
  invalid or unsafe to evaluate.
- `TemplateExpressionException`: If a span expression in the template is
  invalid.
</details>

## `Synthetic`

<details>
  <summary>
Represents the result of a synthetic text generation process including both raw
and annotated text, as well as entity and span metadata.
  </summary>

<br/>

__Attributes__:
- `text (str)`: The raw generated text without annotations.
- `annotation (str)`: The annotated version of the text, including entity
  markers.
- `entities (list[tuple[int, int, str]])`: A list of entities found in the text.
  Each entity is represented as a tuple (`start_index, end_index, label`).
- `spans (list[tuple[int, int, str]])`: A list of pattern-based spans in the
  text. Each span is represented as a tuple (`start_index, end_index, label`).
</details>

## `TemplateException`

Raised when the template file cannot be loaded or parsed due to general errors
in the YAML.

## `TemplateConditionException`

Raised when a condition expression in the template is invalid or unsafe to
evaluate.

## `TemplateExpressionException`
If a span expression in the template is invalid.

## `TemplateSyntxException`

Raised when a syntax error occurs in the jinja2 template.

# System Design

The __synthetics__ module generates annotated natural language from structured
input using predefined templates composed of recombinable sentence fragments. It
does not perform semantic interpretation. The module operates deterministically
and follows a rule-based approach.

Design characteristics:

- Templates are written in YAML and rendered using Jinja2.
- Conditional logic enables dynamic and context-sensitive template selection.
- Inline entity annotation is supported via custom markers.
- RegEx-based span extraction allows postprocessing of semantic patterns.
- Execution is limited to safe built-in functions.

## Components Overview

| Component         | Description                                                                             |
|-------------------|-----------------------------------------------------------------------------------------|
| Template          | Defines recombinable sentence fragments, rendering logic, and selection conditions      |
| Jinja2 Filter     | Additional rendering helpers for annotation and controlled variation                    |
| Jinja2 Renderer   | Renders annotated text from structured input using selected templates                   |
| Entity Extraction | Extracts and annotates entities inline based on input structure                         |
| Span Extraction   | Detects semantic spans in the generated text using regular expressions                  |
| Synthetic         | Structured data object containing the generated text, annotations, entities, and spans. |

## Processing Workflow

1. __Input__: Structured data as a dictionary
2. __Template Preprocessing__: Segments are resolved in the template logic
3. __Template Filtering__: Templates are selected based on conditions
4. __Template Selection__: One template is chosen randomly from the filtered set
5. __Rendering__: Jinja2 renders the template with inline annotations
6. __Entity Extraction__: Markers are parsed and converted to entity spans
7. __Span Detection__: RegEx patterns are applied to extract additional spans
8. __Output__: A `Synthetic` object is returned with all relevant metadata

# Sources & References

- https://jinja.palletsprojects.com/en/stable/
