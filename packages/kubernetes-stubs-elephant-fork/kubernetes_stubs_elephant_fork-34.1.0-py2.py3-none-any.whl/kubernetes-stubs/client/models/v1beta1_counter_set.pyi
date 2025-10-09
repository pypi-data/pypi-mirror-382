import datetime
import typing

import kubernetes.client

class V1beta1CounterSet:
    counters: dict[str, kubernetes.client.V1beta1Counter]
    name: str
    
    def __init__(self, *, counters: dict[str, kubernetes.client.V1beta1Counter], name: str) -> None:
        ...
    def to_dict(self) -> V1beta1CounterSetDict:
        ...
class V1beta1CounterSetDict(typing.TypedDict, total=False):
    counters: dict[str, kubernetes.client.V1beta1CounterDict]
    name: str
