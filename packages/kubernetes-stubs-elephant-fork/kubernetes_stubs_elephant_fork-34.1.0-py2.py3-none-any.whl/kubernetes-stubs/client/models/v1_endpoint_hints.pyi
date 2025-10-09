import datetime
import typing

import kubernetes.client

class V1EndpointHints:
    for_nodes: typing.Optional[list[kubernetes.client.V1ForNode]]
    for_zones: typing.Optional[list[kubernetes.client.V1ForZone]]
    
    def __init__(self, *, for_nodes: typing.Optional[list[kubernetes.client.V1ForNode]] = ..., for_zones: typing.Optional[list[kubernetes.client.V1ForZone]] = ...) -> None:
        ...
    def to_dict(self) -> V1EndpointHintsDict:
        ...
class V1EndpointHintsDict(typing.TypedDict, total=False):
    forNodes: typing.Optional[list[kubernetes.client.V1ForNodeDict]]
    forZones: typing.Optional[list[kubernetes.client.V1ForZoneDict]]
