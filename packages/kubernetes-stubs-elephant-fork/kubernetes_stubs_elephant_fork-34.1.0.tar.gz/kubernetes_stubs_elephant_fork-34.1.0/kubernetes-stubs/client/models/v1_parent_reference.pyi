import datetime
import typing

import kubernetes.client

class V1ParentReference:
    group: typing.Optional[str]
    name: str
    namespace: typing.Optional[str]
    resource: str
    
    def __init__(self, *, group: typing.Optional[str] = ..., name: str, namespace: typing.Optional[str] = ..., resource: str) -> None:
        ...
    def to_dict(self) -> V1ParentReferenceDict:
        ...
class V1ParentReferenceDict(typing.TypedDict, total=False):
    group: typing.Optional[str]
    name: str
    namespace: typing.Optional[str]
    resource: str
