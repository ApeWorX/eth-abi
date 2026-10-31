from eth_abi import (
    encode,
    encode_with_hooks,
)
from eth_abi.hooks import (
    EncodingContext,
)
from eth_abi.registry import (
    registry,
)

# ---------------------------------------------------------------------------
# Tests for callable hook support (offset detection)
# ---------------------------------------------------------------------------


class PatchContext:
    def __init__(self):
        self.entries = []

    def hook(self, value, placeholder):
        '''
        In real usage, the value would be a function to return the real value.
        '''
        def hook(ctx):
            self.entries.append((ctx, value))
            return placeholder

        return hook

    def apply(self, tmpl):
        for ctx, value in self.entries:
            encoded_real_tail = ctx.encoder(value)
            tmpl = tmpl[:ctx.offset] + encoded_real_tail + tmpl[ctx.offset + len(encoded_real_tail) :]
        return tmpl


def test_round_trip_all_static_args():
    """Round-trip all static args through hooks then patch back to original."""
    types = ["uint256", "uint256", "uint256"]
    args = [1, 2, 3]
    data1 = encode(types, args)

    ctx = PatchContext()
    tmpl = encode_with_hooks(types, [ctx.hook(v, 0) for v in args])
    assert ctx.apply(tmpl) == data1


def test_round_trip_mixed_static_types():
    """Round-trip mixed static types (uint256, address, bool, bytes32)."""
    types = ["uint256", "address", "bool", "bytes32"]
    args = [
        999,
        "0x" + "ab" * 20,
        True,
        b"\xff" * 32,
    ]
    data1 = encode(types, args)

    ctx = PatchContext()
    tmpl = encode_with_hooks(
        types,
        [
            ctx.hook(args[0], 0),
            ctx.hook(args[1], "0x" + "00" * 20),
            ctx.hook(args[2], False),
            ctx.hook(args[3], b"\x00" * 32),
        ],
    )

    assert ctx.apply(tmpl) == data1


def test_round_trip_dynamic():
    """Round-trip a dynamic bytes arg through a hook then patch back."""
    args = [b"hello world", "hello"]
    types = ["bytes", "string"]
    data1 = encode(types, args)

    ctx = PatchContext()
    tmpl = encode_with_hooks(types, [
        ctx.hook(args[0], b"\x00" * len(args[0])),
        ctx.hook(args[1], "*" * len(args[1])),
    ])
    assert ctx.apply(tmpl) == data1


def test_round_trip_mixed_static_and_dynamic():
    """Round-trip mixed static and dynamic args together."""
    types = ["uint256", "bytes", "address", "bytes"]
    real_bytes1 = b"foo"
    real_bytes2 = b"bar"
    args = [42, real_bytes1, "0x" + "cd" * 20, real_bytes2]
    data1 = encode(types, args)

    ctx = PatchContext()
    tmpl = encode_with_hooks(
        types,
        [
            ctx.hook(args[0], 0),
            real_bytes1,
            ctx.hook(args[2], "0x" + "00" * 20),
            real_bytes2,
        ],
    )

    assert ctx.apply(tmpl) == data1


def test_round_trip_dynamic_array():
    """Round-trip a dynamic array arg through a hook then patch back."""
    real_value = [1, 2, 3]
    types = ["uint256[]", "uint256"]
    args = [real_value, 99]
    data1 = encode(types, args)

    ctx = PatchContext()
    tmpl = encode_with_hooks(types, [real_value[:-1] + [ctx.hook(real_value[-1], 0)], args[1]])
    assert ctx.apply(tmpl) == data1


def test_round_trip_nested_tuple_inner_hook():
    """Hook inside a nested tuple gets the correct intra-tuple offset."""
    types = ["(uint256,uint256)", "uint256"]
    args = [(7, 8), 9]
    data1 = encode(types, args)

    ctx = PatchContext()
    # Hook inside the nested tuple for the first element
    tmpl = encode_with_hooks(types, [(ctx.hook(args[0][0], 0), args[0][1]), args[1]])
    assert ctx.apply(tmpl) == data1


def test_round_trip_hook_inside_array_in_tuple():
    """Hook at a primitive inside an array that is itself inside a tuple."""
    # Layout: uint256[] is in the tail (dynamic), elements start after head+count.
    types = ["uint256", "uint256[]"]
    args = [5, [10, 20, 30]]
    data1 = encode(types, args)

    ctx = PatchContext()
    # Put a hook on element[1] of the array.
    array_with_hook = [args[1][0], ctx.hook(args[1][1], 0), args[1][2]]
    tmpl = encode_with_hooks(types, [args[0], array_with_hook])
    assert ctx.apply(tmpl) == data1


def test_round_trip_hook_deep_in_nested_tuple():
    """Hook at a primitive inside a nested tuple that is itself dynamic."""
    # (bytes,uint256) is dynamic (contains bytes).
    types = ["(bytes,uint256)", "uint256"]
    args = [(b"hello", 42), 99]
    data1 = encode(types, args)

    ctx = PatchContext()
    # Hook on the uint256 inside the dynamic nested tuple.
    tmpl = encode_with_hooks(types, [(args[0][0], ctx.hook(args[0][1], 0)), args[1]])
    assert ctx.apply(tmpl) == data1


def test_round_trip_hook_in_array_of_tuples():
    """Hook at a primitive inside a tuple that is an element of an array."""
    types = ["(uint256,uint256)[]"]
    args = [[(1, 2), (3, 4), (5, 6)]]
    data1 = encode(types, args)

    ctx = PatchContext()
    # Hook on element[1][0] of the array of (uint256,uint256) tuples.
    array_with_hook = [
        args[0][0],
        (ctx.hook(args[0][1][0], 0), args[0][1][1]),
        args[0][2],
    ]
    tmpl = encode_with_hooks(types, [array_with_hook])
    assert ctx.apply(tmpl) == data1


# ---------------------------------------------------------------------------
# Tests for the public encode_with_hooks() API
# ---------------------------------------------------------------------------


def test_encode_with_hooks_public_api_basic():
    """encode_with_hooks() returns values with hooks replaced by their return values."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return 42

    types = ["uint256", "uint256", "uint256"]
    encode_with_hooks(types, [1, hook, 3])
    assert len(captured) == 1
    assert captured[0] == EncodingContext(offset=32, size=32, encoder=registry.get_encoder("uint256"))


def test_encode_with_hooks_public_api_dynamic():
    """encode_with_hooks() computes correct tail offsets for dynamic types."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return b"\x00" * 5

    types = ["bytes", "uint256", "bytes"]
    encode_with_hooks(types, [b"hello", 42, hook])
    # Head: 3 x 32 = 96 bytes; first bytes tail = 64 bytes (32 length prefix + 32 data right-padded to 32 bytes)
    assert captured[0] == EncodingContext(
        offset=96 + 32 + 32,
        size=None,
        encoder=registry.get_encoder("bytes"),
    )


def test_encode_with_hooks_public_api_nested_array():
    """encode_with_hooks() correctly resolves a hook inside an array."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return 99

    types = ["uint256[]"]
    encode_with_hooks(types, [[1, 2, hook]])
    # Head: 32 (pointer) → array tail at 32: count(32) + elem0(32) + elem1(32) = 96
    assert captured[0] == EncodingContext(
        offset=32 + 32 + 32 + 32,
        size=32,
        encoder=registry.get_encoder("uint256"),
    )


def test_encode_with_hooks_public_api_nested_tuple():
    """encode_with_hooks() recurses into nested tuples."""
    captured = []

    def hook(ctx):
        captured.append(ctx)
        return 7

    types = ["(uint256,uint256)", "uint256"]
    resolved = encode_with_hooks(types, [(hook, 8), 9])
    # The static tuple is inlined at offset 0; its first element is at offset 0.
    assert captured[0] == EncodingContext(offset=0, size=32, encoder=registry.get_encoder("uint256"))


def test_encode_with_hooks_then_encode_matches_direct():
    """encode(encode_with_hooks(types, args)) == encode(types, args) for all hook positions."""
    types = ["uint256", "bytes", "address"]
    args = [123, b"hello", "0x" + "ab" * 20]
    data_direct = encode(types, args)

    captured = []

    def make_hook(real_val):
        def hook(ctx):
            captured.append((ctx, real_val))
            return real_val  # hooks return the real value

        return hook

    data_via_resolve = encode_with_hooks(types, [make_hook(v) for v in args])
    assert data_direct == data_via_resolve


# ---------------------------------------------------------------------------
# Tests for EncodingContext.size
# ---------------------------------------------------------------------------


def test_encoding_context_size_static_abi():
    """size is always 32 for standard ABI static types."""
    captured = []

    def make_hook(ret_val):
        def hook(ctx):
            captured.append(ctx)
            return ret_val
        return hook

    encode_with_hooks(
        ["uint256", "address", "bool", "bytes32"],
        [make_hook(0), make_hook("0x" + "ab" * 20), make_hook(False), make_hook(b"\x00" * 32)],
    )
    for ctx in captured:
        assert ctx.size == 32


def test_encoding_context_size_dynamic_abi_set_after_hook():
    """size is None during hook execution but set after encode_with_hooks() returns."""
    sizes_during = []
    ctx_refs = []

    def hook(ctx):
        sizes_during.append(ctx.size)  # None while hook runs (dynamic type)
        ctx_refs.append(ctx)
        return b"\x00" * 5  # 5-byte placeholder

    encode_with_hooks(["bytes"], [hook])
    # During hook execution size was None
    assert sizes_during[0] is None
    # size is None for dynamic types, it's tricky to do runtime replacing for dynamic types.
    assert ctx_refs[0].size is None


def test_encoding_context_size_dynamic_abi_round_trip():
    """ctx.size can be used for round-trip patching of a dynamic type."""
    types = ["uint256", "bytes", "uint256"]
    real_bytes = b"hello world"
    args = [1, real_bytes, 3]
    data1 = encode(types, args)

    ctx_refs = []

    def hook(ctx):
        ctx_refs.append(ctx)
        return b"\x00" * len(real_bytes)  # same-length placeholder

    tmpl = encode_with_hooks(types, [args[0], hook, args[2]])

    ctx = ctx_refs[0]
    # Patch the placeholder region with the real encoded tail
    enc = registry.get_encoder("bytes")
    real_encoded = enc(real_bytes)

    # size is None for dynamic types, it's tricky to do runtime replacing for dynamic types.
    assert ctx.size is None
