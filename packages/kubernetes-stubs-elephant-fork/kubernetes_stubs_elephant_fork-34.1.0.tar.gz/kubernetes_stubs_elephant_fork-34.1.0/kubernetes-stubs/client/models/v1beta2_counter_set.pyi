import datetime
import typing

import kubernetes.client

class V1beta2CounterSet:
    counters: dict[str, kubernetes.client.V1beta2Counter]
    name: str
    
    def __init__(self, *, counters: dict[str, kubernetes.client.V1beta2Counter], name: str) -> None:
        ...
    def to_dict(self) -> V1beta2CounterSetDict:
        ...
class V1beta2CounterSetDict(typing.TypedDict, total=False):
    counters: dict[str, kubernetes.client.V1beta2CounterDict]
    name: str
