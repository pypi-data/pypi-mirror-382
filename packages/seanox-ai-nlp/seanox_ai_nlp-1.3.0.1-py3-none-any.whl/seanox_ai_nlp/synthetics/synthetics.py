# seanox_ai_npl/synthetics/synthetics.py

from collections import deque, defaultdict
from dataclasses import dataclass
from jinja2 import (
    Environment,
    BaseLoader,
    DebugUndefined,
    Undefined,
    TemplateAssertionError
)
from typing import Callable, Any, Optional

import jsonschema
import os
import random
import re
import yaml


def _re_compile(expression: str, debug: bool = False) -> re.Pattern:
    expression = re.sub(r"\s{2,}|[\r\n]+", "", expression)
    if not debug:
        return re.compile(expression)
    return expression


def _re_unnamed_groups(expression: str) -> str:
    return re.sub(r"\(\?P<[^>]+>", "(?:", expression)


_ENTITY_MARKER_SIGNATURE_START = "[[["
_ENTITY_MARKER_SIGNATURE_END = "]]]"

_ENTITY_MARKER_NAME_RAW_PATTERN = r"\w(?:[\w\-]*\w)?"
_ENTITY_MARKER_START_RAW_PATTERN = rf"""
    (?:
        {re.escape(_ENTITY_MARKER_SIGNATURE_START)}
        (?P<entity_label>{_ENTITY_MARKER_NAME_RAW_PATTERN})
        {re.escape(_ENTITY_MARKER_SIGNATURE_END)}
    )
"""
_ENTITY_MARKER_END_RAW_PATTERN = rf"""
    (?:
        {re.escape(_ENTITY_MARKER_SIGNATURE_START)}
        (?:-)
        {re.escape(_ENTITY_MARKER_SIGNATURE_END)}
    )
"""
_ENTITY_MARKER_RAW_PATTERN = rf"""
    (?P<entity_start_tag>{_ENTITY_MARKER_START_RAW_PATTERN})
    (?P<entity_intermediate_text>.*?)
    (?P<entity_end_tag>{_ENTITY_MARKER_END_RAW_PATTERN})
"""

_ENTITY_MARKER_NAME_PATTERN = re.compile(rf"^{_ENTITY_MARKER_NAME_RAW_PATTERN}$")
_ENTITY_MARKER_PATTERN = _re_compile(_ENTITY_MARKER_RAW_PATTERN)
_ENTITY_MARKER_REGEX_PATTERN = _re_compile(rf"\{{\$(?:)({_ENTITY_MARKER_NAME_RAW_PATTERN})\}}")

_SEGMENT_PLACEHOLDER_NAME = r"(?:\w(?:[\w\-\:]*\w)?)"
_SEGMENT_PLACEHOLDER_INLINE = rf"@({_SEGMENT_PLACEHOLDER_NAME})"
_SEGMENT_PLACEHOLDER_BRACED = rf"{{@({_SEGMENT_PLACEHOLDER_NAME})}}"
_SEGMENT_PLACEHOLDER_PATTERN = re.compile(rf"{_SEGMENT_PLACEHOLDER_INLINE}|{_SEGMENT_PLACEHOLDER_BRACED}")

_FILTER_NAME_PATTERN = re.compile(r"^\w+$")

# Loose Requiredness, Strict Typing
# - wird segments verwendet, ist die Objekt-Struktur beliebig, nur die Sch
# - wird templates verwendet, muss die Objekt-Struktur darunter das Feld template besitzen
_YAML_SCHEMA = {
    "type": "object",
    "properties": {
        "templates": {
            "type": ["array", "null"],
            "items": {
                "type": "object",
                "properties": {
                    "template": {"type": ["string", "boolean", "number"]},
                    "name": {"type": ["string", "boolean", "number", "null"]},
                    "condition": {"type": ["string", "boolean", "number", "null"]},
                    "spans": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": ["string", "boolean", "number", "null"]},
                                "pattern": {"type": ["string", "boolean", "number", "null"]}
                            }
                        }
                    }
                }
            }
        },
        "segments": {"$ref": "#/$defs/segments"}
    },
    "$defs": {
        "segments": {
            "type": ["object", "null"],
            "propertyNames": {
                "pattern": r"^(?:\w(?:[\w\-\:]*\w)?)$"
            },
            "additionalProperties": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"},
                    {"type": "array"},
                    {"$ref": "#/$defs/segments"}
                ]
            }
        }
    }
}


def _annotate(value: Any = "", label: str = "") -> str:
    """
    The method is intended as a function in the template and annotates a given
    value with a structured entity marker if a valid label is provided.

    Designed for use as a Jinja2 filter. This function wraps the string
    representation of `value` with a custom marker format that includes the
    entity label. The format is designed for downstream processing, such as
    entity extraction.

    If the label is invalid or empty, the original value is returned unchanged.

    Example:
        {{ value | annotate("LABEL") }}
        produce: [[[LABEL]]]value[[[-]]]

    Args:
        value (Any): The value to annotate. Will be converted to a string.
        label (str): The entity label to apply. The same conventions apply as
            for variable names. In addition, the minus sign is permitted between
            word characters.

    Returns:
        str: The annotated string if the label is valid, otherwise the original
            value.
    """
    value = str(value)
    if not label or not _ENTITY_MARKER_NAME_PATTERN.match(label.strip()):
        return value
    if not value or not value.strip():
        return value
    return (
        f"{_ENTITY_MARKER_SIGNATURE_START}"
        f"{label.strip()}"
        f"{_ENTITY_MARKER_SIGNATURE_END}"
        f"{value}"
        f"{_ENTITY_MARKER_SIGNATURE_START}"
        f"-"
        f"{_ENTITY_MARKER_SIGNATURE_END}"
    )


def _random_range(items: list[Any], limit: int = -1) -> list[Any]:
    """
    Randomly selects and shuffles a subset of items from the provided list.

    Designed for use as a Jinja2 filter. This utility function picks a random
    number of elements (between 1 and `limit` or the length of `items`) from the
    input list, shuffles them, and returns the result. If the list is empty, an
    empty list is returned. If `limit` is negative, all items are considered.

    Example:
        {{ random_range(["apple", "banana", "cherry"], 2) }}
        might return: ["banana", "apple"]

    Args:
        items (list[Any]): The list of items to choose from.
        limit (int, optional): Maximum number of items to include. If negative,
            no limit is applied.

    Returns:
        list[Any]: A randomly selected and shuffled subset of the input list.
    """
    if not items:
        return []
    if limit < 0:
        limit = len(items)
    elif limit <= 0:
        return []
    count = random.randint(1, min(limit, len(items)))
    selection = random.sample(items, count)
    random.shuffle(selection)
    return selection


def _random_range_join(items: list[Any], separator: str = ", ", limit: int = -1) -> str:
    """
    The method is intended as a function in the template. It randomly selects
    and joins a subset of strings from the provided list using the given
    separator.

    Designed for use as a Jinja2 filter. This function picks a random number of
    items (between 1 and `limit` or the length of `items`) from the input list,
    shuffles them, and joins them into a single string using the specified
    separator.

    If the list is empty, an empty string is returned. If `limit` is negative,
    all items are considered.

    Example:
        {{ ["apple", "banana", "cherry"] | random_range_join(",", 2) }}
        might produce: "cherry, apple"

    Args:
        items (list[Any]): The list of strings to choose from.
        separator (str): The string used to separate the selected items.
        limit (int, optional): Maximum number of items to include. If negative,
            no limit is applied.

    Returns:
        str: A string of randomly selected and joined items, or an empty string
            if `items` is empty.
    """
    selection = [str(item) for item in _random_range(items, limit)]
    return separator.join(selection)


def _random_range_join_phrase(items: list[Any], separator: str = ", ", word: str = ", ", limit: int = -1) -> str:
    """
    The method is intended as a function in the template. It randomly selects
    and joins a subset of strings from the provided list into a natural-language
    phrase.

    Designed for use as a Jinja2 filter. This function randomly selects between
    1 and `limit` items from the list, shuffles them, and joins them into a
    phrase using the specified separator and conjunction word.

    The output mimics natural phrasing:
    - One item: returned as-is.
    - Two items: joined with the conjunction word (e.g., "apple and banana").
    - Three or more: joined with the separator, and the last item prefixed by
      the conjunction word (e.g., "apple, banana, and cherry").

    If the list is empty, an empty string is returned. If `limit` is negative,
    all items are considered.

    Example:
        {{ ["apple", "banana", "cherry"] | random_range_join_phrase(", ", " and ", 3) }}
        might produce: "banana, cherry and apple"

    Args:
        items (list[Any]): The list of strings to choose from.
        separator (str): The string used to separate items before the final one.
        word (str): The conjunction word used before the last item (e.g., "and",
            "or").
        limit (int, optional): Maximum number of items to include. If negative,
            no limit is applied.

    Returns:
        str: A natural-language phrase of randomly selected items, or an empty string if `items` is empty.
    """
    selection = [str(item) for item in _random_range(items, limit)]
    if len(selection) <= 0:
        return ""
    elif len(selection) == 1:
        return selection[0]
    elif len(selection) == 2:
        return f"{selection[0]}{word}{selection[1]}"
    else:
        return f"{separator.join(selection[:-1])}{word}{selection[-1]}"


def _random_set(items: list[Any], count: int = -1) -> list[Any]:
    """
    The method is intended as a function in the template. It randomly selects a
    subset of items from the provided list.

    Designed for use as a Jinja2 filter. This function returns a list containing
    up to `count` randomly selected items from `items`. If `count` is negative
    or exceeds the number of available items, all items are returned in random
    order. If the input list is empty, an empty list is returned.

    Unlike `_random_range_join` or `_random_range_join_phrase`, this function
    returns the raw list of selected items for further processing or formatting.

    Example:
        {{ ["apple", "banana", "cherry"] | random_set(2) }}
        might return: ["banana", "apple"]

    Args:
        items (list[Any]): The list of strings to choose from.
        count (int): The number of items to select.

    Returns:
        list[str]: A randomly selected subset of items, or an empty list if
            `items` is empty.
    """
    if not items:
        return []
    if count < 0:
        count = len(items)
    elif count <= 0:
        return []
    return random.sample(items, min(count, len(items)))


def _normalize(text: str = "") -> str:
    """
    Normalize whitespace in a string.

    Designed for use as a Jinja2 filter. This function removes leading and
    trailing whitespace characters, and replaces any sequence of one or more
    whitespace characters (spaces, tabs, newlines) within the string with a
    single space.

    Args:
        text (str): The input string to be cleaned.

    Returns:
        str: A string with normalized whitespace.

    Example:
        {{ " apple    banana    cherry " | normalize }}
        might return: "apple banana cherry"
    """
    if text is None:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


class TemplateException(Exception):
    def __init__(self, message):
        super().__init__(message)


class TemplateConditionException(TemplateException):
    def __init__(self, message):
        super().__init__(message)


class TemplateSyntaxException(TemplateException):
    def __init__(self, message):
        super().__init__(message)


class TemplateExpressionException(TemplateException):
    def __init__(self, message):
        super().__init__(message)


_SAFE_BUILTINS = {
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
    "any": any,
    "all": all,
    "abs": abs,
    "round": round,
    "sorted": sorted,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "range": range,
    "type": type,
    "list": list,
    "isinstance": isinstance,
}


def _flat_dict(tree: dict[str, Any], parent: str = "") -> dict[str, str]:
    if not tree:
        return {}
    items = {}
    for key, value in tree.items():
        new_key = f"{parent}:{key}" if parent else key
        if isinstance(value, dict):
            items.update(_flat_dict(value, new_key))
        else:
            items[new_key] = value
    return items


class _Template:

    @staticmethod
    def _create_template_environment(filters: dict[str, Callable] = None, validation: bool = False) -> Environment:

        environment = Environment(
            loader=BaseLoader(),
            trim_blocks=False,
            lstrip_blocks=False,
            undefined=Undefined if not validation else DebugUndefined
        )

        environment.filters["annotate"] = _annotate
        environment.filters["random_set"] = _random_set
        environment.filters["random_range"] = _random_range
        environment.filters["random_range_join"] = _random_range_join
        environment.filters["random_range_join_phrase"] = _random_range_join_phrase
        environment.filters["normalize"] = _normalize

        if filters:
            environment.filters.update(**filters)

        return environment

    def __init__(self, directory: str, filename: str, filters: dict[str, Callable] = None):

        self.variants = {}
        self.environment = _Template._create_template_environment(filters)

        if not filename or not filename.strip():
            raise ValueError("filename is required")
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

        if data:
            try:
                jsonschema.validate(instance=data, schema=_YAML_SCHEMA)
            except jsonschema.exceptions.ValidationError as exception:
                path_concat = lambda path: path[0] + "".join(
                    f"[{part}]" if isinstance(part, int) else f".{part}"
                    for part in path[1:]
                )
                raise TemplateException(
                    f"Template error ({type(exception).__name__})"
                    f" in {path_concat(list(exception.path))}: {str(exception.message)}"
                )

        parts = data.get("templates", [])
        if not isinstance(parts, list):
            return

        def _resolve_segments_sequential(segments: dict):

            keys = list(segments.keys())
            resolved = {}

            for index, key in enumerate(keys):
                value = segments[key]
                previous = {key: resolved[key] for key in keys[:index]}

                def _replace(match):
                    name = match.group(1) or match.group(2)
                    return previous.get(name, match.group(0))

                resolved[key] = _SEGMENT_PLACEHOLDER_PATTERN.sub(_replace, value)

            return resolved

        segments = data.get("segments")
        if segments:
            segments = _flat_dict(segments)
            segments = _resolve_segments_sequential(segments)

        def _replace_segments_placeholder(match):
            return segments.get(match.group(1) or match.group(2), match.group(0))

        for index, part in enumerate(parts):
            if not part.get("template"):
                continue
            name = str(part.get("name")) or f"#{str(index + 1)}"
            condition = str(part.get("condition")) or "True"

            content = str(part["template"]) + os.linesep
            content = _SEGMENT_PLACEHOLDER_PATTERN.sub(_replace_segments_placeholder, content)
            payload = re.sub(r"(\s*[\r\n]+\s*)+", " ", content).strip()

            try:
                environment = _Template._create_template_environment(filters, True)
                template = environment.from_string(payload)
                template.render({})
            except TemplateAssertionError as exception:
                raise TemplateException(
                    f"[{name}] Template error ({type(exception).__name__}): {str(exception)}"
                    f"{os.linesep}{content}"
                )
            except Exception as exception:
                raise TemplateSyntaxException(
                    f"[{name}] Template syntax error ({type(exception).__name__}): {str(exception)}"
                    f"{os.linesep}{content}"
                )

            try:
                template = self.environment.from_string(payload)
            except Exception as exception:
                raise TemplateException(
                    f"[{name}] Template error ({type(exception).__name__}): {str(exception)}"
                    f"{os.linesep}{content}"
                )

            if re.search(r"\b(__|import|exec|open|os|sys)\b", condition):
                raise TemplateConditionException(
                    f"[{name}] Condition token error"
                    f"{os.linesep}{str(condition)}"
                )

            try:
                compile(condition, "<condition>", "eval")
            except Exception as exception:
                raise TemplateConditionException(
                    f"[{name}] Condition error ({type(exception).__name__}): {str(exception)}"
                    f"{os.linesep}{str(condition)}"
                )

            patterns = {}
            labels = []

            for span in part.get("spans") or []:
                label = span.get("label")
                pattern = span.get("pattern")
                if label and pattern:
                    if label not in labels:
                        labels.append(label)
                        try:
                            re.compile(_ENTITY_MARKER_REGEX_PATTERN.sub("(?:LABEL|LABEL)", pattern))
                        except Exception as exception:
                            raise TemplateExpressionException(
                                f"[{name}] Expression error ({type(exception).__name__}): {str(exception)}"
                                f"{os.linesep}{str(_ENTITY_MARKER_REGEX_PATTERN.sub('(?:LABEL|LABEL)', pattern))}"
                            )
                        patterns[label] = pattern
            spans = {label: patterns[label] for label in labels}

            self.variants[index] = (name, template, condition, spans)

            self.registry = deque(maxlen=len(self.variants))

    def generate(self, data: dict[str, Any] = None) -> tuple[str, dict[str, Any]] | None:

        context = dict(data or {})
        context["random"] = random
        context["re"] = re

        templates = []
        for index, (name, template, condition, spans) in self.variants.items():
            try:
                if condition is None or eval(condition, {"__builtins__": _SAFE_BUILTINS}, context):
                    templates.append(index)
            except Exception as exception:
                raise TemplateConditionException(
                    f"[{name}] Condition error ({type(exception).__name__}): {str(exception)}"
                    f"{os.linesep}{str(condition)}"
                )

        if not templates:
            return None

        selection = []
        for index in templates:
            if index not in self.registry:
                selection.append(index)
        if selection:
            template_id = random.choice(selection)
        else:
            template_id = random.choice(templates)
        self.registry.append(template_id)

        name, template, condition, spans = self.variants[template_id]
        content = template.render(**context).strip()

        return content, spans


_TEMPLATES: dict[tuple[str, str], _Template] = {}


@dataclass
class Synthetic:
    """
    Represents the result of a synthetic text generation process including both
    raw and annotated text, as well as entity and span metadata.

    Attributes:
        text (str): The raw generated text without annotations.
        annotation (str): The annotated version of the text, including entity
            markers.
        entities (list[tuple[int, int, str]]): A list of entities found in the
            text. Each entity is represented as a tuple (start_index, end_index,
            label).
        spans (list[tuple[int, int, str]]): A list of pattern-based spans in the
            text. Each span is represented as a tuple (start_index, end_index,
            label).
    """
    text: str
    annotation: str
    entities: list[tuple[int, int, str]]
    spans: list[tuple[int, int, str]]


def _re_compile_span_pattern(labels: dict[str, set[str]], pattern: str) -> Optional[re.Pattern]:

    def replacer(match: re.Match) -> str:
        label = match.group(1)
        key = next((key for key in labels if key == label), None)
        if not key or not labels[key]:
            raise LookupError
        return "(?:" + "|".join(re.escape(value) for value in labels[key]) + ")"

    try:
        return re.compile(_ENTITY_MARKER_REGEX_PATTERN.sub(replacer, pattern))
    except LookupError:
        return None


def _extract_entities(text: str, patterns: dict[str, Any] = None) -> Synthetic:

    if patterns is None:
        patterns = {}
    entities: list[tuple[int, int, str]] = []
    plaintext = ""
    last_end = 0

    labels: dict[str, set[str]] = defaultdict(set)

    for match in _ENTITY_MARKER_PATTERN.finditer(text):
        span_start, span_end = match.span()

        label = match.group("entity_label")
        value = match.group("entity_intermediate_text")

        # Intermediate text, text without marker between the last end position
        # (cursor) and the current location of the marker being searched for.
        # The intermediate text is taken over and the cursor is repositioned at
        # the end of the plain text so that the correct span positions can be
        # calculated based on the plain text.
        intermediate_text = text[last_end:span_start]
        plaintext += intermediate_text

        try:
            entity_name = label
            entity_start = len(plaintext)
            entity_end = entity_start + len(value)
            plaintext += value
            entities.append((entity_start, entity_end, entity_name))
            labels[entity_name].add(value)
        except ValueError:
            plaintext += value

        last_end = span_end

    # text at the end, if no marker follows must be adopted
    plaintext += text[last_end:]

    entity_starts = {start for start, end, label in entities}
    entity_ends = {end for start, end, label in entities}

    labels = {key: list(value) for key, value in labels.items()}

    spans: list[tuple[int, int, str]] = []
    for label, pattern in patterns.items():
        pattern = _re_compile_span_pattern(labels, pattern)
        if not pattern:
            continue
        for match in pattern.finditer(plaintext):
            start, end = match.start(), match.end()
            if start in entity_starts and end in entity_ends:
                spans.append((start, end, label))

    return Synthetic(plaintext, text, entities, spans)


def synthetics(
        datasource: str,
        template: str,
        data: dict[str, Any] = None,
        filters: dict[str, Callable] = None
) -> Synthetic:
    """
    Generates synthetic text using predefined YAML templates.

    The function loads template definitions from a YAML file located in the
    datasource directory (e.g. synthetics_en.yaml). It evaluates the conditions
    specified for each template, filters the matching entries, randomly selects
    one of them, and renders the final output using the Jinja2 templating
    engine.

    Templates are cached internally to improve performance on repeated
    invocations.

    Parameters:
        datasource (str): Path to the directory containing template files.
        template (str): Name of the template file.
        data (dict): Contextual data used to evaluate conditions and render the
            template.
        filters (dict, optional): Additional custom filters for template
            rendering. Keys are filter names (str), and values are callable
            objects (callables) that implement the filter.

    Returns:
        Synthetic: A dataclass containing the generated synthetic text, its
            annotated version, and metadata about entities and spans.

        Example:
            Synthetic(
                text="The Earth is a planet.",
                annotation="The [[[PLANET]]]Earth[[[-]]] is a [[[TERM]]]planet[[[-]]].",
                entities=[(4, 9, "PLANET"), (15, 21, "TERM")],
                spans = [(4, 9, "PAIR"), (15, 21, "PAIR")]
            )

    Raises:
        FileNotFoundError: If the YAML template file for the given language
            cannot be found at the specified path.
        TemplateException: If the template file cannot be loaded or parsed.
        TemplateConditionException: If a condition expression in the template
            is invalid or unsafe to evaluate.
        TemplateExpressionException: If a span expression in the template is
            invalid.
    """

    filters = {
        name: function
        for name, function in (filters or {}).items()
        if name and _FILTER_NAME_PATTERN.match(name) and callable(function)
    }

    if not template or not template.strip():
        return Synthetic("", "", [], [])

    # Cache key consists of: (data source, template, flat sequence of (key,
    # value) from filters sorted by key). For callables, equality is by object
    # identity – the same function object must be referenced.
    signature = (
        (datasource or "", template)
        + tuple(entry for pairs in sorted(filters.items()) for entry in pairs)
    )
    if signature not in _TEMPLATES:
        _TEMPLATES[signature] = _Template(datasource, template, filters)
    template = _TEMPLATES[signature]
    result = template.generate(data)
    if not result:
        return Synthetic("", "", [], [])
    return _extract_entities(*result)
