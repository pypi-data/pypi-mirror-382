import datetime
import typing

import kubernetes.client

class V1beta2OpaqueDeviceConfiguration:
    driver: str
    parameters: typing.Any
    
    def __init__(self, *, driver: str, parameters: typing.Any) -> None:
        ...
    def to_dict(self) -> V1beta2OpaqueDeviceConfigurationDict:
        ...
class V1beta2OpaqueDeviceConfigurationDict(typing.TypedDict, total=False):
    driver: str
    parameters: typing.Any
