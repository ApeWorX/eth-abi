from array import (
    array,
)
from collections import (
    UserList,
)

import pytest

from eth_abi import (
    encoding,
)
from eth_abi.exceptions import (
    EncodingTypeError,
    ValueOutOfBounds,
)
from eth_abi.registry import (
    registry,
)


@pytest.mark.parametrize("value", (True, False))
def test_integer_validation_still_rejects_bool(value):
    with pytest.raises(EncodingTypeError):
        registry.get_encoder("uint8").validate_value(value)


def test_integer_validation_calls_custom_type_checker():
    calls = []

    def reject(value):
        calls.append(value)
        return False

    encoder = encoding.UnsignedIntegerEncoder(value_bit_size=8, type_check_fn=reject)

    with pytest.raises(EncodingTypeError):
        encoder.validate_value(1)

    assert calls == [1]


def test_integer_validation_preserves_type_checker_property_reads():
    calls = []

    def accept(value):
        calls.append(("check", value))
        return True

    class CustomEncoder(encoding.UnsignedIntegerEncoder):
        @property
        def type_check_fn(self):
            calls.append("get")
            return accept

    encoder = CustomEncoder(value_bit_size=8)
    calls.clear()
    encoder.validate_value(1)

    assert calls == ["get", "get", ("check", 1)]


def test_integer_validation_releases_temporary_checker_before_bounds():
    class Checker:
        def __init__(self, owner, change):
            self.owner, self.change = owner, change

        def __call__(self, value):
            return True

        def __del__(self):
            if self.change:
                self.owner.value_bit_size = 8

    class CustomEncoder(encoding.UnsignedIntegerEncoder):
        def __init__(self):
            self.reads = 0
            self.armed = False
            super().__init__(value_bit_size=16)

        @property
        def type_check_fn(self):
            self.reads += 1
            return Checker(self, self.armed and self.reads == 2)

    encoder = CustomEncoder()
    encoder.reads = 0
    encoder.armed = True

    with pytest.raises(ValueOutOfBounds, match="Cannot be encoded in 8 bits"):
        encoder.validate_value(256)

    assert encoder.reads == 2
    assert encoder.value_bit_size == 8


def test_integer_validation_releases_temporary_checker_on_error():
    calls = []

    class Checker:
        __call__ = staticmethod(int)

        def __del__(self):
            calls.append("release")

    class CustomEncoder(encoding.UnsignedIntegerEncoder):
        @property
        def type_check_fn(self):
            return Checker()

    encoder = CustomEncoder(value_bit_size=8)
    calls.clear()

    try:
        encoder.validate_value("bad")
    except ValueError:
        # Check while the exception traceback is still alive.
        assert calls == ["release", "release"]
    else:
        pytest.fail("Expected the custom checker to fail")


@pytest.mark.parametrize(
    "value", ([1, 2], (1, 2), UserList([1, 2]), array("I", [1, 2]))
)
@pytest.mark.parametrize("type_str", ("(uint8,uint8)", "uint8[]", "uint8[2]"))
def test_container_validation_preserves_sequence_inputs(value, type_str):
    encoder = registry.get_encoder(type_str)

    assert encoder.validate_value(value) is None
    assert encoder(value) == encoder([1, 2])


def test_tuple_validation_preserves_subclass_iteration():
    calls = []

    class Values(list):
        def __len__(self):
            calls.append("length")
            return super().__len__()

        def __iter__(self):
            calls.append("iterate")
            return super().__iter__()

    registry.get_encoder("(uint8,uint8)").validate_value(Values([1, 2]))

    assert calls == ["length", "iterate"]


def test_container_validation_preserves_replaced_list_checker(monkeypatch):
    calls = []

    def reject(value):
        calls.append(value)
        return False

    monkeypatch.setattr(encoding, "is_list_like", reject)

    with pytest.raises(EncodingTypeError):
        registry.get_encoder("(uint8,uint8)").validate_value([1, 2])

    assert calls == [[1, 2]]
