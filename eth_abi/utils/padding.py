def zpad(value: bytes, length: int) -> bytes:
    return value.rjust(length, b"\x00")


def zpad32(value: bytes) -> bytes:
    return zpad(value, length=32)


def zpad_right(value: bytes, length: int) -> bytes:
    return value.ljust(length, b"\x00")


def zpad32_right(value: bytes) -> bytes:
    return zpad_right(value, length=32)


def fpad(value: bytes, length: int) -> bytes:
    return value.rjust(length, b"\xff")


def fpad32(value: bytes) -> bytes:
    return fpad(value, length=32)
