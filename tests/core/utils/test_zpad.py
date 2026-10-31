import pytest

from eth_abi.utils.padding import (
    fpad,
    fpad32,
    zpad,
    zpad32,
    zpad32_right,
    zpad_right,
)


@pytest.mark.parametrize(
    "value,length,expected",
    (
        (b"", 5, b"\x00\x00\x00\x00\x00"),
        (b"abc", 5, b"\x00\x00abc"),
        (b"abcde", 5, b"abcde"),
        (b"abcdef", 5, b"abcdef"),
    ),
)
def test_zpadding(value, length, expected):
    actual = zpad(value, length)
    assert actual == expected


@pytest.mark.parametrize(
    "func,value,length,expected",
    (
        (zpad_right, b"abc", 5, b"abc\x00\x00"),
        (fpad, b"abc", 5, b"\xff\xffabc"),
    ),
)
def test_padding_helpers(func, value, length, expected):
    actual = func(value, length)
    assert actual == expected


@pytest.mark.parametrize(
    "func,value,expected",
    (
        (zpad32, b"abc", (b"\x00" * 29) + b"abc"),
        (zpad32_right, b"abc", b"abc" + (b"\x00" * 29)),
        (fpad32, b"abc", (b"\xff" * 29) + b"abc"),
    ),
)
def test_32_byte_padding_helpers(func, value, expected):
    actual = func(value)
    assert actual == expected
