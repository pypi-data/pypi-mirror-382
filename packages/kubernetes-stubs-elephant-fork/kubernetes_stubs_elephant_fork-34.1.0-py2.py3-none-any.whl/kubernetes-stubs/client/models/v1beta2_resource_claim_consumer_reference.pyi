import datetime
import typing

import kubernetes.client

class V1beta2ResourceClaimConsumerReference:
    api_group: typing.Optional[str]
    name: str
    resource: str
    uid: str
    
    def __init__(self, *, api_group: typing.Optional[str] = ..., name: str, resource: str, uid: str) -> None:
        ...
    def to_dict(self) -> V1beta2ResourceClaimConsumerReferenceDict:
        ...
class V1beta2ResourceClaimConsumerReferenceDict(typing.TypedDict, total=False):
    apiGroup: typing.Optional[str]
    name: str
    resource: str
    uid: str
