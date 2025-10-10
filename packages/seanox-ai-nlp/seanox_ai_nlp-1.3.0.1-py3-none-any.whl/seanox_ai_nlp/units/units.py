# seanox_ai_npl/units/units.py

# DESIGN NOTE
#
# This module relies entirely on statically aggregated and precompiled data
# structures derived from an external structured Excel source. The decision to
# embed unit definitions and classification patterns directly into the code is
# intentional and performance-driven.
#
# Rationale:
# - The unit data is curated and maintained externally in an Excel file.
# - At build time, the relevant entries are aggregated and transformed into
#   static regex-compatible strings and dictionaries.
# - This avoids runtime file I/O, dynamic parsing, or external dependencies.
# - All regex patterns are precompiled to maximize performance during text
#   processing.
#
# Trade-offs:
# - Flexibility is reduced: updates require regeneration of the static data.
# - Readability may be impacted due to the dense format of embedded strings.
# - However, this approach ensures high-speed recognition and classification of
#   units in NLP pipelines, especially when processing large volumes of text.
#
# Summary:
# This module prioritizes performance and reliability over dynamic flexibility.
# It is designed for production-grade NLP tasks where speed and consistency are
# critical.

from typing import Optional, NamedTuple
from enum import Enum
from functools import lru_cache

import re


def _re_compile(expression: str, debug: bool = False) -> re.Pattern:
    expression = re.sub(r"\s{2,}|[\r\n]+", "", expression)
    if not debug:
        return re.compile(expression)
    return expression


def _re_reverse_units(expression: str) -> str:
    units = expression[3:-1].split("|")
    units = sorted(units, key=lambda string: string.lower(), reverse=True)
    return f"(?:{'|'.join(units)})"


# Patterns generated from the Excel file
_UNIT_SYMBOLS_PATTERN = r"(?:\'|\"|%|\u2032|\u2033|A|A|a|AE|Ah|atm|At\u00FC|AU|b|B|B|bar|baud|bbl|Bit|bps|Bq|Byte|C|cd|cd|ct|d|Da|dam|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpi|DPI|dpt|dz|dz|eV|F|FLOPS|fps|ft|g|g|gal|Gy|H|h|ha|hL|hl|hp|Hz|in|J|K|K|kat|kn|kt|kt|l|L|lb|lj|lm|ls|lx|m|m|mel|mi|mile|min|MIPS|mol|mol|mph|N|Np|\u00BA|\u00BAC|oz|oz.|oz\. tr\.|p|Pa|pc|PPI|ppi|PS|pt|px|rad|rm|RPM|s|s|S|sone|sr|St|Sv|t|T|tex|u|V|VA|Var|vCore|W|Wb|Wh|yd|Z|\u03C9|\u03A9)"
_UNIT_SI_SYMBOLS_BASE_PATTERN = r"(?:A|cd|g|K|m|mol|s)"
_UNIT_SI_SYMBOLS_DERIVATION_PATTERN = r"(?:Bq|C|F|Gy|H|Hz|J|kat|lm|lx|N|\u00BAC|Pa|rad|S|sr|Sv|T|V|W|Wb|\u03A9)"
_UNIT_SI_SYMBOLS_EXTENSION_PATTERN = r"(?:a|AE|Ah|AU|b|B|bar|ct|d|Da|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpt|eV|h|ha|hL|hl|kn|kt|l|L|mel|min|Np|oz\. tr\.|PS|pt|sone|tex|VA|Wh)"
_UNIT_SI_SYMBOLS_RELEVANT_PATTERN = r"(?:A|a|AE|Ah|AU|b|B|B|bar|baud|Bit|bps|Bq|Byte|C|cd|ct|d|Da|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpt|eV|F|FLOPS|g|Gy|H|h|ha|hL|hl|Hz|J|K|kat|kn|kt|l|L|lm|lx|m|mel|min|MIPS|mol|N|Np|\u00BAC|oz\. tr\.|Pa|PS|pt|rad|s|S|sone|sr|Sv|T|tex|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_M_PATTERN = r"(?:A|b|B|Bit|bps|Bq|Byte|C|cd|Da|eV|F|FLOPS|g|Gy|H|Hz|J|kat|lm|lx|m|MIPS|N|Pa|S|Sv|T|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_S_PATTERN = r"(?:A|b|B|Bit|bps|Bq|Byte|C|cd|Da|eV|F|FLOPS|g|Gy|H|Hz|J|kat|l|L|lm|lx|m|MIPS|N|Pa|s|S|Sv|T|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_SUFFIX_PATTERN = r"(?:A|Bq|C|F|g|H|J|kat|l|L|lm|lx|m|mol|Pa|s|S|sr|T|V|W|Wb|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN = r"(?:A|Bq|C|F|g|H|J|kat|lm|lx|m|Pa|S|T|V|W|Wb|\u03A9)"
_UNIT_IEC_SYMBOLS_PATTERN = r"(?:B)"
_UNIT_COMMON_SYMBOLS_PATTERN = r"(?:\'|\"|%|\u2032|\u2033|a|AE|Ah|atm|At\u00FC|AU|B|bar|bbl|ct|d|dam|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpi|DPI|dpt|dz|dz|fps|ft|gal|h|ha|hp|in|K|kn|kt|kt|l|L|lb|lj|ls|mel|mi|min|mol|Np|\u00BA|\u00BAC|oz|oz.|oz\. tr\.|p|pc|PPI|ppi|PS|pt|px|rad|rm|RPM|s|sone|sr|St|t|tex|u|Var|vCore|yd|Z|\u03C9)"
_UNIT_INFORMAL_SYMBOLS_PATTERN = r"(?:ft|in|m|mi|mile|mph|yd)"

# The units are sorted alphabetically, which means that shorter ones such as "p"
# appear before longer ones such as "px". In the regular expression, "p" is then
# recognized, even though "px" is meant. To avoid this, the order is reversed
# using the method _re_reverse_units(expression: str) -> str -- longer and more
# specific units appear first and are recognized correctly.

_UNIT_SYMBOLS_PATTERN = _re_reverse_units(_UNIT_SYMBOLS_PATTERN)
_UNIT_SI_SYMBOLS_BASE_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_BASE_PATTERN)
_UNIT_SI_SYMBOLS_DERIVATION_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_DERIVATION_PATTERN)
_UNIT_SI_SYMBOLS_EXTENSION_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_EXTENSION_PATTERN)
_UNIT_SI_SYMBOLS_RELEVANT_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_RELEVANT_PATTERN)
_UNIT_SI_SYMBOLS_M_PREFIX_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_PREFIX_M_PATTERN)
_UNIT_SI_SYMBOLS_S_PREFIX_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_PREFIX_S_PATTERN)
_UNIT_SI_SYMBOLS_SUFFIX_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_SUFFIX_PATTERN)
_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN = _re_reverse_units(_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN)
_UNIT_IEC_SYMBOLS_PATTERN = _re_reverse_units(_UNIT_IEC_SYMBOLS_PATTERN)
_UNIT_COMMON_SYMBOLS_PATTERN = _re_reverse_units(_UNIT_COMMON_SYMBOLS_PATTERN)
_UNIT_INFORMAL_SYMBOLS_PATTERN = _re_reverse_units(_UNIT_INFORMAL_SYMBOLS_PATTERN)

_UNIT_SI_PREFIX_M_PATTERN = r"(?:Q|R|Y|Z|E|P|T|G|M|k|h|da)"
_UNIT_SI_PREFIX_S_PATTERN = r"(?:d|c|m|\u00B5|n|p|f|a|z|y|r|q)"
_UNIT_SI_SUFFIX_PATTERN = r"(?:\u207B?[\u00B9\u00B2\u00B3])"
_UNIT_SI_SYMBOLS_RELEVANT_SET = set(_UNIT_SI_SYMBOLS_RELEVANT_PATTERN[3:-1].split("|"))

_UNIT_IEC_PREFIX_PATTERN = r"(?:Ki|Mi|Gi|Ti|Pi|Ei|Zi|Yi)"

_UNIT_INFORMAL_SYMBOLS_SET = set(_UNIT_INFORMAL_SYMBOLS_PATTERN[3:-1].split("|"))
_UNIT_INFORMAL_SI_SYMBOLS_SET = _UNIT_INFORMAL_SYMBOLS_SET & _UNIT_SI_SYMBOLS_RELEVANT_SET
_UNIT_INFORMAL_SI_SYMBOLS_PATTERN = rf"(?:{'|'.join(_UNIT_INFORMAL_SI_SYMBOLS_SET)})"
_UNIT_INFORMAL_COMMON_SYMBOLS_SET = _UNIT_INFORMAL_SYMBOLS_SET - _UNIT_SI_SYMBOLS_RELEVANT_SET
_UNIT_INFORMAL_COMMON_SYMBOLS_PATTERN = rf"(?:{'|'.join(_UNIT_INFORMAL_COMMON_SYMBOLS_SET)})"
_UNIT_INFORMAL_PREFIX_PATTERN = r"(?:c|q|sq\.\s?)"
_UNIT_INFORMAL_SUFFIX_PATTERN = r"(?:2|3)"

_NUMERIC_LOOK_AHEAD_PATTERN = r"(?:(?<![\u00B1+\-,\.\u2019\w\d])|^)"
_NUMERIC_SIGN_PATTERN = r"[\u00B1+\-~]"
_NUMERIC_DE_PATTERN = r"(?:(?:(?:\d{1,3}(?:\.\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_EN_PATTERN = r"(?:(?:(?:\d{1,3}(?:,\d{3})*)|\d+)(?:\.\d+)?)"
_NUMERIC_CH_PATTERN = r"(?:(?:(?:\d{1,3}(?:\u2019\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_FR_PATTERN = r"(?:(?:(?:\d{1,3}(?: \d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_IN_PATTERN = r"(?:(?:(?:(?:(?:\d{1,2},)(?:\d{2},)*)?\d{3})|\d+)(?:\.\d+)?)"
_NUMERIC_ISO_PATTERN = r"(?:(?:(?:\d{1,3}(?:[\u00A0\u202F]\d{3})*)|\d+)(?:\.\d+)?)"

_NUMERIC_DIMENSIONAL_SEPARATORS_PATTERN = r"(?:[*+\-/:\^x\u00B1\u00D7\u00B7\u00F7\u2012\u2013\u2014\u2212])"

_NUMERIC_PATTERN = rf"""
    (?:
      {_NUMERIC_DE_PATTERN}
      |{_NUMERIC_EN_PATTERN}
      |{_NUMERIC_CH_PATTERN}
      |{_NUMERIC_FR_PATTERN}
      |{_NUMERIC_IN_PATTERN}
      |{_NUMERIC_ISO_PATTERN}
    )
"""

_NUMERIC_EXPRESSION_PATTERN = rf"""
    (?:
      {_NUMERIC_SIGN_PATTERN}?
      {_NUMERIC_PATTERN}
      (?:
        \s*
        {_NUMERIC_DIMENSIONAL_SEPARATORS_PATTERN}
        \s*
        {_NUMERIC_PATTERN}
      )*
    )
"""

# RegEx for numerical values in various formats.
NUMERIC_PATTERN = _re_compile(_NUMERIC_EXPRESSION_PATTERN)

# RegEx with dimensional separators that combine numeric values into a numeric
# expression.
NUMERIC_DIMENSIONAL_SEPARATORS_PATTERN = _re_compile(_NUMERIC_DIMENSIONAL_SEPARATORS_PATTERN)

# RegEx for validating numeric values..
NUMERIC_VALIDATION_PATTERN = _re_compile(rf"^{_NUMERIC_PATTERN}$")

# RegEx for validating numeric expressions.
NUMERIC_EXPRESSION_VALIDATION_PATTERN = _re_compile(rf"^{_NUMERIC_EXPRESSION_PATTERN}$")

# RegEx for all supported units.
UNIT_SYMBOLS_PATTERN = _re_compile(rf"({_UNIT_SYMBOLS_PATTERN})")

_UNIT_INFORMAL_SI_RAW_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_PREFIX_PATTERN}?
      (?:{_UNIT_SI_PREFIX_M_PATTERN}|{_UNIT_SI_PREFIX_S_PATTERN})?
      {_UNIT_INFORMAL_SI_SYMBOLS_PATTERN}
      (?:
        {_UNIT_INFORMAL_SUFFIX_PATTERN}
        |{_UNIT_SI_SUFFIX_PATTERN} 
      )?
    )
"""

_UNIT_INFORMAL_COMMON_RAW_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_PREFIX_PATTERN}?
      {_UNIT_INFORMAL_COMMON_SYMBOLS_PATTERN}
      {_UNIT_INFORMAL_SUFFIX_PATTERN}?
    )
"""

_UNIT_INFORMAL_RAW_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_SI_RAW_PATTERN}
      |{_UNIT_INFORMAL_COMMON_RAW_PATTERN}
    )
"""

_UNIT_OPERATORS_PATTERN = r"(?:(?:\s*[*/\u00B7\u00D7]\s*)|(?:\s+x\s+))"

# RegEx for operators that combine units into compound unit expressions.
UNIT_OPERATORS_PATTERN = _re_compile(_UNIT_OPERATORS_PATTERN)

_UNIT_LOOK_AHEAD_PATTERN = r"(?:(?<=[\W\d])|^)"
_UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN = r"(?<=\d)"
_UNIT_LOOK_BEHIND_PATTERN = r"(?:(?=[^\w\u00B7\u002F])|$)"
_UNIT_MULTIPLE_SPACES = r"(?:\s{2,})"

_UNIT_SI_RAW_PATTERN = rf"""
    (?:(?:{_UNIT_SI_PREFIX_M_PATTERN}|{_UNIT_SI_PREFIX_S_PATTERN})?
    {_UNIT_SI_SYMBOLS_RELEVANT_PATTERN}
    {_UNIT_SI_SUFFIX_PATTERN}?)
"""

_UNIT_COMMON_RAW_PATTERN = rf"""
    (?:{_UNIT_COMMON_SYMBOLS_PATTERN})
"""

_UNIT_IEC_RAW_PATTERN = rf"""
    (?:{_UNIT_IEC_PREFIX_PATTERN}?
    {_UNIT_IEC_SYMBOLS_PATTERN})
"""

_UNIT_RAW_PATTERN = rf"""
    (?:
      {_UNIT_SI_RAW_PATTERN}
      |{_UNIT_INFORMAL_RAW_PATTERN}
      |{_UNIT_IEC_RAW_PATTERN}
      |{_UNIT_COMMON_RAW_PATTERN}
    )
"""

_UNIT_EXPRESSION_RAW_PATTERN = rf"""
    (?:
      {_UNIT_RAW_PATTERN}
      (?:
        {_UNIT_OPERATORS_PATTERN}
        {_UNIT_RAW_PATTERN}
      )*
    )
"""

_UNIT_VALUE_PATTERN = rf"""
    {_NUMERIC_LOOK_AHEAD_PATTERN}
    (?P<unit_value_numeric>{_NUMERIC_EXPRESSION_PATTERN})
    \s*
    (?P<unit_value_unit>{_UNIT_EXPRESSION_RAW_PATTERN})
    {_UNIT_LOOK_BEHIND_PATTERN}
"""

_UNIT_PATTERN = rf"""
    {_UNIT_LOOK_AHEAD_PATTERN}
    (?P<unit_unit>{_UNIT_EXPRESSION_RAW_PATTERN})
    {_UNIT_LOOK_BEHIND_PATTERN}
"""

# RegEx for detecting measured values and units
UNIT_PATTERN = _re_compile(rf"""
    {_UNIT_VALUE_PATTERN}
    |{_UNIT_PATTERN}
""")

_UNIT_WITH_INVALID_SPACES_NUMERIC_PATTERN = _re_compile(rf"""
    (?<=\d)(\s{{2,}})?
    {_UNIT_EXPRESSION_RAW_PATTERN}
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_WITH_INVALID_SPACES_ALPHANUMERIC_PATTERN = _re_compile(rf"""
    (?:
      (?:
        (?<=\d)(\s{{2,}})?)
        |(?:(?<=\w)(\s{{2,}})
      )
    )
    {_UNIT_EXPRESSION_RAW_PATTERN}
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_WITH_INVALID_SPACES_ALL_PATTERN = _re_compile(rf"""
    (?:
      (?:(?<=\d)(\s{{2,}})?{_UNIT_EXPRESSION_RAW_PATTERN})
      |(?:\s{{2,}}{_UNIT_EXPRESSION_RAW_PATTERN})
      |(?:(?<=[.,:;!?%])(\s{{2,}})?{_UNIT_EXPRESSION_RAW_PATTERN})
    )
    {_UNIT_LOOK_BEHIND_PATTERN}  
""")

_UNIT_SI_VALIDATION_PATTERN = rf"""
    (?:
      (?:
        (?:{_UNIT_SI_PREFIX_M_PATTERN}|{_UNIT_SI_PREFIX_S_PATTERN})
        {_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN}
        {_UNIT_SI_SUFFIX_PATTERN}
      )
      |
      (?:
        {_UNIT_SI_PREFIX_M_PATTERN}
        {_UNIT_SI_SYMBOLS_PREFIX_M_PATTERN}
      )
      |
      (?:
        {_UNIT_SI_PREFIX_S_PATTERN}
        {_UNIT_SI_SYMBOLS_PREFIX_S_PATTERN}
      )
      |
      (?:
        {_UNIT_SI_SYMBOLS_SUFFIX_PATTERN}
        {_UNIT_SI_SUFFIX_PATTERN}
      )
      |{_UNIT_SI_SYMBOLS_RELEVANT_PATTERN}
    )  
"""

_UNIT_COMMON_VALIDATION_PATTERN = rf"""
    (?:{_UNIT_COMMON_SYMBOLS_PATTERN})
"""

_UNIT_INFORMAL_VALIDATION_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_PREFIX_PATTERN}?
      {_UNIT_INFORMAL_SYMBOLS_PATTERN}
      {_UNIT_INFORMAL_SUFFIX_PATTERN}?    
    )
"""

_UNIT_IEC_VALIDATION_PATTERN = rf"""
    (?:
      {_UNIT_IEC_PREFIX_PATTERN}?
      {_UNIT_IEC_SYMBOLS_PATTERN}
    )
"""

_UNIT_VALIDATION_PATTERN = rf"""
    (?:
      {_UNIT_SI_VALIDATION_PATTERN}
      |{_UNIT_INFORMAL_VALIDATION_PATTERN}
      |{_UNIT_IEC_VALIDATION_PATTERN}
      |{_UNIT_COMMON_VALIDATION_PATTERN}
    )
"""

# RegEx for validating units.
UNIT_VALIDATION_PATTERN = _re_compile(rf"^{_UNIT_VALIDATION_PATTERN}")

# RegEx for validating unit expressions.
UNIT_EXPRESSION_VALIDATION_PATTERN = _re_compile(rf"""
    ^(?:
      {_UNIT_VALIDATION_PATTERN}
      (?:
        {_UNIT_OPERATORS_PATTERN}
        {_UNIT_VALIDATION_PATTERN}
      )*
    )$
""")

_UNIT_SI_CLASSIFICATION_PATTERN = rf"""
    (?:
      (?:
        (?P<unit_si_prefix_suffix_prefix>(?:{_UNIT_SI_PREFIX_M_PATTERN}|{_UNIT_SI_PREFIX_S_PATTERN}))
        (?P<unit_si_prefix_suffix_symbol>{_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN})
        (?P<unit_si_prefix_suffix_suffix>{_UNIT_SI_SUFFIX_PATTERN})
      )
      |
      (?:
        (?P<unit_si_prefix_prefix>{_UNIT_SI_PREFIX_M_PATTERN})
        (?P<unit_si_prefix_symbol>{_UNIT_SI_SYMBOLS_PREFIX_M_PATTERN})
      )
      |
      (?:
        (?P<unit_si_prefix_prefix>{_UNIT_SI_PREFIX_S_PATTERN})
        (?P<unit_si_prefix_symbol>{_UNIT_SI_SYMBOLS_PREFIX_S_PATTERN})
      )
      |
      (?:
        (?P<unit_si_suffix_symbol>{_UNIT_SI_SYMBOLS_SUFFIX_PATTERN})
        (?P<unit_si_suffix_suffix>{_UNIT_SI_SUFFIX_PATTERN})
      )
      |(?P<unit_si_symbol>{_UNIT_SI_SYMBOLS_RELEVANT_PATTERN})
    )  
"""

_UNIT_COMMON_CLASSIFICATION_PATTERN = rf"""
    (?P<unit_common_symbol>{_UNIT_COMMON_SYMBOLS_PATTERN})
"""

_UNIT_INFORMAL_CLASSIFICATION_PATTERN = rf"""
    (?:
      (?P<unit_informal_prefix>{_UNIT_INFORMAL_PREFIX_PATTERN})?
      (?P<unit_informal_symbol>{_UNIT_INFORMAL_SYMBOLS_PATTERN})
      (?P<unit_informal_suffix>{_UNIT_INFORMAL_SUFFIX_PATTERN})?    
    )
"""

_UNIT_IEC_CLASSIFICATION_PATTERN = rf"""
    (?:
      (?P<unit_iec_prefix>{_UNIT_IEC_PREFIX_PATTERN})?
      (?P<unit_iec_symbol>{_UNIT_IEC_SYMBOLS_PATTERN})
    )
"""

# RegEx for classification with OR linked named groups.
UNIT_CLASSIFICATION_PATTERN = UNIT_SYMBOLS_PATTERN

def _dict_from_comma_separated_pairs(data: str) -> dict[str, str]:
    result = {}
    data = re.sub(r"\s*\|\s*[\r\n]\s*", "", data.strip())
    items = re.split(r"\s*\|\s*", data)
    for item in range(1, len(items) - 1, 2):
        key = items[item].strip()
        value = items[item + 1].strip()
        if key and value:
            result.setdefault(key, []).extend(value.split())
    return result


# For better maintainability and error analysis, a proprietary inline format
# that is not CSV is deliberately used, as it is only used internally and the
# format is fully controlled.
_UNIT_CLASSIFICATION_DICT = _dict_from_comma_separated_pairs(r"""
| '         | length                        | d         | time                          | hl        | volume                        | N         | force                         | T         | magnetic field                |
| "         | length                        | Da        | mass atomic                   | hp        | power                         | Np        | acoustics                     | tex       | mass                          |
| %         | ratio                         | dam       | length                        | Hz        | frequency                     | \u00BA    | angle                         | u         | mass atomic                   |
| \u2032    | length                        | dB        | acoustics                     | in        | length                        | \u00BAC   | temperature                   | V         | electricity                   |
| \u2033    | length                        | db(A)     | acoustics                     | J         | energy                        | oz        | mass                          | VA        | electricity power             |
| A         | electricity                   | db(C)     | acoustics                     | K         | temperature                   | oz.       | mass                          | Var       | electricity power             |
| a         | area                          | db(G)     | acoustics                     | kat       | amount                        | oz. tr.   | mass                          | vCore     | it processing amount          |
| AE        | length astronomy              | db(Z)     | acoustics                     | kn        | speed                         | p         | force                         | W         | power                         |
| Ah        | electricity                   | dpi       | it graphics                   | kt        | mass                          | Pa        | pressure                      | Wb        | magnetism                     |
| atm       | pressure                      | DPI       | it graphics                   | kt        | speed                         | pc        | length astronomy              | Wh        | energy                        |
| At\u00FC  | pressure                      | dpt       | optics                        | l         | volume                        | PPI       | it graphics area              | yd        | length                        |
| AU        | length astronomy              | dz        | quantity                      | L         | volume                        | ppi       | it graphics area              | Z         | mass                          |
| b         | area radiation                | dz        | quantity                      | lb        | mass                          | PS        | power                         | \u03C9    | frequency rotation            |
| B         | acoustics                     | eV        | energy                        | lj        | length astronomy              | pt        | volume                        | \u03A9    | electricity                   |
| B         | it storage                    | F         | electricity capacitance       | lm        | light                         | px        | it graphics                   |           |                               |
| bar       | pressure                      | FLOPS     | it processing time            | ls        | light energy                  | rad       | angle                         |           |                               |
| baud      | It network time               | fps       | it graphics video time        | lx        | light                         | rm        | volume                        |           |                               |
| bbl       | volume                        | ft        | length                        | m         | length                        | RPM       | it frequency rotation time    |           |                               |
| Bit       | it storage                    | g         | mass                          | mel       | acoustics                     | s         | time                          |           |                               |
| bps       | it network time               | gal       | volume                        | mi        | length                        | S         | electricity conductance       |           |                               |
| Bq        | radiation                     | Gy        | radiation                     | mile      | length                        | sone      | acoustics                     |           |                               |
| Byte      | it storage                    | H         | electricity                   | min       | time                          | sr        | angle                         |           |                               |
| C         | electricity                   | h         | time                          | MIPS      | it processing time            | St        | volume                        |           |                               |
| cd        | light                         | ha        | area                          | mol       | amount                        | Sv        | radiation                     |           |                               |
| ct        | mass                          | hL        | volume                        | mph       | length time                   | t         | mass                          |           |                               |
""")


class SpacingMode(Enum):
    """
    Specifies patterns used to correct spacing between numeric/alphanumeric
    expressions and unit identifiers.

    Modes:
    - NUMERIC: Applies to spacing between numeric values and unit expressions.
    - ALPHANUMERIC: Applies to alphanumeric strings followed by unit expressions.
    - ALL: Applies broadly to numeric, alphanumeric, and special-character contexts.
    """
    NUMERIC = _UNIT_WITH_INVALID_SPACES_NUMERIC_PATTERN
    ALPHANUMERIC = _UNIT_WITH_INVALID_SPACES_ALPHANUMERIC_PATTERN
    ALL = _UNIT_WITH_INVALID_SPACES_ALL_PATTERN


def spacing(text: str, mode: SpacingMode = SpacingMode.NUMERIC) -> str:
    """
    Corrects invalid spacing between numbers and unit expressions.

    Args:
        text (str): Input string to be corrected
        mode (SpacingMode, optional): Correction mode for spacing.
            Default is SpacingMode.NUMERIC.

    Returns:
        str: Corrected text with corrected spacing
    """
    text = mode.value.sub(
        lambda match: " " + match.group(0).strip(),
        text
    )
    return text


class Unit(NamedTuple):
    """
    Represents a recognized unit entity extracted from text.

    Attributes:
        label (str): Classification label, e.g. 'MEASURE'.
        start (int): Start index of the unit in the original text.
        end (int): End index of the unit in the original text.
        text (str): Raw text fragment containing the unit.
        categories (tuple[str, ...]): Assigned semantic categories for the unit.
        unit (str): The extracted unit string (e.g. 'kg', 'm').
        value (Optional[str]): The numerical value associated with the unit, if present.
    """
    label: str
    start: int
    end: int
    text: str
    categories: tuple[str, ...]
    unit: str
    value: Optional[str] = None


@lru_cache(maxsize=256)
def _get_categories_for_unit(unit: str) -> tuple[str, ...]:
    categories = set()
    unit = UNIT_SYMBOLS_PATTERN.sub(r" \1 ", unit).strip()
    for unitEntry in UNIT_OPERATORS_PATTERN.split(unit):
        match = UNIT_CLASSIFICATION_PATTERN.search(unitEntry)
        categories.update(_UNIT_CLASSIFICATION_DICT.get(match.group(0), []))
    return tuple(sorted(categories))


def units(text: str) -> list[Unit]:
    """
    Extracts valid unit expressions and associated numeric values from a given text.

    Args:
        text (str): Input string to analyze.

    Returns:
        list[Unit]: List of Unit objects representing detected unit entities.

    Notes:
        - Only units matching known validation patterns will be returned.
        - Numeric expression preceding units will be included when available.
        - Designed for use in NLP pipelines, extraction, and preprocessing tasks.
    """

    if not text:
        return []

    entities = []
    for match in UNIT_PATTERN.finditer(text):
        groups = match.groupdict()
        numeric = groups.get("unit_value_numeric")
        unit = groups.get("unit_value_unit") or groups.get("unit_unit")

        if not (UNIT_EXPRESSION_VALIDATION_PATTERN.match(unit)):
            continue

        if numeric:
            entities.append(
                Unit(
                    label="MEASURE",
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    unit=unit,
                    value=numeric,
                    categories=_get_categories_for_unit(unit)
                )
            )
        else:
            entities.append(
                Unit(
                    label="UNIT",
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    unit=unit,
                    categories=_get_categories_for_unit(unit)
                )
            )

    return entities
