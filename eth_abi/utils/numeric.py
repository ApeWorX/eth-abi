import decimal
from collections.abc import (
    Callable,
)

ABI_DECIMAL_PREC = 999

abi_decimal_context = decimal.Context(prec=ABI_DECIMAL_PREC)

ZERO = decimal.Decimal(0)
TEN = decimal.Decimal(10)


def ceil32(x: int) -> int:
    return x if x % 32 == 0 else x + 32 - (x % 32)


_unsigned_integer_bounds_cache: dict[int, tuple[int, int]] = {}


def compute_unsigned_integer_bounds(num_bits: int) -> tuple[int, int]:
    bounds = _unsigned_integer_bounds_cache.get(num_bits)
    if bounds is None:
        bounds = 0, 2**num_bits - 1
        _unsigned_integer_bounds_cache[num_bits] = bounds

    return bounds


_signed_integer_bounds_cache: dict[int, tuple[int, int]] = {}


def compute_signed_integer_bounds(num_bits: int) -> tuple[int, int]:
    bounds = _signed_integer_bounds_cache.get(num_bits)
    if bounds is None:
        overflow_at = 2 ** (num_bits - 1)
        bounds = -overflow_at, overflow_at - 1
        _signed_integer_bounds_cache[num_bits] = bounds

    return bounds


_unsigned_fixed_bounds_cache: dict[tuple[int, int], decimal.Decimal] = {}


def compute_unsigned_fixed_bounds(
    num_bits: int,
    frac_places: int,
) -> tuple[decimal.Decimal, decimal.Decimal]:
    cache_key = (num_bits, frac_places)
    upper = _unsigned_fixed_bounds_cache.get(cache_key)
    if upper is None:
        int_upper = 2**num_bits - 1

        with decimal.localcontext(abi_decimal_context):
            upper = decimal.Decimal(int_upper) * TEN**-frac_places

        _unsigned_fixed_bounds_cache[cache_key] = upper

    return ZERO, upper


_signed_fixed_bounds_cache: dict[
    tuple[int, int], tuple[decimal.Decimal, decimal.Decimal]
] = {}


def compute_signed_fixed_bounds(
    num_bits: int,
    frac_places: int,
) -> tuple[decimal.Decimal, decimal.Decimal]:
    cache_key = (num_bits, frac_places)
    bounds = _signed_fixed_bounds_cache.get(cache_key)
    if bounds is None:
        int_lower, int_upper = compute_signed_integer_bounds(num_bits)

        with decimal.localcontext(abi_decimal_context):
            exp = TEN**-frac_places
            lower = decimal.Decimal(int_lower) * exp
            upper = decimal.Decimal(int_upper) * exp

        bounds = lower, upper
        _signed_fixed_bounds_cache[cache_key] = bounds

    return bounds


def scale_places(places: int) -> Callable[[decimal.Decimal], decimal.Decimal]:
    """
    Returns a function that shifts the decimal point of decimal values to the
    right by ``places`` places.
    """
    if not isinstance(places, int):
        raise ValueError(
            f"Argument `places` must be int.  Got value {places} "
            f"of type {type(places)}.",
        )

    with decimal.localcontext(abi_decimal_context):
        scaling_factor = TEN**-places

    def f(x: decimal.Decimal) -> decimal.Decimal:
        with decimal.localcontext(abi_decimal_context):
            return x * scaling_factor

    places_repr = f"Eneg{places}" if places > 0 else f"Epos{-places}"
    func_name = f"scale_by_{places_repr}"

    f.__name__ = func_name
    f.__qualname__ = func_name

    return f
