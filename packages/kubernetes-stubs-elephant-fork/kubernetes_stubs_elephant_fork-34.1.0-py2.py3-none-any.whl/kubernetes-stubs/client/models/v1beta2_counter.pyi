import datetime
import typing

import kubernetes.client

class V1beta2Counter:
    value: str
    
    def __init__(self, *, value: str) -> None:
        ...
    def to_dict(self) -> V1beta2CounterDict:
        ...
class V1beta2CounterDict(typing.TypedDict, total=False):
    value: str
