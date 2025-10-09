import datetime
import typing

import kubernetes.client

class V1beta1DeviceCounterConsumption:
    counter_set: str
    counters: dict[str, kubernetes.client.V1beta1Counter]
    
    def __init__(self, *, counter_set: str, counters: dict[str, kubernetes.client.V1beta1Counter]) -> None:
        ...
    def to_dict(self) -> V1beta1DeviceCounterConsumptionDict:
        ...
class V1beta1DeviceCounterConsumptionDict(typing.TypedDict, total=False):
    counterSet: str
    counters: dict[str, kubernetes.client.V1beta1CounterDict]
