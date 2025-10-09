import datetime
import typing

import kubernetes.client

class V1ServiceCIDRList:
    api_version: typing.Optional[str]
    items: list[kubernetes.client.V1ServiceCIDR]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMeta]
    
    def __init__(self, *, api_version: typing.Optional[str] = ..., items: list[kubernetes.client.V1ServiceCIDR], kind: typing.Optional[str] = ..., metadata: typing.Optional[kubernetes.client.V1ListMeta] = ...) -> None:
        ...
    def to_dict(self) -> V1ServiceCIDRListDict:
        ...
class V1ServiceCIDRListDict(typing.TypedDict, total=False):
    apiVersion: typing.Optional[str]
    items: list[kubernetes.client.V1ServiceCIDRDict]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMetaDict]
