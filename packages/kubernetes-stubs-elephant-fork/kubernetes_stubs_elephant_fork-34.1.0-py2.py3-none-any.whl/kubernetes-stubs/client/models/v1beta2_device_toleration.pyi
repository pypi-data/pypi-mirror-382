import datetime
import typing

import kubernetes.client

class V1beta2DeviceToleration:
    effect: typing.Optional[str]
    key: typing.Optional[str]
    operator: typing.Optional[str]
    toleration_seconds: typing.Optional[int]
    value: typing.Optional[str]
    
    def __init__(self, *, effect: typing.Optional[str] = ..., key: typing.Optional[str] = ..., operator: typing.Optional[str] = ..., toleration_seconds: typing.Optional[int] = ..., value: typing.Optional[str] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceTolerationDict:
        ...
class V1beta2DeviceTolerationDict(typing.TypedDict, total=False):
    effect: typing.Optional[str]
    key: typing.Optional[str]
    operator: typing.Optional[str]
    tolerationSeconds: typing.Optional[int]
    value: typing.Optional[str]
