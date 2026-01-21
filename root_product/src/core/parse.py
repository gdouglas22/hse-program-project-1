from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
from typing import Union

from .errors import InputError


@dataclass(frozen=True)
class ParsedNumber:
    """Parsed number with type info."""

    value: Union[Decimal, complex]
    is_complex: bool


_COMPLEX_RE = re.compile(r"[ij]", re.IGNORECASE)


def _normalize_complex(text: str) -> str:
    text = text.replace("I", "i").replace("J", "j")
    if "i" in text and "j" not in text:
        text = text.replace("i", "j")
    return text


def parse_number(text: str) -> ParsedNumber:
    """Parse a real or complex number from user input."""
    raw = text.strip()
    if not raw:
        raise InputError("empty")
    if _COMPLEX_RE.search(raw):
        normalized = _normalize_complex(raw)
        try:
            value = complex(normalized)
        except ValueError as exc:
            raise InputError("invalid_complex") from exc
        return ParsedNumber(value=value, is_complex=True)
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise InputError("invalid_real") from exc
    return ParsedNumber(value=value, is_complex=False)


def parse_degree(text: str) -> int:
    """Parse n-th root degree."""
    raw = text.strip()
    if not raw:
        raise InputError("degree_empty")
    try:
        value = int(raw)
    except ValueError as exc:
        raise InputError("degree_invalid") from exc
    if value < 2:
        raise InputError("degree_range")
    return value


def parse_precision(text: str, min_value: int = 0, max_value: int = 50) -> int:
    """Parse precision setting (digits after decimal)."""
    raw = text.strip()
    if not raw:
        raise InputError("precision_empty")
    try:
        value = int(raw)
    except ValueError as exc:
        raise InputError("precision_invalid") from exc
    if value < min_value or value > max_value:
        raise InputError("precision_range")
    return value
