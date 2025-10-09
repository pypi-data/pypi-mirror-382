import datetime
import typing

import kubernetes.client

class V1beta2DeviceClaimConfiguration:
    opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfiguration]
    requests: typing.Optional[list[str]]
    
    def __init__(self, *, opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfiguration] = ..., requests: typing.Optional[list[str]] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceClaimConfigurationDict:
        ...
class V1beta2DeviceClaimConfigurationDict(typing.TypedDict, total=False):
    opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfigurationDict]
    requests: typing.Optional[list[str]]
