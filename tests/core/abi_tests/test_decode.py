import re

import pytest

from eth_abi.abi import (
    decode,
)
from eth_abi.exceptions import (
    InsufficientDataBytes,
    InvalidPointer,
)
from eth_abi.grammar import (
    parse,
)
from tests.core.common.unit import (
    CORRECT_DYNAMIC_ENCODINGS,
    CORRECT_STATIC_ENCODINGS,
    CORRECT_TUPLE_ENCODINGS,
    words,
)


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize(
    "type_str,expected,abi_encoding,_",
    CORRECT_TUPLE_ENCODINGS,
)
def test_abi_decode_for_multiple_types_as_list(
    type_str, expected, abi_encoding, _, strict
):
    abi_type = parse(type_str)
    if abi_type.arrlist is not None:
        pytest.skip("ABI coding functions do not support array types")

    types = [t.to_type_str() for t in abi_type.components]

    actual = decode(types, abi_encoding, strict=strict)
    assert actual == expected


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize(
    "type_str,expected,abi_encoding,_",
    CORRECT_STATIC_ENCODINGS,
)
def test_abi_decode_for_single_static_types(
    type_str, expected, abi_encoding, _, strict
):
    (actual,) = decode([type_str], abi_encoding, strict=strict)
    assert actual == expected


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize(
    "type_str,expected,abi_encoding,_",
    CORRECT_DYNAMIC_ENCODINGS,
)
def test_abi_decode_for_single_dynamic_types(
    type_str, expected, abi_encoding, _, strict
):
    # Tests set up list values but encoders return sequences as tuples.
    # i.e. [b'\xde\xad\xbe\xef'] vs encoder return type (b'\xde\xad\xbe\xef',)
    expected = tuple(expected) if isinstance(expected, list) else expected

    abi_encoding = (
        # 32 bytes offset for dynamic types
        b"".join([words("20"), abi_encoding])
    )

    (actual,) = decode([type_str], abi_encoding, strict=strict)
    assert actual == expected


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize("data", (b"", bytearray()))
def test_abi_decode_empty_data_raises(data, strict):
    with pytest.raises(InsufficientDataBytes):
        decode(["uint"], data, strict=strict)


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize("data", ("", 123, 0x123, [b"\x01"], (b"\x01",), {b"\x01"}))
def test_abi_decode_wrong_data_param_type_raises(data, strict):
    with pytest.raises(
        TypeError, match=f"The `data` value must be of bytes type. Got {type(data)}"
    ):
        decode(["uint32", "uint32"], data, strict=strict)


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize(
    "types",
    (
        "",
        123,
        b"",
        b"\xff",
        b"david attenborough",
        bytearray(b"\x01\xff"),
        {"key": "val"},
        {1, 2},
    ),
)
def test_abi_decode_wrong_types_param_type_raises(types, strict):
    with pytest.raises(
        TypeError,
        match=f"The `types` value type must be one of list or tuple. Got {type(types)}",
    ):
        decode(types, b"\x00" * 32, strict=strict)


@pytest.mark.parametrize("strict", (True, False))
@pytest.mark.parametrize(
    "zero_sized_tuple_type",
    ("()[]", "()", "(int,())", "(int,((),))", "(int,(),int)"),
)
def test_abi_decode_raises_for_zero_sized_tuple_type(zero_sized_tuple_type, strict):
    with pytest.raises(
        ValueError,
        match=re.escape('Zero-sized tuple types "()" are not supported.'),
    ):
        decode(
            [zero_sized_tuple_type],
            b"bytes data shouldn't matter for validation",
            strict=strict,
        )


@pytest.mark.parametrize(
    "types,hex_data,expected",
    (
        (
            ["string"],
            (
                "0000000000000000000000000000000000000000000000000000000000000020"
                "0000000000000000000000000000000000000000000000000000000000000011"
                "6e6f2070616464696e67206e6565646564"
            ),
            ("no padding needed",),
        ),
        (
            ["bytes"],
            (
                # offset to data is 32 bytes:
                "0000000000000000000000000000000000000000000000000000000000000020"
                # length of data is 1 byte:
                "0000000000000000000000000000000000000000000000000000000000000001"
                # b"\x01" with less than 32 bytes of padding:
                "01000000000000000000"
            ),
            (b"\x01",),
        ),
        (
            # example from issue #198
            ["uint256", "uint256", "address", "bytes"],
            (
                # uint256 with value of 891276594009425425420:
                "00000000000000000000000000000000000000000000003050f28c10d7d9b40c"
                # uint256 with value of 0:
                "0000000000000000000000000000000000000000000000000000000000000000"
                # address:
                "000000000000000000000000b5c7ad3cb6506c65da01f2fac2e667dcb9e66e9c"
                # data starts at 128 bytes into the byte array:
                "0000000000000000000000000000000000000000000000000000000000000080"
                # 201 bytes of data (padded would've been 224 bytes):
                "00000000000000000000000000000000000000000000000000000000000000c9"
                "04853d955acef822db058eb8505911ed77f175b99e1531c1a63a169ac75a2daa"
                "e399080745fa51de440000000000000000000000000000000000000000000000"
                "3050f28c10d7d9b40c7bc2c873190bbaddefe646c35f1ae6cffbfb402059bd67"
                "74c22486d9f4fab2d448dce4f892a9ae250d0ab87046fbb341d058f17cbc4c11"
                "33f25a20a52f000db63cac384247597756545b500253ff8e607a8020010b0002"
                "0f0100000e030c01990966d504030200000569b81152c5a8d35a67b32a4d3772"
                "795d96cae4da010106"
            ),
            (
                891276594009425425420,
                0,
                "0xb5c7ad3cb6506c65da01f2fac2e667dcb9e66e9c",
                b'\x04\x85=\x95Z\xce\xf8"\xdb\x05\x8e\xb8PY\x11\xedw\xf1u\xb9\x9e'
                b"\x151\xc1\xa6:\x16\x9a\xc7Z-\xaa\xe3\x99\x08\x07E\xfaQ\xdeD\x00"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x00\x00\x00\x00\x00\x000P\xf2\x8c\x10\xd7\xd9\xb4\x0c{\xc2\xc8s"
                b"\x19\x0b\xba\xdd\xef\xe6F\xc3_\x1a\xe6\xcf\xfb\xfb@ Y\xbdgt\xc2$"
                b"\x86\xd9\xf4\xfa\xb2\xd4H\xdc\xe4\xf8\x92\xa9\xae%\r\n\xb8pF\xfb"
                b"\xb3A\xd0X\xf1|\xbcL\x113\xf2Z \xa5/\x00\r\xb6<\xac8BGYwVT[P\x02S"
                b"\xff\x8e`z\x80 \x01\x0b\x00\x02\x0f\x01\x00\x00\x0e\x03\x0c\x01"
                b"\x99\tf\xd5\x04\x03\x02\x00\x00\x05i\xb8\x11R\xc5\xa8\xd3Zg"
                b"\xb3*M7ry]\x96\xca\xe4\xda\x01\x01\x06",
            ),
        ),
    ),
)
def test_abi_decode_with_shorter_data_than_32_bytes(types, hex_data, expected):
    assert decode(types, bytes.fromhex(hex_data), strict=False) == expected

    # assert flag is transient and does not affect other calls to ``decode()``
    # without the flag set (i.e. assert the default behavior is always ``strict=True``).
    with pytest.raises(InsufficientDataBytes):
        decode(types, bytes.fromhex(hex_data))


@pytest.mark.parametrize(
    "typestring,malformed_payload",
    (
        (
            ["uint256[][][][][][][][][][]"],
            ("0" * 62 + "20") * 10 + "00" * 2056,
        ),
        (
            ["uint256[][][][][][][][][][][][]"],
            "0" * 62 + "20" + "0" * 62 + "a0" + ("0" * 62 + "20") * 9 + "00" * 1024,
        ),
        (
            ["uint8[]", "uint[2]", "uint8[]"],
            "00000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
        ),
        (
            ["(uint8[2],uint8[])"],
            "00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
        ),
        (
            ["(uint8[2],uint8[])"],
            "00000000000000000000000000000000000000000000000000000000000000f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
        ),
        (
            ["uint8[]"],
            "00000000000000000000000000000000000000000000000000000000000000f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
        ),
        (
            ["(uint8[],uint8[8],uint8[])"],
            "0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
        ),
        (
            ["((uint256,uint256,uint256),string)"],
            "00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040",  # noqa: E501
        ),
        (
            ["(uint256[2][2],string)"],
            "000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000060",  # noqa: E501
        ),
    ),
    ids=(
        "nested array with all pointers equal to 0x20",
        "nested array user example",
        "separate dynamic, sized, dynamic arrays",
        "tuple of sized array and dynamic array",
        "pointer beyond end of data for tuple",
        "pointer beyond end of data for array",
        "tuple of arrays to check length of head section of tuple calcd correctly",
        "pointer into head section after a static tuple",
        "pointer into head section after a nested sized array",
    ),
)
@pytest.mark.timeout(1)
def test_decode_nested_dynamic_array_with_invalid_pointer_fails_fast(
    typestring, malformed_payload
):
    malformed_payload_bytes = bytearray.fromhex(malformed_payload)
    with pytest.raises(InvalidPointer, match=r"^Invalid pointer in"):
        decode(typestring, malformed_payload_bytes)
