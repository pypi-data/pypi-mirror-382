import datetime
import typing

import kubernetes.client

class V1beta2DeviceAllocationConfiguration:
    opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfiguration]
    requests: typing.Optional[list[str]]
    source: str
    
    def __init__(self, *, opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfiguration] = ..., requests: typing.Optional[list[str]] = ..., source: str) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceAllocationConfigurationDict:
        ...
class V1beta2DeviceAllocationConfigurationDict(typing.TypedDict, total=False):
    opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfigurationDict]
    requests: typing.Optional[list[str]]
    source: str
