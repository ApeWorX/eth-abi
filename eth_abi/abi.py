from eth_abi.codec import (
    ABICodec,
)
from eth_abi.registry import (
    registry,
)

default_codec = ABICodec(registry)

encode = default_codec.encode
encode_with_hooks = default_codec.encode_with_hooks
decode = default_codec.decode
is_encodable = default_codec.is_encodable
is_encodable_type = default_codec.is_encodable_type
