# ruff: noqa: ANN401, RUF100,


import gwproto.named_types.cacs
import gwproto.named_types.components
from gwproto.decoders import CacDecoder, ComponentDecoder

__all__ = [
    "default_cac_decoder",
    "default_component_decoder",
]

default_cac_decoder = CacDecoder(
    model_name="DefaultCacDecoder",
    modules=[gwproto.named_types.cacs],
)

default_component_decoder = ComponentDecoder(
    model_name="DefaultComponentDecoder",
    modules=[gwproto.named_types.components],
)
