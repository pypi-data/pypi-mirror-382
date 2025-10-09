import datetime
import typing

import kubernetes.client

class V1beta2DeviceCounterConsumption:
    counter_set: str
    counters: dict[str, kubernetes.client.V1beta2Counter]
    
    def __init__(self, *, counter_set: str, counters: dict[str, kubernetes.client.V1beta2Counter]) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceCounterConsumptionDict:
        ...
class V1beta2DeviceCounterConsumptionDict(typing.TypedDict, total=False):
    counterSet: str
    counters: dict[str, kubernetes.client.V1beta2CounterDict]
