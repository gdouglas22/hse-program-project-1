from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import cmath
import math
from typing import Iterable, List, Union

from .parse import ParsedNumber

RootValue = Union[Decimal, complex, float]


def principal_root(parsed: ParsedNumber, degree: int) -> RootValue:
    if parsed.is_complex:
        return _principal_root_complex(parsed.value, degree)
    return _principal_root_real(parsed.value, degree)


def all_roots(parsed: ParsedNumber, degree: int) -> List[complex]:
    if parsed.is_complex:
        z = parsed.value
    else:
        z = complex(float(parsed.value), 0.0)
    return _nth_roots_complex(z, degree)


def format_root(value: RootValue, precision: int) -> str:
    if isinstance(value, Decimal):
        return _format_decimal(value, precision)
    if isinstance(value, complex):
        return _format_complex(value, precision)
    return _format_float(float(value), precision)


def format_polar(value: complex, precision: int) -> str:
    r, theta = cmath.polar(value)
    r_s = _format_float(r, precision)
    t_s = _format_float(theta, precision)
    return f"r={r_s}, theta={t_s} rad"


def _principal_root_real(value: Decimal, degree: int) -> RootValue:
    if degree == 2 and value >= 0:
        return value.sqrt()
    if value < 0 and degree % 2 == 0:
        z = complex(float(value), 0.0)
        return _principal_root_complex(z, degree)
    return _real_nth_root_float(float(value), degree)


def _principal_root_complex(value: complex, degree: int) -> complex:
    if value == 0:
        return 0j
    return cmath.exp(cmath.log(value) / degree)


def _nth_roots_complex(value: complex, degree: int) -> List[complex]:
    if value == 0:
        return [0j for _ in range(degree)]
    r, theta = cmath.polar(value)
    root_r = r ** (1.0 / degree)
    roots = []
    for k in range(degree):
        angle = (theta + 2 * math.pi * k) / degree
        roots.append(cmath.rect(root_r, angle))
    return roots


def _real_nth_root_float(value: float, degree: int) -> float:
    if value >= 0:
        return value ** (1.0 / degree)
    if degree % 2 == 1:
        return -((-value) ** (1.0 / degree))
    return float("nan")


def _format_decimal(value: Decimal, precision: int) -> str:
    quant = Decimal(1).scaleb(-precision)
    rounded = value.quantize(quant, rounding=ROUND_HALF_UP)
    return format(rounded, f".{precision}f")


def _format_float(value: float, precision: int) -> str:
    if _is_negative_zero(value, precision):
        value = 0.0
    return format(value, f".{precision}f")


def _format_complex(value: complex, precision: int) -> str:
    real = value.real
    imag = value.imag
    real_s = _format_float(real, precision)
    imag_s = _format_float(abs(imag), precision)
    sign = "+" if imag >= 0 else "-"
    return f"{real_s} {sign} {imag_s}i"


def _is_negative_zero(value: float, precision: int) -> bool:
    if value != 0.0:
        return False
    threshold = 0.5 * (10 ** -precision) if precision > 0 else 0.5
    return abs(value) < threshold
