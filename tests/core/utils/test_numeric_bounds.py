import decimal

import pytest

from eth_abi.utils.numeric import (
    ZERO,
    compute_signed_fixed_bounds,
    compute_signed_integer_bounds,
    compute_unsigned_fixed_bounds,
    compute_unsigned_integer_bounds,
)


@pytest.mark.parametrize(
    "num_bits,expected",
    (
        (8, (0, 255)),
        (16, (0, 65535)),
        (256, (0, 2**256 - 1)),
    ),
)
def test_compute_unsigned_integer_bounds(num_bits, expected):
    assert compute_unsigned_integer_bounds(num_bits) == expected


@pytest.mark.parametrize(
    "num_bits,expected",
    (
        (8, (-128, 127)),
        (16, (-32768, 32767)),
        (256, (-(2**255), 2**255 - 1)),
    ),
)
def test_compute_signed_integer_bounds(num_bits, expected):
    assert compute_signed_integer_bounds(num_bits) == expected


def test_compute_unsigned_fixed_bounds():
    assert compute_unsigned_fixed_bounds(8, 1) == (ZERO, decimal.Decimal("25.5"))


def test_compute_signed_fixed_bounds():
    assert compute_signed_fixed_bounds(8, 1) == (
        decimal.Decimal("-12.8"),
        decimal.Decimal("12.7"),
    )
