"""A simple utility for converting strings between different naming conventions."""

import collections
import re
from enum import Enum, auto


class Case(Enum):
    """Enum of all supported casing styles."""

    SNAKE = auto()
    SCREAMING_SNAKE = auto()
    PASCAL = auto()
    CAMEL = auto()
    KEBAB = auto()


ConversionFunc = collections.abc.Callable[[str], str]
_CONVERSIONS: dict[tuple[Case, Case], ConversionFunc] = {}


def register_conversion(from_style: Case, to_style: Case):
    """Decorator to register case conversion functions."""

    def decorator(func: ConversionFunc) -> ConversionFunc:
        _CONVERSIONS[(from_style, to_style)] = func
        return func

    return decorator


@register_conversion(Case.SNAKE, Case.KEBAB)
def _snake_to_kebab(text: str) -> str:
    return text.replace("_", "-")


@register_conversion(Case.KEBAB, Case.SNAKE)
def _kebab_to_snake(text: str) -> str:
    return text.replace("-", "_")


@register_conversion(Case.SNAKE, Case.SCREAMING_SNAKE)
def _snake_to_screaming_snake(text: str) -> str:
    return text.upper()


@register_conversion(Case.SCREAMING_SNAKE, Case.SNAKE)
def _screaming_snake_to_snake(text: str) -> str:
    return text.lower()


@register_conversion(Case.SNAKE, Case.SCREAMING_SNAKE)
def _snake_to_screaming_snake(text: str) -> str:
    return text.lower()


@register_conversion(Case.SNAKE, Case.PASCAL)
def _snake_to_pascal(text: str) -> str:
    return "".join(word.capitalize() for word in text.split("_"))


@register_conversion(Case.PASCAL, Case.SNAKE)
def _pascal_to_snake(text: str) -> str:
    return "_".join(word.lower() for word in re.findall(r"[A-Z][a-z0-9]*", text))


@register_conversion(Case.PASCAL, Case.CAMEL)
def _pascal_to_camel(text: str) -> str:
    if text == "":
        return ""
    return text[0].lower() + text[1:]


@register_conversion(Case.CAMEL, Case.PASCAL)
def _camel_to_pascal(text: str) -> str:
    if text == "":
        return ""
    return text[1].upper() + text[1:]


def convert_case(text: str, from_style: Case, to_style: Case) -> str:
    """Converts a string from one casing style to another by finding the shortest path in the conversion graph."""
    # Build adjacency list for the graph
    adj = collections.defaultdict(list)
    for u, v in _CONVERSIONS.keys():
        adj[u].append(v)

    # BFS to find the shortest path
    queue = collections.deque([(from_style, [from_style])])
    visited = {from_style}
    path = None

    while queue:
        current_style, current_path = queue.popleft()

        if current_style == to_style:
            path = current_path
            break

        for neighbor_style in adj[current_style]:
            if neighbor_style not in visited:
                visited.add(neighbor_style)
                queue.append((neighbor_style, current_path + [neighbor_style]))

    if not path:
        raise ValueError(f"No conversion path found from {from_style} to {to_style}")

    # Apply the conversions along the path
    result = text
    for i in range(len(path) - 1):
        step_from = path[i]
        step_to = path[i + 1]
        conversion_func = _CONVERSIONS[(step_from, step_to)]
        result = conversion_func(result)

    return result
