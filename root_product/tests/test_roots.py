import pytest
from decimal import Decimal

from core.parse import parse_number
from core.roots import all_roots, principal_root


def test_principal_sqrt_real_decimal():
    parsed = parse_number("9")
    root = principal_root(parsed, 2)
    assert isinstance(root, Decimal)
    assert root == Decimal("3")


def test_principal_sqrt_negative_complex():
    parsed = parse_number("-9")
    root = principal_root(parsed, 2)
    assert isinstance(root, complex)
    assert root.real == pytest.approx(0.0, abs=1e-9)
    assert root.imag == pytest.approx(3.0, abs=1e-9)


def test_all_roots_count():
    parsed = parse_number("1+0j")
    roots = all_roots(parsed, 3)
    assert len(roots) == 3


def test_large_decimal_sqrt():
    parsed = parse_number("1e100")
    root = principal_root(parsed, 2)
    assert root == Decimal("1E+50")
