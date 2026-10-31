from collections.abc import (
    Iterable,
)
from typing import (
    Any,
    cast,
)

from eth_typing.abi import (
    Decodable,
    TypeStr,
)

from eth_abi.decoding import (
    ContextFramesBytesIO,
)
from eth_abi.exceptions import (
    EncodingError,
    MultipleEntriesFound,
)
from eth_abi.registry import (
    ABIRegistry,
)
from eth_abi.utils.validation import (
    validate_bytes_param,
    validate_list_like_param,
)


class BaseABICoder:
    """
    Base class for porcelain coding APIs.  These are classes which wrap
    instances of :class:`~eth_abi.registry.ABIRegistry` to provide last-mile
    coding functionality.
    """

    def __init__(self, registry: ABIRegistry):
        """
        Constructor.

        :param registry: The registry providing the encoders to be used when
            encoding values.
        """
        self._registry = registry


class ABIEncoder(BaseABICoder):
    """
    Wraps a registry to provide last-mile encoding functionality.
    """

    def encode(self, types: Iterable[TypeStr], args: Iterable[Any]) -> bytes:
        """
        Encodes the python values in ``args`` as a sequence of binary values of
        the ABI types in ``types`` via the head-tail mechanism.

        :param types: A list or tuple of string representations of the ABI types
            that will be used for encoding e.g.  ``('uint256', 'bytes[]',
            '(int,int)')``
        :param args: A list or tuple of python values to be encoded.

        :returns: The head-tail encoded binary representation of the python
            values in ``args`` as values of the ABI types in ``types``.
        """
        # validate encode types and args
        validate_list_like_param(types, "types")
        validate_list_like_param(args, "args")

        encoder = self._registry.get_tuple_encoder(*types)

        return encoder(args)

    def is_encodable(self, typ: TypeStr, arg: Any) -> bool:
        """
        Determines if the python value ``arg`` is encodable as a value of the
        ABI type ``typ``.

        :param typ: A string representation for the ABI type against which the
            python value ``arg`` will be checked e.g. ``'uint256'``,
            ``'bytes[]'``, ``'(int,int)'``, etc.
        :param arg: The python value whose encodability should be checked.

        :returns: ``True`` if ``arg`` is encodable as a value of the ABI type
            ``typ``.  Otherwise, ``False``.
        """
        try:
            encoder = self._registry.get_encoder(typ)
        except MultipleEntriesFound:
            raise
        except Exception:
            return False

        validate = getattr(encoder, "validate_value", encoder)
        try:
            validate(arg)
        except EncodingError:
            return False

        return True

    def is_encodable_type(self, typ: TypeStr) -> bool:
        """
        Returns ``True`` if values for the ABI type ``typ`` can be encoded by
        this codec.

        :param typ: A string representation for the ABI type that will be
            checked for encodability e.g. ``'uint256'``, ``'bytes[]'``,
            ``'(int,int)'``, etc.

        :returns: ``True`` if values for ``typ`` can be encoded by this codec.
            Otherwise, ``False``.
        """
        return self._registry.has_encoder(typ)


class ABIDecoder(BaseABICoder):
    """
    Wraps a registry to provide last-mile decoding functionality.
    """

    stream_class = ContextFramesBytesIO

    def decode(
        self,
        types: Iterable[TypeStr],
        data: Decodable,
        strict: bool = True,
    ) -> tuple[Any, ...]:
        """
        Decodes the binary value ``data`` as a sequence of values of the ABI types
        in ``types`` via the head-tail mechanism into a tuple of equivalent python
        values.

        :param types: A list or tuple of string representations of the ABI types that
            will be used for decoding e.g. ``('uint256', 'bytes[]', '(int,int)')``
        :param data: The binary value to be decoded.
        :param strict: If ``False``, dynamic-type decoders will ignore validations such
            as making sure the data is padded to a multiple of 32 bytes or checking that
            padding bytes are zero / empty. ``False`` is how the Solidity ABI decoder
            currently works. However, ``True`` is the default for the eth-abi library.

        :returns: A tuple of equivalent python values for the ABI values
            represented in ``data``.
        """
        # validate decode types and data
        validate_list_like_param(types, "types")
        validate_bytes_param(data, "data")

        decoder = self._registry.get_tuple_decoder(*types, strict=strict)
        stream = self.stream_class(data)

        return cast(tuple[Any, ...], decoder(stream))


class ABICodec(ABIEncoder, ABIDecoder):
    pass
