import datetime
import typing

import kubernetes.client

class V1alpha3DeviceTaintRuleList:
    api_version: typing.Optional[str]
    items: list[kubernetes.client.V1alpha3DeviceTaintRule]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMeta]
    
    def __init__(self, *, api_version: typing.Optional[str] = ..., items: list[kubernetes.client.V1alpha3DeviceTaintRule], kind: typing.Optional[str] = ..., metadata: typing.Optional[kubernetes.client.V1ListMeta] = ...) -> None:
        ...
    def to_dict(self) -> V1alpha3DeviceTaintRuleListDict:
        ...
class V1alpha3DeviceTaintRuleListDict(typing.TypedDict, total=False):
    apiVersion: typing.Optional[str]
    items: list[kubernetes.client.V1alpha3DeviceTaintRuleDict]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMetaDict]
