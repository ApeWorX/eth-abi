import pytest
from eth_utils import (
    to_canonical_address,
    to_normalized_address,
)
from hypothesis import (
    given,
)
from hypothesis import (
    strategies as st,
)

from eth_abi.decoding import (
    AddressDecoder,
)
from eth_abi.encoding import (
    AddressEncoder,
    PackedAddressEncoder,
)


def outcome(function, value):
    try:
        result = function(value)
    except Exception as exc:
        return type(exc), str(exc)
    return type(result), result


@pytest.mark.parametrize(
    "value",
    [
        b"\xab" * 20,
        bytearray(b"\xab" * 20),
        memoryview(b"\xab" * 20),
        "ab" * 20,
        "0x" + "aB" * 20,
        "0X" + "Ab" * 20,
        "00" * 19 + "  ",
        "0x" + "00" * 19 + "\t\n",
        "0x" + "00" * 19 + "\u00a0\u00a0",
        "0x" + "00" * 19 + "gg",
        "00" * 19 + "\u0130\u0130",
        "0x" + "00" * 21,
        "",
        b"",
        b"\x00" * 19,
        b"\x00" * 21,
        0,
        2**159,
        None,
        True,
        [],
    ],
)
def test_address_conversion_preserves_general_inputs(value):
    assert outcome(AddressEncoder.encode_fn, value) == outcome(
        to_canonical_address, value
    )
    assert outcome(PackedAddressEncoder.encode_fn, value) == outcome(
        to_canonical_address, value
    )
    assert outcome(AddressDecoder.decoder_fn, value) == outcome(
        to_normalized_address, value
    )


@given(st.binary(min_size=20, max_size=20))
def test_address_conversion_matches_normalization(value):
    for address in (value, value.hex(), "0x" + value.hex().upper()):
        assert outcome(AddressEncoder.encode_fn, address) == outcome(
            to_canonical_address, address
        )
        assert outcome(AddressDecoder.decoder_fn, address) == outcome(
            to_normalized_address, address
        )


def test_address_conversion_preserves_subclass_methods():
    class CustomBytes(bytes):
        def hex(self):
            raise AssertionError("custom hex must not be called")

    class CustomString(str):
        def __getitem__(self, item):
            raise ValueError("custom slice")

    for value in (CustomBytes(b"\xab" * 20), CustomString("0x" + "ab" * 20)):
        assert outcome(AddressEncoder.encode_fn, value) == outcome(
            to_canonical_address, value
        )
        assert outcome(AddressDecoder.decoder_fn, value) == outcome(
            to_normalized_address, value
        )
