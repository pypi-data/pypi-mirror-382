import datetime
import typing

import kubernetes.client

class V1beta1LeaseCandidateList:
    api_version: typing.Optional[str]
    items: list[kubernetes.client.V1beta1LeaseCandidate]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMeta]
    
    def __init__(self, *, api_version: typing.Optional[str] = ..., items: list[kubernetes.client.V1beta1LeaseCandidate], kind: typing.Optional[str] = ..., metadata: typing.Optional[kubernetes.client.V1ListMeta] = ...) -> None:
        ...
    def to_dict(self) -> V1beta1LeaseCandidateListDict:
        ...
class V1beta1LeaseCandidateListDict(typing.TypedDict, total=False):
    apiVersion: typing.Optional[str]
    items: list[kubernetes.client.V1beta1LeaseCandidateDict]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMetaDict]
