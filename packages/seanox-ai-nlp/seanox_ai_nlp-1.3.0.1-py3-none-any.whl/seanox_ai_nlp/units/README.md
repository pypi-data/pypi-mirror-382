# Introduction

Measurement expressions appear across domains like weather, medicine,
e-commerce, and social media. Their formats are often inconsistent and informal,
which complicates automated extraction.

The __units__ module provides a __rule-based__ approach to identifying such
expressions. It uses deterministic pattern recognition and does not depend on
large language models (LLMs), supporting __lightweight__ NLP workflows.

Developed for practitioners and developers, the module extracts constructs like
`1000 hPa`, `-20 &ordm;C`, or `km/h`, and also handles standalone units (`in`,
`cm`, etc.). Its language-agnostic design and adaptable formatting support a
wide range of applications, including general, semi-technical, and semi-academic
content.

The module integrates with tools such as spaCy's __EntityRuler__ and supports
workflows involving __annotation__, __filtering__, or __token alignment__, where
clarity and control are essential. It does not perform semantic analysis itself,
but produces structured output suitable for downstream semantic processing.

# Features

__units__ provides a deterministic mechanism for extracting measurement
expressions from natural language.

- __Pattern-based extraction__  
  Identifies constructs like _5 km_, _-20 &ordm;C_, or _1000 hPa_ using regular
  expressions and token patterns -- no training required.

- __Language-independent architecture__  
  Operates at token and character level, making it effective across multilingual
  content.

- __Support for compound expressions__  
  Recognizes both unit combinations (_km/h, kWh/m&sup2;, g/cm&sup3;_) and
  numerical constructs using signs and operators: _&plusmn;, &times;, &middot;,
  :, /, ^, -_ and more.

- __Integration-ready output__  
  Returns structured results compatible with tools like spaCy's EntityRuler for
  use in pipelines.

- __Transparent design__  
  Fully interpretable and deterministic -- avoids black-box ML, supporting
  reliable and auditable processing.

# Table Of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Supported formats and units](#supported-formats-and-units)
  - [Numeric Values](#numeric-values)
  - [Dimensional Separators](#dimensional-separators)
  - [Units](#units)
  - [SI Prefixes for Multiples & Parts](#si-prefixes-for-multiples--parts)
  - [SI Exponents](#si-exponents)
  - [IEC Prefixes for Multiples & Parts](#iec-prefixes-for-multiples--parts)
  - [Mathematical Operators](#mathematical-operators)
  - [Informal Prefix & Exponents](#informal-prefix--exponents)
- [Usage](#usage)
  - [Unit Extraction Note](#unit-extraction-note)
  - [Integration in NLP-Workflows](#integration-in-nlp-workflows)
  - [Downstream Processing with pandas](#downstream-processing-with-pandas)
- [Benchmark](#benchmark)
  - [Single-Pass Evaluation](#single-pass-evaluation) 
  - [Scaled Evaluation &times;10](#scaled-evaluation-10)
- [Known Limitations](#known-limitations)
  - [Unit Recognition Without Semantic Context](#unit-recognition-without-semantic-context)
  - [Ambiguous Unit Symbols](#ambiguous-unit-symbols)
- [API Reference](#api-reference)
  - [`units`](#unitstext-str---listunit)
  - [`spacing`](#spacingtext-str-mode-spacingmode--spacingmodenumeric---str)
  - [`Unit`](#unit-namedtuple)
  - [`NUMERIC_PATTERN`](#numeric_pattern)
  - [`NUMERIC_VALIDATION_PATTERN`](#numeric_validation_pattern)
  - [`NUMERIC_EXPRESSION_VALIDATION_PATTERN`](#numeric_expression_validation_pattern)
  - [`UNIT_SYMBOLS_PATTERN`](#unit_symbols_pattern)
  - [`UNIT_PATTERN`](#unit_pattern)
  - [`UNIT_VALIDATION_PATTERN`](#unit_validation_pattern)
  - [`UNIT_EXPRESSION_VALIDATION_PATTERN`](#unit_expression_validation_pattern)
  - [`UNIT_CLASSIFICATION_PATTERN`](#unit_classification_pattern)
  - [`UNIT_OPERATORS_PATTERN`](#unit_operators_pattern)
- [System Design](#system-design)
  - [Components Overview](#components-overview)
  - [Processing Workflow](#processing-workflow)
- [Maintenance & Extensibility](#maintenance--extensibility)
- [Sources & References](#sources--references)

# Supported formats and units

## Numeric Values

<details>
  <summary>
Measurement values appear in diverse numeric formats depending on locale,
notation, and domain. <b>units</b> supports common representations, including
signs and tolerance indicators.
  </summary>

<br/>

| Locale | Signs          | Format                   | 
|--------|----------------|--------------------------|
| CH     | + - &plusmn; ~ | 1&rsquo;000&rsquo;000,00 |
| DE     | + - &plusmn; ~ | 1.000.000,00             |
| EN     | + - &plusmn; ~ | 1,000,000.00             |
| FR     | + - &plusmn; ~ | 1 000 000,00             |
| IN     | + - &plusmn; ~ | 1,00,000.00              |
| ISO    | + - &plusmn; ~ | 1 000 000.00             |
| plain  | + - &plusmn; ~ | 1000000.00               |
| plain  | + - &plusmn; ~ | 1000000,00               |

</details>

## Dimensional Separators

<details>
  <summary>
Dimensional separators link numerical values to compact measurements such as
<b>10 &times; 20 &times; 30 cm</b>, where each value represents a distinct
dimension (e.g. width &times height &times depth). These separators help convey
structured spatial information in a concise format.
  </summary>

<br/>

| Separator                   | Symbol   |
|-----------------------------|----------|
| Plus                        | &plus;   |
| Minus                       | &minus;  |
| Plus-minus / Tolerance      | &plusmn; |
| Asterisk / Multiplication   | &ast;    |
| Times (Multiplication Sign) | &times;  |
| x / Times (ASCII)           | x        |
| Middle Dot / Dot Separator  | &middot; |
| Colon / Ratio               | &colon;  |
| Divide Sign                 | &divide; |
| Slash / Division            | &sol;    |
| Caret / Exponentiation      | &Hat;    |
| Figure Dash                 | &#8210;  |
| En Dash / Range             | &ndash;  |
| Em Dash / Dash              | &mdash;  |

</details>

## Units

<details>
  <summary>
Supported unit symbols (SI, IEC, common & informal)  
  </summary>

<br/>

__Note__ These are base units only. Variants result from the additional
properties recorded (e.g. km as a combination of kilo and meter). There is no
claim to interpretation, classification, or complete standardization of the
units (e.g. [IEC](https://iec.ch/si), [BIPM](
    https://www.bipm.org/en/measurement-units)).

| Unit                                 | Symbol&nbsp;&blacktriangledown; | Classification (Categories) | SI Base | SI Derivation | SI Extension | SI relevant | SI with Prefix (M) | SI with Prefix (S) | SI with Exponents | IEC relevant | Common Units | Informal  |
|--------------------------------------|---------------------------------|-----------------------------|---------|---------------|--------------|-------------|--------------------|--------------------|-------------------|--------------|--------------|-----------|
| Foot (single quote mark)             | '                               | length                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Inch (double quote mark)             | "                               | length                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Percent                              | %                               | ratio                       |         |               |              |             |                    |                    |                   |              | x            |           |
| Foot (quote mark)                    | &#x2032;                        | length                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Inch (quote mark)                    | &#x2033;                        | length                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Ampere                               | A                               | electricity                 | x       |               |              | x           | x                  | x                  | x                 |              |              |           |
| Are                                  | a                               | area                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Astronomical Unit                    | AE                              | length astronomy            |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Battery Capacity                     | Ah                              | electricity                 |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Atmosphere (pressure)                | atm                             | pressure                    |         |               |              |             |                    |                    |                   |              | x            |           |
| Gauge Pressure                       | At&uuml;                        | pressure                    |         |               |              |             |                    |                    |                   |              | x            |           |
| Astronomical Unit                    | AU                              | length astronomy            |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Barn                                 | b                               | area radiation              |         |               | x            | x           | x                  | x                  |                   |              |              |           |
| Bel                                  | B                               | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Byte                                 | B                               | it storage                  |         |               |              | x           | x                  | x                  |                   | x            |              |           |
| Bar                                  | bar                             | pressure                    |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Baud Rate                            | baud                            | It network time             |         |               |              | x           |                    |                    |                   |              |              |           |
| Barrel (oil)                         | bbl                             | volume                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Bit                                  | Bit                             | it storage                  |         |               |              | x           | x                  | x                  |                   |              |              |           |
| Bits Per Second                      | bps                             | it network time             |         |               |              | x           | x                  | x                  |                   |              |              |           |
| Becquerel                            | Bq                              | radiation                   |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Byte                                 | Byte                            | it storage                  |         |               |              | x           | x                  | x                  |                   |              |              |           |
| Coulomb                              | C                               | electricity                 |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Candela                              | cd                              | light                       | x       |               |              | x           | x                  | x                  |                   |              |              |           |
| Carat (gem weight)                   | ct                              | mass                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Day                                  | d                               | time                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Dalton                               | Da                              | mass atomic                 |         |               | x            | x           | x                  | x                  |                   |              |              |           |
| Decameter                            | dam                             | length                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Decibel                              | dB                              | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Decibel A curve                      | db(A)                           | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Decibel C curve                      | db(C)                           | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Decibel G curve                      | db(G)                           | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Decibel Z curve                      | db(Z)                           | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Dots Per Inch                        | dpi                             | it graphics                 |         |               |              |             |                    |                    |                   |              | x            |           |
| Dots Per Inch                        | DPI                             | it graphics                 |         |               |              |             |                    |                    |                   |              | x            |           |
| Dioptre                              | dpt                             | optics                      |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Double Hundredweight                 | dz                              | quantity                    |         |               |              |             |                    |                    |                   |              | x            |           |
| Dozen                                | dz                              | quantity                    |         |               |              |             |                    |                    |                   |              | x            |           |
| Electronvolt                         | eV                              | energy                      |         |               | x            | x           | x                  | x                  |                   |              |              |           |
| Farad                                | F                               | electricity capacitance     |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Floating Point Operations Per Second | FLOPS                           | it processing time          |         |               |              | x           | x                  | x                  |                   |              |              |           |
| Frames Per Second                    | fps                             | it graphics video time      |         |               |              |             |                    |                    |                   |              | x            |           |
| Foot                                 | ft                              | length                      |         |               |              |             |                    |                    |                   |              | x            | x         |
| Gram                                 | g                               | mass                        | x       |               |              | x           | x                  | x                  | x                 |              |              |           |
| Gallon                               | gal                             | volume                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Gray                                 | Gy                              | radiation                   |         | x             |              | x           | x                  | x                  |                   |              |              |           |
| Henry                                | H                               | electricity                 |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Hour                                 | h                               | time                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Hectare                              | ha                              | area                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Hectoliter                           | hL                              | volume                      |         |               | x            | x           |                    |                    |                   |              |              |           |
| Hectoliter                           | hl                              | volume                      |         |               | x            | x           |                    |                    |                   |              |              |           |
| Horsepower (imperial)                | hp                              | power                       |         |               |              |             |                    |                    |                   |              | x            |           |
| Hertz                                | Hz                              | frequency                   |         | x             |              | x           | x                  | x                  |                   |              |              |           |
| Inch                                 | in                              | length                      |         |               |              |             |                    |                    |                   |              | x            | x         |
| Joule                                | J                               | energy                      |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Kelvin                               | K                               | temperature                 | x       |               |              | x           |                    |                    |                   |              | x            |           |
| Katal                                | kat                             | amount                      |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Knot                                 | kn                              | speed                       |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Karat (gold purity)                  | kt                              | mass                        |         |               |              |             |                    |                    |                   |              | x            |           |
| Knot                                 | kt                              | speed                       |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Liter                                | l                               | volume                      |         |               | x            | x           |                    | x                  | x                 |              | x            |           |
| Liter                                | L                               | volume                      |         |               | x            | x           |                    | x                  | x                 |              | x            |           |
| Pound                                | lb                              | mass                        |         |               |              |             |                    |                    |                   |              | x            |           |
| Light Year                           | lj                              | length astronomy            |         |               |              |             |                    |                    |                   |              | x            |           |
| Lumen                                | lm                              | light                       |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Lumen second                         | ls                              | light energy                |         |               |              |             |                    |                    |                   |              | x            |           |
| Lux                                  | lx                              | light                       |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Meter                                | m                               | length                      | x       |               |              | x           | x                  | x                  | x                 |              |              | x         |
| Mel                                  | mel                             | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Mile                                 | mi                              | length                      |         |               |              |             |                    |                    |                   |              | x            | x         |
| Mile                                 | mile                            | length                      |         |               |              |             |                    |                    |                   |              |              | x         |
| Minute (long form)                   | min                             | time                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Million Instructions Per Second      | MIPS                            | it processing time          |         |               |              | x           | x                  | x                  |                   |              |              |           |
| Mole                                 | mol                             | amount                      | x       |               |              | x           |                    |                    | x                 |              | x            |           |
| Miles per Hour                       | mph                             | length time                 |         |               |              |             |                    |                    |                   |              |              | x         |
| Newton                               | N                               | force                       |         | x             |              | x           | x                  | x                  |                   |              |              |           |
| Neper                                | Np                              | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Degree                               | &ordm;                          | angle                       |         |               |              |             |                    |                    |                   |              | x            |           |
| Degree Celsius                       | &ordm;C                         | temperature                 |         | x             |              | x           |                    |                    |                   |              | x            |           |
| Ounce                                | oz                              | mass                        |         |               |              |             |                    |                    |                   |              | x            |           |
| Ounce                                | oz.                             | mass                        |         |               |              |             |                    |                    |                   |              | x            |           |
| Troy Ounce                           | oz. tr.                         | mass                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Pond (metric force)                  | p                               | force                       |         |               |              |             |                    |                    |                   |              | x            |           |
| Pascal                               | Pa                              | pressure                    |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Parsec                               | pc                              | length astronomy            |         |               |              |             |                    |                    |                   |              | x            |           |
| Pixels Per Inch                      | PPI                             | it graphics area            |         |               |              |             |                    |                    |                   |              | x            |           |
| Pixels Per Inch                      | ppi                             | it graphics area            |         |               |              |             |                    |                    |                   |              | x            |           |
| Horsepower (metric)                  | PS                              | power                       |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Pint                                 | pt                              | volume                      |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Pixel                                | px                              | it graphics                 |         |               |              |             |                    |                    |                   |              | x            |           |
| Radian                               | rad                             | angle                       |         | x             |              | x           |                    |                    |                   |              | x            |           |
| Cubic Meter (stacked wood)           | rm                              | volume                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Revolutions Per Minute               | RPM                             | it frequency rotation time  |         |               |              |             |                    |                    |                   |              | x            |           |
| Second (long form)                   | s                               | time                        | x       |               |              | x           |                    | x                  | x                 |              | x            |           |
| Siemens                              | S                               | electricity conductance     |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Sone                                 | sone                            | acoustics                   |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Steradian                            | sr                              | angle                       |         | x             |              | x           |                    |                    | x                 |              | x            |           |
| Stere (wood volume)                  | St                              | volume                      |         |               |              |             |                    |                    |                   |              | x            |           |
| Sievert                              | Sv                              | radiation                   |         | x             |              | x           | x                  | x                  |                   |              |              |           |
| Metric Ton                           | t                               | mass                        |         |               |              |             |                    |                    |                   |              | x            |           |
| Tesla                                | T                               | magnetic field              |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Tex                                  | tex                             | mass                        |         |               | x            | x           |                    |                    |                   |              | x            |           |
| Atomic Mass Unit                     | u                               | mass atomic                 |         |               |              |             |                    |                    |                   |              | x            |           |
| Volt                                 | V                               | electricity                 |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Apparent Power                       | VA                              | electricity power           |         |               | x            | x           | x                  | x                  |                   |              |              |           |
| Reactive Power                       | Var                             | electricity power           |         |               |              |             |                    |                    |                   |              | x            |           |
| Virtual CPU Cores                    | vCore                           | it processing amount        |         |               |              |             |                    |                    |                   |              | x            |           |
| Watt                                 | W                               | power                       |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Weber                                | Wb                              | magnetism                   |         | x             |              | x           | x                  | x                  | x                 |              |              |           |
| Energy                               | Wh                              | energy                      |         |               | x            | x           | x                  | x                  |                   |              |              |           |
| Yard                                 | yd                              | length                      |         |               |              |             |                    |                    |                   |              | x            | x         |
| Hundredweight (metric)               | Z                               | mass                        |         |               |              |             |                    |                    |                   |              | x            |           |
| Angular Frequency                    | &omega;                         | frequency rotation          |         |               |              |             |                    |                    |                   |              | x            |           |
| Ohm                                  | &Omega;                         | electricity                 |         | x             |              | x           | x                  | x                  | x                 |              |              |           |

The units and prefixes included were compiled from publicly available sources,
including technical references (e.g. Wikipedia, national standards, public
websites on the subject), as well as commonly observed usage. In the absence of
a unified standard, this dataset aims to offer a practical and extensible
collection rather than a formally authoritative one.

</details>

## SI Prefixes for Multiples & Parts

<details>
  <summary>
Internationally defined SI prefixes for multiples and submultiples of units of
measurement.
  </summary>

<br/>

| Multiples | Symbol | Submultiples | Symbol  |
|-----------|--------|--------------|---------|
| Quetta    | Q      | Deci         | d       |
| Ronna     | R      | Centi        | c       |
| Yotta     | Y      | Milli        | m       |
| Zetta     | Z      | Mikro        | &micro; |
| Exa       | E      | Nano         | n       |
| Peta      | P      | Pico         | p       |
| Tera      | T      | Femto        | f       |
| Giga      | G      | Atto         | a       |
| Mega      | M      | Zepto        | z       |
| Kilo      | k      | Yocto        | y       |
| Hecto     | h      | Ronto        | r       |
| Deca      | da     | Quecto       | q       |

</details>

## SI Exponents

<details>
  <summary>
Exponents commonly used in everyday life in combining to SI units.
  </summary>

<br/>

| Positive Exponents | Negative Exponents |
|--------------------|--------------------|
| &sup1;             | &#x207B;&sup1;     |
| &sup2;             | &#x207B;&sup2;     |
| &sup3;             | &#x207B;&sup3;     |

</details>

## IEC Prefixes for Multiples & Parts

<details>
  <summary>
International Electrotechnical Commission (IEC) prefixes for indicating
multiples and fractions in data processing.
  </summary>

<br/>

| Multiplicative | Symbol | Submultiplicative | Symbol |
|----------------|--------|-------------------|--------|
| Kibi           | Ki     |                   |        |
| Mebi           | Mi     |                   |        |
| Gibi           | Gi     |                   |        |
| Tebi           | Ti     |                   |        |
| Pebi           | Pi     |                   |        |
| Exbi           | Ei     |                   |        |
| Zebi           | Zi     |                   |        |
| Yobi           | Yi     |                   |        |

</details>

## Mathematical Operators

<details>
  <summary>
Mathematical operators for combining units into expressions.
  </summary>

<br/>

| Operator                                | Symbol   |
|-----------------------------------------|----------|
| Asterisk                                | *        |
| Division sign /<br/> Slash              | &sol;    |
| Letter x                                | x        |
| Multiplication point /<br/>Center point | &middot; |
| Multiplication sign                     | &times;  |

</details>

## Informal Prefix & Exponents

<details>
  <summary>
Everyday informal prefixes and exponents that are commonly used in certain
contexts but are not part of the official SI system.
  </summary>

<br/>

| Prefix       | Symbol | Exponents | Symbol | 
|--------------|--------|-----------|--------|
| Cubic        | c      | Cubic     | 2      |
| Square (lat) | q      | Square    | 3      |
| Square (en)  | sq     |           |        |

</details>

# Known Limitations

## Unit Recognition Without Semantic Context

The module operates purely on rule-based pattern matching without semantic
interpretation. This means unit-like expressions are extracted context-free,
regardless of their actual meaning in the sentence. For [example, the word
    __in__](#usage) may be matched as a unit due to its spelling, even when used
as a preposition. Such cases are not false positives in a technical sense, but
rather edge cases that require downstream filtering, e.g. via stop words or
Part-of-Speech (PoS) tags.

see also:
- [example-spaCy-pipeline.py](
    ../../examples/units/example-spaCy-pipeline.py) with comments
- [example-spaCy-pipeline-component.py](
    ../../examples/units/example-spaCy-component.py) as spaCy pipeline

## Ambiguous Unit Symbols

Some unit symbols are inherently ambiguous due to overlapping usage across
domains. For example, the symbol __B__ may refer to both __Bel__ (acoustics) and
__Byte__ or __Bit__ (information technology). Since the module does not perform
semantic disambiguation, such cases are handled inclusively: the __categories__
attribute will contain all relevant classifications, e.g. '["acoustics", "it",
"storage"]'. Therefore, downstream applications should apply domain-specific
filtering or interpretation as needed.

# Usage

```python
from seanox_ai_nlp.units import units

text = (
    "The cruising speed of the Boeing 747 is approximately 900 km/h (559 mph)."
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)

entities = units(text)
for entity in entities:
    print(entity)
```

```text
Unit(label='MEASURE', start=54, end=62, text='900 km/h', categories=('length', 'time'), unit='km/h', value='900')
Unit(label='MEASURE', start=64, end=71, text='559 mph', categories=('length', 'time'), unit='mph', value='559')
Unit(label='UNIT', start=100, end=102, text='in', categories=('length',), unit='in', value=None)
Unit(label='UNIT', start=124, end=128, text='km/h', categories=('length', 'time'), unit='km/h', value=None)
Unit(label='UNIT', start=150, end=153, text='mph', categories=('length', 'time'), unit='mph', value=None)
```

## Unit Extraction Note

The module identifies units and values using rule-based pattern recognition. In
the preceding example, the word __in__ is extracted as a unit __(inch)__, even
though it is used as a preposition in the context.

Since the module does __not perform semantic analysis__, such edge cases are
extracted __context-free__. Semantic interpretation is intentionally delegated to
the application layer -- typically based on:

- the presence of a __numeric value (value)__, if available
- and the assigned __categories (categories)__, such as __length__ or __time__

For example, an entry like __15 in__ can be interpreted as a valid unit
__(inch)__, while a standalone __in__ without a value or matching context may be
treated as a preposition.

## Integration in NLP-Workflows

Example for a spaCy pipeline.  
see also:
- [example-spaCy-pipeline.py](
    ../../examples/units/example-spaCy-pipeline.py) with comments
- [example-spaCy-pipeline-component.py](
    ../../examples/units/example-spaCy-component.py) as spaCy pipeline
component with comments

```python
import spacy
from spacy.tokens import Span
from spacy.util import filter_spans
from seanox_ai_nlp.units import units

Span.set_extension("value", default=None)
Span.set_extension("unit", default=None)
Span.set_extension("categories", default=None)

nlp = spacy.load("en_core_web_md")
text = (
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph)."
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)
doc = nlp(text)
units_entities = units(text)
for units_entity in units_entities:
    span = doc.char_span(
        units_entity.start,
        units_entity.end,
        label=units_entity.label
    )
    if span:
      span._.value = units_entity.value
      span._.unit = units_entity.unit
      span._.categories = list(units_entity.categories)
      doc.ents = filter_spans([span] + list(doc.ents))
for ent in doc.ents:
  if ent.label_ in ["UNIT", "MEASURE"]:
    print(f"{ent.text:{20}} | label: {ent.label_:{10}} | value: {ent._.value or '':{10}} | unit: {ent._.unit:{5}} | categories: {ent._.categories}")
  else:
    print(f"{ent.text:{20}} | label: {ent.label_}")
```

```text
Boeing               | label: ORG
747                  | label: PRODUCT
900 - 950 km/h       | label: MEASURE    | value: 900 - 950  | unit: km/h  | categories: ['length', 'time']
559 mph              | label: MEASURE    | value: 559        | unit: mph   | categories: ['length', 'time']
in                   | label: UNIT       | value:            | unit: in    | categories: ['length']
kilometers per hour  | label: TIME
km/h                 | label: UNIT       | value:            | unit: km/h  | categories: ['length', 'time']
mph                  | label: UNIT       | value:            | unit: mph   | categories: ['length', 'time']
```

The approach with spaCy-Retokenizer can be problematic.
- Token structure is changed globally, previously calculated offsets and spans
  become invalid.
- Overlapping entities are not allowed in spaCy, and merges of MEASURE collide
  with existing NER spans.
- After each merge, all affected spans must be recalculated, which is
  error-prone and resource-intensive.
- Unexpected side effects can occur, such as incorrect labels in unwanted places.

## Downstream Processing with pandas

Example for downstream processing with pandas.  
see also [example-pandas.py](
    ../../examples/units/example-pandas.py) with comments.

```python
import pandas as pd
from seanox_ai_nlp.units import units
texts = [
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph).",
    " It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
]
df = pd.DataFrame(texts, columns=["text"])
df["units"] = df["text"].apply(units)
df["first_unit"] = df["units"].apply(lambda u: u[0].value if u else None)
for index, row in df.iterrows():
    print(f"\nText: {row['text']}")
    print("Extracted units:")
    for unit in row["units"]:
      print(f"- {unit.label:{10}} | text: {unit.text:{15}} | value: {unit.value or '':{10}} | unit: {unit.unit or '':{5}} | categories: {', '.join(unit.categories)}")
```

```text
Text: The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph).
Extracted units:
- MEASURE    | text: 900 - 950 km/h  | value: 900 - 950  | unit: km/h  | categories: length, time
- MEASURE    | text: 559 mph         | value: 559        | unit: mph   | categories: length, time

Text:  It is typically expressed in kilometers per hour (km/h) and miles per hour (mph).
Extracted units:
- UNIT       | text: in              | value:            | unit: in    | categories: length
- UNIT       | text: km/h            | value:            | unit: km/h  | categories: length, time
- UNIT       | text: mph             | value:            | unit: mph   | categories: length, time
```

# Benchmark

The module was tested on an Intel Core i5-12400 with Windows 11 and 16 GB RAM.  

## Single-Pass Evaluation

[test_units_benchmark_01](../../tests/test_units_units.py)

| Metric                         | Value               |
|--------------------------------|---------------------|
| Varied text without repetition | 1,983 characters    |
| Detections                     | 51 units + measures |
| Processing time                | 1.02 ms             |
| Avg. time per unit             | ~0.020 ms           |
| Theoretical throughput         | ~50,000 units/s     |

## Scaled Evaluation (&times;10)

[test_units_benchmark_02](../../tests/test_units_units.py)

| Metric                              | Value                |
|-------------------------------------|----------------------|
| Scaled text (10&times; single test) | 19,830 characters    |
| Detections                          | 510 units + measures |
| Processing time                     | 8.83 ms              |
| Avg. time per unit                  | ~0.0173 ms           |
| Theoretical throughput              | ~57,740 units/s      |

# API Reference

The __units__ module offers a compact API for extracting unit expressions from
natural language. It is suitable for NLP pipelines, preprocessing workflows, and
annotation tools.

## `units(text: str) -> list[Unit]`

<details>
  <summary>
Extracts valid unit expressions and associated numerical values from a given
text.
  </summary>

__Parameters:__
- `text` (`str`): Input text for analysis.

__Returns:__
- `list[Unit]`: A list of structured `Unit` objects representing detected
  entities.

__Notes:__
- Recognizes both standalone units (`cm`, `kg`) and compound expressions
  (`km/h`, `mol&middot;L&#8315;&sup1;	`).
- Includes numeric values when present (`15 cm`, `?20 &ordm;C`).
- Applies strict validation using precompiled regular expressions.
- Semantic categories (e.g. `mass`, `length`, `energy`) are assigned via static
  lookup.

</details> 

## `spacing(text: str, mode: SpacingMode = SpacingMode.NUMERIC) -> str`

<details>
  <summary>
Corrects invalid spacing between numeric/alphanumeric expressions and unit
identifiers.
  </summary>

__Parameters:__
- `text` (`str`): Input string to normalize.
- `mode` (`SpacingMode`, optional): Spacing correction mode. Options:
  - `SpacingMode.NUMERIC`
  - `SpacingMode.ALPHANUMERIC`
  - `SpacingMode.ALL`

__Returns:__
- `str`: Text with corrected spacing.

</details>

## `Unit` (NamedTuple)

<details>
  <summary>
Represents a recognized unit entity.
  </summary>

__Attributes:__
- `label` (`str`): Entity type (`UNIT` or `MEASURE`)
- `start` / `end` (`int`): Character offsets in the original text
- `text` (`str`): Raw matched fragment
- `unit` (`str`): Extracted unit expression
- `value` (`Optional[str]`): Associated numeric value, if present
- `categories` (`tuple[str, ...]`): Semantic categories assigned to the unit

</details>

## `NUMERIC_PATTERN`

Precompiled regular expressions, matches numeric values in various
locale-specific formats (e.g. `1,000.5`, `1.000,5`, `1 000.5`).

## `NUMERIC_VALIDATION_PATTERN`

Precompiled regular expressions, validates a single numeric value.

## `NUMERIC_EXPRESSION_VALIDATION_PATTERN`

Precompiled regular expressions, validates compound numeric expressions (e.g.
`5 x 10`, `3.5/2`).

## `UNIT_SYMBOLS_PATTERN`

Precompiled regular expressions, matches all supported unit symbols, including
SI, IEC, informal, and common units.

## `UNIT_PATTERN`

Precompiled regular expressions, matches both standalone units and measure pairs
(e.g. `15 cm`, `?20 &ordm;C`).

## `UNIT_VALIDATION_PATTERN`

Precompiled regular expressions, validates a single unit symbol.

## `UNIT_EXPRESSION_VALIDATION_PATTERN`

Precompiled regular expressions, validates compound unit expressions (e.g.
`km/h`, `mol&middot;L?&sup1;`).

## `UNIT_CLASSIFICATION_PATTERN`

Precompiled regular expressions, named group-based pattern for classifying units
into semantic categories (e.g. `mass`, `length`, `energy`).

## `UNIT_OPERATORS_PATTERN`

Precompiled regular expressions, matches operators used in compound units (e.g.
`/`, `&middot;`, `x`).

# System Design

The module adopts a minimalist, rule-based design focused on regular expressions
to identify and classify measurement units in unstructured text. Its behavior is
__deterministic__, __language-independent__, and free from machine learning
dependencies -- ensuring transparency and reproducibility.

## Components Overview

| Component                     | Description                                                                                                                                |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| __Token Normalization__       | Detects and corrects typographic inconsistencies -- such as missing spaces between numbers and units -- to improve recognition robustness. |
| __Unit Extraction__           | Applies structured regular expressions to detect SI, informal, and compound unit formats in natural language.                              |
| __Semantic Categorization__   | Assigns domain-specific categories (e.g., *mass*, *energy*, *length*) to recognized units via a static lookup table.                       |
| __Structured Representation__ | Creates structured entities from matched expressions -- designed for downstream processing in NLP pipelines or annotation tools.           |

## Processing Workflow

1. __Input__: Raw text string containing potential measurement expressions
2. __Normalization__: Spacing corrections applied to improve pattern matching
3. __Pattern Matching__: Fast regex-based detection of candidate expressions
4. __Validation__: Slower detailed validation of numeric formats and unit
   formats using regular expressions
5. __Unit Categorization__: Semantic tags assigned based on unit classification
6. __Structured Output__: Matched expressions are converted into a list of Unit
  objects, each containing structured metadata for downstream use

# Maintenance & Extensibility

The __units__ module is designed with a clear separation of concerns: all
unit-related data -- including definitions, prefixes, spellings, and
classifications -- is maintained in a structured Excel file __units.xlsx__. This
file serves as the single source of truth, enabling collaborative editing and
transparent versioning.

Regular expressions for unit recognition are generated directly within
__units.xlsx__ using embedded formulas. These expressions are manually
transferred into the Python module __units.py__ as constants, without requiring
any changes to the core logic. This procedure enables updates and extensions to
be carried out securely and efficiently.

Adding new units to existing categories requires only an update to the Excel
file. For broader extensions -- such as introducing new semantic domains (e.g.
currencies or chemical symbols) -- the rule set in units.py can be adapted
accordingly. The modular design supports targeted enhancements without
compromising stability.

# Sources & References

- https://de.wikipedia.org/wiki/Internationales_Einheitensystem
- https://en.wikipedia.org/wiki/International_System_of_Units
- https://de.wikipedia.org/wiki/Gebr%C3%A4uchliche_Nicht-SI-Einheiten
- https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-5-units-outside-si
- https://www.taschenhirn.de/aktuelles-allgemeinwissen/liste-masseinheiten-formeln/
- https://www.tablesgenerator.com/markdown_tables
- https://copilot.microsoft.com
