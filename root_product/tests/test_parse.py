import pytest

from core.parse import parse_degree, parse_number, parse_precision
from core.errors import InputError


def test_parse_real_decimal():
    parsed = parse_number("123.45")
    assert not parsed.is_complex
    assert str(parsed.value) == "123.45"


@pytest.mark.parametrize("text, real, imag", [("3+4j", 3.0, 4.0), ("3+4i", 3.0, 4.0), ("-2j", 0.0, -2.0)])
def test_parse_complex(text, real, imag):
    parsed = parse_number(text)
    assert parsed.is_complex
    assert parsed.value.real == pytest.approx(real)
    assert parsed.value.imag == pytest.approx(imag)


def test_parse_number_empty():
    with pytest.raises(InputError):
        parse_number("  ")


def test_parse_degree_invalid():
    with pytest.raises(InputError):
        parse_degree("1")
    with pytest.raises(InputError):
        parse_degree("x")


def test_parse_precision_range():
    with pytest.raises(InputError):
        parse_precision("-1")
    with pytest.raises(InputError):
        parse_precision("100")
