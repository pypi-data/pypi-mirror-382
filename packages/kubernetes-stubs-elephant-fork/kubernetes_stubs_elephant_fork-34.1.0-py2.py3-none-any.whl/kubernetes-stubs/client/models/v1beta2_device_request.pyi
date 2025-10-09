import datetime
import typing

import kubernetes.client

class V1beta2DeviceRequest:
    exactly: typing.Optional[kubernetes.client.V1beta2ExactDeviceRequest]
    first_available: typing.Optional[list[kubernetes.client.V1beta2DeviceSubRequest]]
    name: str
    
    def __init__(self, *, exactly: typing.Optional[kubernetes.client.V1beta2ExactDeviceRequest] = ..., first_available: typing.Optional[list[kubernetes.client.V1beta2DeviceSubRequest]] = ..., name: str) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceRequestDict:
        ...
class V1beta2DeviceRequestDict(typing.TypedDict, total=False):
    exactly: typing.Optional[kubernetes.client.V1beta2ExactDeviceRequestDict]
    firstAvailable: typing.Optional[list[kubernetes.client.V1beta2DeviceSubRequestDict]]
    name: str
