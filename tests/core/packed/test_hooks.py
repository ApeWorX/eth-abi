from eth_abi.packed import (
    encode_packed,
    encode_packed_with_hooks,
)
from eth_abi.hooks import (
    EncodingContext,
)
from eth_abi.registry import (
    registry_packed,
)

# ---------------------------------------------------------------------------
# Tests for callable hook support in packed encoding
# ---------------------------------------------------------------------------


def test_packed_hook_fixed_size_uint8_offset():
    """Hook for uint8 in packed encoding receives the correct byte offset."""
    contexts = []

    def hook(ctx):
        contexts.append(ctx)
        return 0

    # uint8 = 1 byte each → hook is at offset 2
    resolved = encode_packed_with_hooks(["uint8", "uint8", "uint8"], [1, 2, hook])
    assert contexts[0] == EncodingContext(offset=2, size=1, encoder=registry_packed.get_encoder("uint8"))


def test_packed_hook_address_offset():
    """Hook for address (20 bytes) in packed encoding gets the correct offset."""
    contexts = []

    def hook(ctx):
        contexts.append(ctx)
        return "0x" + "ab" * 20

    # uint8=1 byte → hook is at offset 1
    resolved = encode_packed_with_hooks(["uint8", "address"], [1, hook])
    assert contexts[0] == EncodingContext(offset=1, size=20, encoder=registry_packed.get_encoder("address"))


def test_packed_hook_variable_bytes_before_hook():
    """Hook after a packed bytes (variable size) gets the offset after the bytes data."""
    contexts = []

    def hook(ctx):
        contexts.append(ctx)
        return 0

    # b'hello' = 5 bytes, uint8 = 1 byte → hook at offset 6
    resolved = encode_packed_with_hooks(["bytes", "uint8", "uint8"], [b"hello", 2, hook])
    assert contexts[0] == EncodingContext(offset=6, size=1, encoder=registry_packed.get_encoder("uint8"))


def test_packed_hook_result_matches_explicit_value():
    """Packed encoding with hook returning a value matches direct encoding."""
    result_explicit = encode_packed(["uint8", "uint8", "uint8"], [1, 99, 3])
    result_hook = encode_packed_with_hooks(["uint8", "uint8", "uint8"], [1, lambda ctx: 99, 3])
    assert result_explicit == result_hook


def test_packed_hook_multiple_hooks():
    """Multiple hooks in packed encoding each receive the correct sequential offset."""
    contexts = []

    def make_hook(retval):
        def hook(ctx):
            contexts.append(ctx)
            return retval

        return hook

    resolved = encode_packed_with_hooks(
        ["uint8", "uint8", "uint8"],
        [make_hook(1), make_hook(2), make_hook(3)],
    )
    assert contexts == [
        EncodingContext(offset=0, size=1, encoder=registry_packed.get_encoder("uint8")),
        EncodingContext(offset=1, size=1, encoder=registry_packed.get_encoder("uint8")),
        EncodingContext(offset=2, size=1, encoder=registry_packed.get_encoder("uint8")),
    ]


def test_packed_hook_uint256_offset():
    """Hook for uint256 (32 bytes) gets correct offset in packed mode."""
    contexts = []

    def hook(ctx):
        contexts.append(ctx)
        return 42

    # uint8=1 byte, uint256=32 bytes → hook at offset 1
    resolved = encode_packed_with_hooks(["uint8", "uint256"], [1, hook])
    assert contexts[0] == EncodingContext(offset=1, size=32, encoder=registry_packed.get_encoder("uint256"))


# ---------------------------------------------------------------------------
# Comprehensive round-trip tests for callable hook offset detection (packed)
#
# Pattern:
#   data1 = encode_packed(types, args)
#   tmpl  = encode_packed(types, args_with_hooks)   # zero placeholders
#   data2 = patch(tmpl, contexts, data1)
#   assert data1 == data2
#
# For packed types, ctx.offset is the first byte of the type's packed
# representation.  The patch slice length equals the actual packed byte size
# of the real value.
# ---------------------------------------------------------------------------


def _make_hook_p(ctx_list, placeholder):
    """Hook for packed encoding: records ctx, returns *placeholder*."""

    def hook(ctx):
        ctx_list.append(ctx)
        return placeholder

    return hook


def _patch_packed(tmpl, offset, real_slice):
    """Return a copy of *tmpl* with *len(real_slice)* bytes replaced at *offset*."""
    n = len(real_slice)
    return tmpl[:offset] + real_slice + tmpl[offset + n :]


def _apply_fixed_patches(tmpl, contexts, data1):
    """Patch every context's slot in *tmpl* with the same-width bytes from *data1*.

    Works for fixed-size packed types where the encoder exposes
    ``data_byte_size``.
    """
    result = tmpl
    for ctx in contexts:
        size = ctx.encoder.data_byte_size
        result = _patch_packed(result, ctx.offset, data1[ctx.offset : ctx.offset + size])
    return result


def test_packed_round_trip_all_fixed_size():
    """Round-trip uint8/uint16/uint32 through hooks then patch back."""
    types = ["uint8", "uint16", "uint32"]
    args = [1, 2, 3]
    data1 = encode_packed(types, args)

    contexts = []
    tmpl = encode_packed_with_hooks(types, [_make_hook_p(contexts, 0) for _ in args])

    assert _apply_fixed_patches(tmpl, contexts, data1) == data1


def test_packed_round_trip_uint256_and_address():
    """Round-trip uint256 (32 bytes) and address (20 bytes) in packed mode."""
    types = ["uint256", "address", "uint8"]
    args = [0xDEAD, "0x" + "ab" * 20, 7]
    data1 = encode_packed(types, args)

    contexts = []
    tmpl = encode_packed_with_hooks(
        types,
        [
            _make_hook_p(contexts, 0),
            _make_hook_p(contexts, "0x" + "00" * 20),
            _make_hook_p(contexts, 0),
        ],
    )

    assert _apply_fixed_patches(tmpl, contexts, data1) == data1


def test_packed_round_trip_bool_and_bytes32():
    """Round-trip bool (1 byte) and bytes32 (32 bytes) in packed mode."""
    types = ["bool", "bytes32", "uint8"]
    args = [True, b"\xca\xfe" + b"\x00" * 30, 42]
    data1 = encode_packed(types, args)

    contexts = []
    tmpl = encode_packed_with_hooks(
        types,
        [
            _make_hook_p(contexts, False),
            _make_hook_p(contexts, b"\x00" * 32),
            _make_hook_p(contexts, 0),
        ],
    )

    assert _apply_fixed_patches(tmpl, contexts, data1) == data1


def test_packed_round_trip_variable_bytes_before_hook():
    """Variable-length packed bytes shifts subsequent offsets; verify round-trip."""
    real_bytes = b"hello"
    types = ["bytes", "uint8", "uint16"]
    args = [real_bytes, 10, 20]
    data1 = encode_packed(types, args)

    contexts = []
    # Placeholder has the same byte length so tmpl has the same total size as
    # data1, keeping all subsequent offsets valid.
    tmpl = encode_packed_with_hooks(
        types,
        [
            _make_hook_p(contexts, b"\x00" * len(real_bytes)),
            _make_hook_p(contexts, 0),
            _make_hook_p(contexts, 0),
        ],
    )

    # For variable-length types the byte size is the gap to the next offset
    # (or to the end of data for the last element).
    offsets = [ctx.offset for ctx in contexts]
    ends = offsets[1:] + [len(data1)]
    sizes = [end - start for start, end in zip(offsets, ends)]

    result = tmpl
    for ctx, size in zip(contexts, sizes):
        result = _patch_packed(result, ctx.offset, data1[ctx.offset : ctx.offset + size])
    assert result == data1


def test_packed_round_trip_hooks_at_subset_of_positions():
    """Only some positions use hooks in packed mode; non-hooked stay intact."""
    types = ["uint8", "uint8", "uint8"]
    args = [10, 20, 30]
    data1 = encode_packed(types, args)

    # Only hook positions 0 and 2
    contexts = []
    tmpl = encode_packed_with_hooks(
        types, [_make_hook_p(contexts, 0), args[1], _make_hook_p(contexts, 0)]
    )

    assert _apply_fixed_patches(tmpl, contexts, data1) == data1


# ---------------------------------------------------------------------------
# Tests for the public encode_packed_with_hooks() API
# ---------------------------------------------------------------------------


def test_encode_packed_with_hooks_basic():
    """encode_packed_with_hooks() returns values with hooks replaced by their return values."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return 99

    types = ["uint8", "uint8", "uint8"]
    resolved = encode_packed_with_hooks(types, [1, hook, 3])
    assert len(captured) == 1
    # uint8 = 1 byte, so hook is at offset 1
    assert captured[0] == EncodingContext(offset=1, size=1, encoder=registry_packed.get_encoder("uint8"))


def test_encode_packed_with_hooks_address():
    """encode_packed_with_hooks() tracks 20-byte address offsets correctly."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return "0x" + "ab" * 20

    types = ["uint8", "address"]
    encode_packed_with_hooks(types, [1, hook])
    # uint8 = 1 byte, so address hook is at offset 1
    assert captured[0] == EncodingContext(offset=1, size=20, encoder=registry_packed.get_encoder("address"))


def test_encode_packed_with_hooks_variable_bytes():
    """encode_packed_with_hooks() tracks offsets after variable-length bytes."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return 0

    types = ["bytes", "uint8"]
    encode_packed_with_hooks(types, [b"hello", hook])
    # b"hello" = 5 bytes packed, so uint8 hook is at offset 5
    assert captured[0] == EncodingContext(offset=5, size=1, encoder=registry_packed.get_encoder("uint8"))


def test_encode_packed_with_hooks_then_encode_matches_direct():
    """encode_packed(encode_packed_with_hooks(types, args)) == encode_packed(types, args)."""
    types = ["uint8", "uint16", "address", "bytes32"]
    args = [1, 500, "0x" + "cd" * 20, b"\xab" * 32]
    data_direct = encode_packed(types, args)

    def make_hook(real_val):
        def hook(ctx):
            return real_val

        return hook

    data_via_resolve = encode_packed_with_hooks(types, [make_hook(v) for v in args])
    assert data_direct == data_via_resolve


# ---------------------------------------------------------------------------
# Tests for EncodingContext.size
# ---------------------------------------------------------------------------


def test_encoding_context_size_packed_fixed():
    """size reflects the natural packed byte width for fixed-size types."""
    captured = []

    def make_hook(ret_val):
        def hook(ctx):
            captured.append(ctx)
            return ret_val
        return hook

    # uint8=1 byte, uint16=2 bytes, uint32=4 bytes, uint256=32 bytes, address=20 bytes
    types = ["uint8", "uint16", "uint32", "uint256", "address"]
    placeholders = [0, 0, 0, 0, "0x" + "00" * 20]
    hooks = [make_hook(p) for p in placeholders]
    encode_packed_with_hooks(types, hooks)

    expected_sizes = [1, 2, 4, 32, 20]
    for ctx, expected in zip(captured, expected_sizes):
        assert (
            ctx.size == expected
        ), f"encoder={ctx.encoder.__class__.__name__}: expected size {expected}, got {ctx.size}"


def test_encoding_context_size_packed_variable_bytes():
    """size for packed bytes reflects the raw byte length of the placeholder."""
    sizes_during = []
    ctx_refs = []

    def hook(ctx):
        sizes_during.append(ctx.size)
        ctx_refs.append(ctx)
        return b"\x00" * 7  # 7-byte placeholder

    encode_packed_with_hooks(["bytes"], [hook])
    # bytes is dynamic in the packed sense (no data_byte_size); None during hook
    assert sizes_during[0] is None
    # size is None for dynamic types, it's tricky to do runtime replacing for dynamic types.
    assert ctx_refs[0].size is None


def test_encoding_context_size_packed_round_trip():
    """ctx.size works for round-trip patching in packed mode."""

    types = ["uint8", "uint32", "uint8"]
    args = [10, 99999, 20]
    data1 = encode_packed(types, args)

    ctx_refs = []

    def hook(ctx):
        ctx_refs.append(ctx)
        return 0  # zero placeholder

    tmpl = encode_packed_with_hooks(types, [args[0], hook, args[2]])

    ctx = ctx_refs[0]
    assert ctx.size == 4  # uint32 = 4 bytes
    patched = tmpl[: ctx.offset] + data1[ctx.offset : ctx.offset + ctx.size] + tmpl[ctx.offset + ctx.size :]
    assert patched == data1
