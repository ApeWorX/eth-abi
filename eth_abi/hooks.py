"""
Hook resolver for ABI encoding offset discovery.

Provides :func:`resolve_hooks` and :class:`EncodingContext` for callers
who need to discover the exact byte offsets of argument slots in
ABI-encoded output without modifying the core encoder.
"""

from collections.abc import Iterable, Sequence
from typing import Any, NamedTuple

from eth_utils import (
    is_list_like,
)

from .encoding import (
    BaseEncoder,
    BaseArrayEncoder,
    DynamicArrayEncoder,
    TupleEncoder,
)


class EncodingContext(NamedTuple):
    """
    Context information provided to callable hook values in resolve_hooks.

    :param offset: The byte offset in the encoded output where this value's
        data begins.  For static types, this is the position of the value in
        the head section.  For dynamic types, this is the position of the data
        (length prefix included) in the tail section.
    :param size: The encoded byte size of the value at this position.
        It's None for dynamic types.
    """

    offset: int
    size: int | None
    encoder: Any


def resolve_hooks(encoder: BaseEncoder, value: Any) -> Any:
    """
    Resolve callable hooks within ``value``, returning a new value
    with each hook replaced by its placeholder value.

    A hook is any callable placed where a value is expected.  Before
    encoding, the hook is called with an :class:`EncodingContext` object
    that reports the absolute byte offset at which the value's encoded data
    will appear in the final output, the encoded byte size for that
    position, and the encoder instance responsible for encoding it.

    Hooks may be placed at primitive leaf positions at any depth of nesting:
    directly in ``value``, inside tuple values, inside array values, or any
    combination thereof.

    :param encoder: The :class:`~eth_abi.encoding.BaseEncoder` to use for
        the value.
    :param value: A python value, possibly containing callable
        hooks.

    :returns: A new value with all hooks replaced by their placeholders.
        The resolved value can be passed directly to encode.
    """
    return _resolve_value(
        value, encoder, 0
    )


def encode_with_hooks(encoder: BaseEncoder, value: Any) -> bytes:
    value = resolve_hooks(encoder, value)
    return encoder(value)


def _get_head_size(encoder: BaseEncoder) -> int:
    """
    Returns the number of bytes that ``encoder`` contributes to the head
    section of a standard ABI-encoded tuple.

    Dynamic encoders contribute a 32-byte offset pointer.  Static primitive
    encoders contribute exactly 32 bytes.  Static composite encoders
    (tuples, fixed-size arrays) contribute the combined head size of their
    elements.
    """
    if getattr(encoder, "is_dynamic", False):
        return 32

    if isinstance(encoder, TupleEncoder):
        return sum(_get_head_size(e) for e in encoder.encoders)

    if (
        hasattr(encoder, "array_size")
        and hasattr(encoder, "item_encoder")
        and encoder.array_size is not None
    ):
        assert isinstance(encoder.array_size, int)
        return encoder.array_size * _get_head_size(encoder.item_encoder)

    # All other primitive static types (uint, int, address, bool, bytesN, …)
    return 32


def _resolve_value(value: Any, encoder: BaseEncoder, base_offset: int) -> Any:
    """
    Resolve a single (value, encoder) tuple at the given offset.

    * Callables are invoked with an :class:`EncodingContext` and replaced by
      their return value.
    * Tuples are recursed into via :func:`_resolve_tuple`.
    * Arrays are recursed into via :func:`_resolve_array`.
    * All other values are returned unchanged.
    """
    if isinstance(encoder, TupleEncoder) and is_list_like(value):
        return _resolve_tuple(value, encoder.encoders, base_offset)
    if isinstance(encoder, BaseArrayEncoder) and is_list_like(value):
        return _resolve_array(value, encoder, base_offset)
    if callable(value):
        # For fixed-size encoders (static primitives) data_byte_size is the
        # exact encoded byte width: 32 for standard-ABI types, 1/4/20/…  for
        # packed types.  Dynamic encoders have no data_byte_size, so we pass
        # None and fill it in after the hook returns (see below).
        size: int | None = getattr(encoder, "data_byte_size", None)
        ctx = EncodingContext(
            offset=base_offset,
            size=size,
            encoder=encoder,
        )
        return value(ctx)
    return value


def _resolve_tuple(
    values: Iterable[Any],
    encoders: Sequence[BaseEncoder],
    base_offset: int,
) -> list[Any]:
    """
    Resolve hooks in a flat sequence of ``(value, encoder)`` tuples.

    Handles both standard ABI layout (static head + dynamic tail) and packed
    layout (all items sequential, no 32-byte padding for static items).

    ``base_offset`` is the absolute byte position where this sequence's
    encoding starts in the final output.
    """
    # Analytic head total — used only to compute absolute offsets for dynamic
    # items whose data lives in the tail section.
    head_total = sum(_get_head_size(e) for e in encoders)

    current_head_pos = 0
    current_tail_size = 0
    resolved: list[Any] = list(values)  # shallow copy

    for i, (value, encoder) in enumerate(zip(resolved, encoders)):
        is_dynamic = getattr(encoder, "is_dynamic", False)

        if is_dynamic:
            item_base = base_offset + head_total + current_tail_size
        else:
            item_base = base_offset + current_head_pos

        resolved_value = _resolve_value(value, encoder, item_base)
        resolved[i] = resolved_value

        # Advance position counters using the actual encoded byte length so
        # that packed encoders (uint8 → 1 byte, address → 20 bytes, etc.) are
        # tracked correctly alongside standard 32-byte-slot ABI encoders.
        encoded: bytes = encoder(resolved_value)
        if is_dynamic:
            current_tail_size += len(encoded)
            current_head_pos += 32  # head slot is always 32 bytes (offset pointer)
        else:
            current_head_pos += len(encoded)

    return resolved


def _resolve_array(
    values: Sequence[Any],
    encoder: BaseArrayEncoder,
    base_offset: int,
) -> list[Any]:
    """
    Recurse into an array value.

    ``base_offset`` is the absolute byte position where this array's encoding
    starts (including the 32-byte count prefix for
    :class:`~eth_abi.encoding.DynamicArrayEncoder`).

    ABI layout for arrays with dynamic items::

        [count?][ptr0][ptr1]...[data0][data1]...

    ABI layout for arrays with static items (or packed arrays)::

        [count?][item0][item1]...

    The count slot is only present for
    :class:`~eth_abi.encoding.DynamicArrayEncoder`.
    """
    item_enc: BaseEncoder = encoder.item_encoder
    items_dynamic: bool = getattr(item_enc, "is_dynamic", False)

    # DynamicArrayEncoder prepends a 32-byte element count; others do not.
    if isinstance(encoder, DynamicArrayEncoder):
        elements_base = base_offset + 32
    else:
        elements_base = base_offset

    resolved: list[Any] = list(values)  # shallow copy

    if items_dynamic:
        # Head section: one 32-byte offset pointer per element.
        head_total = 32 * len(resolved)
        current_tail_size = 0
        for i, item in enumerate(resolved):
            item_base = elements_base + head_total + current_tail_size
            resolved_item = _resolve_value(item, item_enc, item_base)
            resolved[i] = resolved_item
            current_tail_size += len(item_enc(resolved_item))
    else:
        # Static ABI items or packed items: laid out sequentially.
        current_pos = 0
        for i, item in enumerate(resolved):
            item_base = elements_base + current_pos
            resolved_item = _resolve_value(item, item_enc, item_base)
            resolved[i] = resolved_item
            current_pos += len(item_enc(resolved_item))

    return resolved
