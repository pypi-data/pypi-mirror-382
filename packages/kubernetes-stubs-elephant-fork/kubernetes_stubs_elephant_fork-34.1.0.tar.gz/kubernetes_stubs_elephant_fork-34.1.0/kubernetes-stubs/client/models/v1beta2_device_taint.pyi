import datetime
import typing

import kubernetes.client

class V1beta2DeviceTaint:
    effect: str
    key: str
    time_added: typing.Optional[datetime.datetime]
    value: typing.Optional[str]
    
    def __init__(self, *, effect: str, key: str, time_added: typing.Optional[datetime.datetime] = ..., value: typing.Optional[str] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceTaintDict:
        ...
class V1beta2DeviceTaintDict(typing.TypedDict, total=False):
    effect: str
    key: str
    timeAdded: typing.Optional[datetime.datetime]
    value: typing.Optional[str]
