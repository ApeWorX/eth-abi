import pytest

from eth_abi import (
    encode,
)
from eth_abi.exceptions import (
    EncodingError,
    EncodingTypeError,
    IllegalValue,
    ValueOutOfBounds,
)


@pytest.mark.parametrize(
    "types,args,expected_exc,builtin_exc",
    (
        (["address"], ["0x123"], EncodingTypeError, TypeError),
        (["uint256"], ["abc"], EncodingTypeError, TypeError),
        (["uint8"], [300], ValueOutOfBounds, ValueError),
        (["bytes32"], [b"x" * 40], ValueOutOfBounds, ValueError),
    ),
)
def test_encoding_errors_are_builtin_exceptions(types, args, expected_exc, builtin_exc):
    with pytest.raises(expected_exc) as excinfo:
        encode(types, args)

    assert isinstance(excinfo.value, EncodingError)
    assert isinstance(excinfo.value, builtin_exc)


def test_encoding_error_hierarchy():
    assert issubclass(EncodingTypeError, TypeError)
    assert issubclass(IllegalValue, ValueError)
    assert issubclass(ValueOutOfBounds, ValueError)
