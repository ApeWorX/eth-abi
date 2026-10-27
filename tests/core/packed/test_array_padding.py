from decimal import Decimal

import pytest

from eth_abi.codec import ABIEncoder
from eth_abi.encoding import UnsignedIntegerEncoder
from eth_abi.exceptions import ValueOutOfBounds
from eth_abi.packed import encode_packed
from eth_abi.registry import registry_packed


@pytest.mark.parametrize("suffix", ["[]", "[2]"])
@pytest.mark.parametrize(
    "abi_type,values,expected",
    [
        ("uint8", [1, 255], (1).to_bytes(32, "big") + (255).to_bytes(32, "big")),
        ("int8", [-1, -128], b"\xff" * 32 + b"\xff" * 31 + b"\x80"),
        ("bool", [True, False], b"\x00" * 31 + b"\x01" + b"\x00" * 32),
        (
            "address",
            ["0x" + "12" * 20, "0x" + "34" * 20],
            b"\x00" * 12 + b"\x12" * 20 + b"\x00" * 12 + b"\x34" * 20,
        ),
        ("bytes2", [b"ab", b"c"], b"ab" + b"\x00" * 30 + b"c" + b"\x00" * 31),
        (
            "fixed16x1",
            [Decimal("-1.2"), Decimal("1.2")],
            (-12).to_bytes(32, "big", signed=True) + (12).to_bytes(32, "big"),
        ),
        (
            "ufixed16x1",
            [Decimal("0"), Decimal("1.2")],
            b"\x00" * 32 + (12).to_bytes(32, "big"),
        ),
    ],
)
def test_packed_array_elements_are_words(abi_type, values, expected, suffix):
    assert encode_packed([abi_type + suffix], [values]) == expected


def test_packed_array_does_not_mutate_cached_scalar_encoder():
    registry = registry_packed.copy()
    codec = ABIEncoder(registry)
    scalar = registry.get_encoder("int8")
    assert codec.encode(["int8"], [-1]) == b"\xff"
    assert codec.encode(["int8[]", "int8"], [[-1], -1]) == b"\xff" * 33
    assert registry.get_encoder("int8") is scalar
    assert scalar.data_byte_size == 1
    assert codec.encode(["int8"], [-1]) == b"\xff"


def test_packed_array_preserves_custom_encoder():
    registry = registry_packed.copy()
    registry.unregister_encoder("uint")

    def encode(value):
        return bytes([value + 1])

    encode.validate_value = lambda value: None
    registry.register_encoder("uint8", encode)
    assert ABIEncoder(registry).encode(["uint8[]"], [[1, 2]]) == b"\x02\x03"


@pytest.mark.parametrize("abi_type", ["uint8", "int8", "bytes2", "bool", "address"])
def test_empty_packed_array(abi_type):
    assert encode_packed([abi_type + "[]"], [[]]) == b""


@pytest.mark.parametrize(
    "abi_type,value", [("uint8", 256), ("int8", 128), ("bytes2", b"abc")]
)
def test_packed_array_keeps_scalar_validation(abi_type, value):
    with pytest.raises(ValueOutOfBounds):
        encode_packed([abi_type + "[]"], [[value]])


def test_packed_array_keeps_fixed_length_validation():
    with pytest.raises(ValueOutOfBounds):
        encode_packed(["uint8[2]"], [[1]])


@pytest.mark.parametrize("array_type", ["uint8[]", "uint8[2]"])
def test_array_first_lookup_does_not_widen_later_scalar(array_type):
    codec = ABIEncoder(registry_packed.copy())
    expected = (1).to_bytes(32, "big") + (2).to_bytes(32, "big")
    assert codec.encode([array_type], [[1, 2]]) == expected
    assert codec.encode(["uint8"], [3]) == b"\x03"


@pytest.mark.parametrize(
    "abi_type,value,expected",
    [
        ("uint8[][]", [[1], [2]], (1).to_bytes(32, "big") + (2).to_bytes(32, "big")),
        ("(int8[],uint8)", ([-1], 3), b"\xff" * 32 + b"\x03"),
        ("bytes[]", [b"ab", b"c"], b"abc"),
        ("string[]", ["a", "bc"], b"abc"),
    ],
)
def test_existing_packed_extensions_keep_their_structure(abi_type, value, expected):
    # Nested arrays/tuples are library extensions, not Solidity encodePacked inputs.
    # Dynamic byte/string array padding is deliberately outside this correction.
    assert encode_packed([abi_type], [value]) == expected


def test_packed_array_preserves_wider_custom_encoder():
    registry = registry_packed.copy()
    scalar = UnsignedIntegerEncoder(value_bit_size=512, data_byte_size=64)
    registry.register_encoder("wide", scalar)
    codec = ABIEncoder(registry)
    expected = (1).to_bytes(64, "big")
    assert codec.encode(["wide"], [1]) == expected
    assert codec.encode(["wide[]"], [[1]]) == expected
    array = registry.get_encoder("wide[]")
    array.item_encoder.validate()
    assert array.item_encoder is scalar
    assert scalar.data_byte_size == 64
