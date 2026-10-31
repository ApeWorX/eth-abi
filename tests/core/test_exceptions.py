import pytest

from eth_abi import (
    decode,
    encode,
)
from eth_abi.exceptions import (
    EncodingError,
    EncodingTypeError,
    IllegalValue,
    ValueOutOfBounds,
)


def test_value_out_of_bounds_is_a_value_error():
    assert issubclass(ValueOutOfBounds, ValueError)
    assert issubclass(IllegalValue, ValueError)


def test_encoding_type_error_is_a_type_error():
    assert issubclass(EncodingTypeError, TypeError)


def test_encoding_errors_still_subclass_encoding_error():
    # The builtin base classes are added without dropping the library one, so
    # existing `except EncodingError` handlers keep working.
    assert issubclass(ValueOutOfBounds, EncodingError)
    assert issubclass(IllegalValue, EncodingError)
    assert issubclass(EncodingTypeError, EncodingError)


def test_out_of_range_int_is_caught_as_value_error():
    with pytest.raises(ValueError) as exc_info:
        encode(["uint8"], [300])
    assert isinstance(exc_info.value, ValueOutOfBounds)


def test_wrong_python_type_is_caught_as_type_error():
    with pytest.raises(TypeError) as exc_info:
        encode(["uint8"], ["not an int"])
    assert isinstance(exc_info.value, EncodingTypeError)


def test_decoding_still_round_trips():
    assert decode(["uint8"], encode(["uint8"], [255])) == (255,)
