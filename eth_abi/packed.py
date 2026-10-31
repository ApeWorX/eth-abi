from .codec import (
    ABIEncoder,
)
from .registry import (
    registry_packed,
)

default_encoder_packed = ABIEncoder(registry_packed)

encode_packed = default_encoder_packed.encode
encode_packed_with_hooks = default_encoder_packed.encode_with_hooks
is_encodable_packed = default_encoder_packed.is_encodable
