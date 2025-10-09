import datetime
import typing

import kubernetes.client

class V1beta2DeviceClassConfiguration:
    opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfiguration]
    
    def __init__(self, *, opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfiguration] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceClassConfigurationDict:
        ...
class V1beta2DeviceClassConfigurationDict(typing.TypedDict, total=False):
    opaque: typing.Optional[kubernetes.client.V1beta2OpaqueDeviceConfigurationDict]
