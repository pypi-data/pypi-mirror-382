import datetime
import typing

import kubernetes.client

class V1beta2ResourceClaimTemplateList:
    api_version: typing.Optional[str]
    items: list[kubernetes.client.V1beta2ResourceClaimTemplate]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMeta]
    
    def __init__(self, *, api_version: typing.Optional[str] = ..., items: list[kubernetes.client.V1beta2ResourceClaimTemplate], kind: typing.Optional[str] = ..., metadata: typing.Optional[kubernetes.client.V1ListMeta] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2ResourceClaimTemplateListDict:
        ...
class V1beta2ResourceClaimTemplateListDict(typing.TypedDict, total=False):
    apiVersion: typing.Optional[str]
    items: list[kubernetes.client.V1beta2ResourceClaimTemplateDict]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMetaDict]
