import datetime
import typing

import kubernetes.client

class V1beta1Counter:
    value: str
    
    def __init__(self, *, value: str) -> None:
        ...
    def to_dict(self) -> V1beta1CounterDict:
        ...
class V1beta1CounterDict(typing.TypedDict, total=False):
    value: str
