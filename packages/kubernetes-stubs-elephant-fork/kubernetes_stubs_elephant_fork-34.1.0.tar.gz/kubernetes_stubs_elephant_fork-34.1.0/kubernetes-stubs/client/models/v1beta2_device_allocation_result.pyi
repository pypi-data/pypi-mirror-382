import datetime
import typing

import kubernetes.client

class V1beta2DeviceAllocationResult:
    config: typing.Optional[list[kubernetes.client.V1beta2DeviceAllocationConfiguration]]
    results: typing.Optional[list[kubernetes.client.V1beta2DeviceRequestAllocationResult]]
    
    def __init__(self, *, config: typing.Optional[list[kubernetes.client.V1beta2DeviceAllocationConfiguration]] = ..., results: typing.Optional[list[kubernetes.client.V1beta2DeviceRequestAllocationResult]] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceAllocationResultDict:
        ...
class V1beta2DeviceAllocationResultDict(typing.TypedDict, total=False):
    config: typing.Optional[list[kubernetes.client.V1beta2DeviceAllocationConfigurationDict]]
    results: typing.Optional[list[kubernetes.client.V1beta2DeviceRequestAllocationResultDict]]
