import datetime
import typing

import kubernetes.client

class V1beta2DeviceClaim:
    config: typing.Optional[list[kubernetes.client.V1beta2DeviceClaimConfiguration]]
    constraints: typing.Optional[list[kubernetes.client.V1beta2DeviceConstraint]]
    requests: typing.Optional[list[kubernetes.client.V1beta2DeviceRequest]]
    
    def __init__(self, *, config: typing.Optional[list[kubernetes.client.V1beta2DeviceClaimConfiguration]] = ..., constraints: typing.Optional[list[kubernetes.client.V1beta2DeviceConstraint]] = ..., requests: typing.Optional[list[kubernetes.client.V1beta2DeviceRequest]] = ...) -> None:
        ...
    def to_dict(self) -> V1beta2DeviceClaimDict:
        ...
class V1beta2DeviceClaimDict(typing.TypedDict, total=False):
    config: typing.Optional[list[kubernetes.client.V1beta2DeviceClaimConfigurationDict]]
    constraints: typing.Optional[list[kubernetes.client.V1beta2DeviceConstraintDict]]
    requests: typing.Optional[list[kubernetes.client.V1beta2DeviceRequestDict]]
