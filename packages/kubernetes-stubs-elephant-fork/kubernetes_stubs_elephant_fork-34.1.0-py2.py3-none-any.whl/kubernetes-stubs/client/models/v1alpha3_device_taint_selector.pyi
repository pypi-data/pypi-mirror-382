import datetime
import typing

import kubernetes.client

class V1alpha3DeviceTaintSelector:
    device: typing.Optional[str]
    device_class_name: typing.Optional[str]
    driver: typing.Optional[str]
    pool: typing.Optional[str]
    selectors: typing.Optional[list[kubernetes.client.V1alpha3DeviceSelector]]
    
    def __init__(self, *, device: typing.Optional[str] = ..., device_class_name: typing.Optional[str] = ..., driver: typing.Optional[str] = ..., pool: typing.Optional[str] = ..., selectors: typing.Optional[list[kubernetes.client.V1alpha3DeviceSelector]] = ...) -> None:
        ...
    def to_dict(self) -> V1alpha3DeviceTaintSelectorDict:
        ...
class V1alpha3DeviceTaintSelectorDict(typing.TypedDict, total=False):
    device: typing.Optional[str]
    deviceClassName: typing.Optional[str]
    driver: typing.Optional[str]
    pool: typing.Optional[str]
    selectors: typing.Optional[list[kubernetes.client.V1alpha3DeviceSelectorDict]]
