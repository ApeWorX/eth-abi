import pytest

from eth_abi import (
    encode,
)
from eth_abi.encoding import (
    TupleEncoder,
)


@pytest.mark.parametrize("chunk_type", (bytes, bytearray))
def test_static_tuple_preserves_custom_encoder_calls(chunk_type):
    calls = []

    def encoder(value):
        calls.append(value)
        return chunk_type([value])

    result = TupleEncoder(encoders=(encoder, encoder))((1, 2))

    assert type(result) is bytes
    assert result == b"\x01\x02"
    assert calls == [1, 2, 1, 2]


def test_static_tuple_preserves_custom_chunk_length_checks():
    class CustomBytes(bytes):
        def __len__(self):
            raise ValueError("custom length")

    encoder = TupleEncoder(encoders=(lambda value: CustomBytes(value),))

    with pytest.raises(ValueError, match="^custom length$"):
        encoder((b"value",))


def test_static_tuple_validates_all_values_before_encoding():
    calls = []

    class Encoder:
        def validate_value(self, value):
            calls.append(("validate", value))
            if value == 2:
                raise ValueError("second value")

        def __call__(self, value):
            calls.append(("encode", value))
            return bytes([value])

    encoder = TupleEncoder(encoders=(Encoder(), Encoder()))

    with pytest.raises(ValueError, match="^second value$"):
        encoder((1, 2))

    assert calls == [("validate", 1), ("validate", 2)]


def test_static_tuple_nested_and_empty():
    assert encode([], []) == b""
    assert encode(["(uint8,(bool,bytes1))"], [(7, (True, b"a"))]) == (
        b"\x00" * 31 + b"\x07" + b"\x00" * 31 + b"\x01" + b"a" + b"\x00" * 31
    )
