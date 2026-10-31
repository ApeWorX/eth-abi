import pytest
from hypothesis import (
    given,
    settings,
)

from eth_abi import (
    is_encodable,
)
from eth_abi.codec import (
    ABICodec,
)
from eth_abi.encoding import (
    UnsignedIntegerEncoder,
)
from eth_abi.exceptions import (
    EncodingError,
    MultipleEntriesFound,
)
from eth_abi.registry import (
    registry,
)
from tests.core.common.strategies import (
    single_strs_values,
    tuple_strs_values,
)
from tests.core.common.unit import (
    CORRECT_ENCODINGS,
    NOT_ENCODABLE,
)


@pytest.mark.parametrize(
    "type_str,python_value,_1,_2",
    CORRECT_ENCODINGS,
)
def test_is_encodable_returns_true(type_str, python_value, _1, _2):
    assert is_encodable(type_str, python_value)


@pytest.mark.parametrize(
    "type_str,python_value",
    NOT_ENCODABLE,
)
def test_is_encodable_returns_false(type_str, python_value):
    assert not is_encodable(type_str, python_value)


@settings(deadline=None)
@given(single_strs_values)
def test_is_encodable_returns_true_for_random_valid_values(type_and_value):
    _type, value = type_and_value
    assert is_encodable(_type, value)


def encode_null(value):
    if value is not None:
        raise EncodingError("Unsupported value")

    return b"\x00" * 32


def test_is_encodable_supports_callable_encoders():
    codec = ABICodec(registry.copy())
    codec._registry.register_encoder("null", encode_null)

    assert codec.is_encodable("null", None)
    assert not codec.is_encodable("null", 1)


def test_is_encodable_raises_for_multiple_matching_encoders():
    codec = ABICodec(registry.copy())
    codec._registry.register_encoder(
        lambda type_str: type_str == "uint256",
        UnsignedIntegerEncoder,
        label="uint256-duplicate",
    )

    with pytest.raises(MultipleEntriesFound):
        codec.is_encodable("uint256", 1)


@settings(deadline=None)
@given(tuple_strs_values)
def test_is_encodable_returns_true_for_random_valid_tuple_values(type_and_value):
    _type, value = type_and_value
    assert is_encodable(_type, value)
