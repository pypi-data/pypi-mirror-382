import datetime
import typing

import kubernetes.client

class V1beta2CELDeviceSelector:
    expression: str
    
    def __init__(self, *, expression: str) -> None:
        ...
    def to_dict(self) -> V1beta2CELDeviceSelectorDict:
        ...
class V1beta2CELDeviceSelectorDict(typing.TypedDict, total=False):
    expression: str
