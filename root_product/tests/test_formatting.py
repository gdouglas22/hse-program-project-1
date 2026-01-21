from decimal import Decimal

from core.roots import format_root


def test_format_decimal_precision():
    value = Decimal("1.23456")
    assert format_root(value, 2) == "1.23"
    assert format_root(value, 4) == "1.2346"


def test_format_complex_i():
    value = 1 - 2j
    assert format_root(value, 1) == "1.0 - 2.0i"
