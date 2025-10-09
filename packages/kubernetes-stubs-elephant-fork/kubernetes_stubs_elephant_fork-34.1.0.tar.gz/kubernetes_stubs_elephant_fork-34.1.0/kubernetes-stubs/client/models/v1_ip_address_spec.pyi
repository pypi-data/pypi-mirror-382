import datetime
import typing

import kubernetes.client

class V1IPAddressSpec:
    parent_ref: kubernetes.client.V1ParentReference
    
    def __init__(self, *, parent_ref: kubernetes.client.V1ParentReference) -> None:
        ...
    def to_dict(self) -> V1IPAddressSpecDict:
        ...
class V1IPAddressSpecDict(typing.TypedDict, total=False):
    parentRef: kubernetes.client.V1ParentReferenceDict
