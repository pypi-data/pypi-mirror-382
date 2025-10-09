import datetime
import typing

import kubernetes.client

class V1alpha3DeviceTaintRuleSpec:
    device_selector: typing.Optional[kubernetes.client.V1alpha3DeviceTaintSelector]
    taint: kubernetes.client.V1alpha3DeviceTaint
    
    def __init__(self, *, device_selector: typing.Optional[kubernetes.client.V1alpha3DeviceTaintSelector] = ..., taint: kubernetes.client.V1alpha3DeviceTaint) -> None:
        ...
    def to_dict(self) -> V1alpha3DeviceTaintRuleSpecDict:
        ...
class V1alpha3DeviceTaintRuleSpecDict(typing.TypedDict, total=False):
    deviceSelector: typing.Optional[kubernetes.client.V1alpha3DeviceTaintSelectorDict]
    taint: kubernetes.client.V1alpha3DeviceTaintDict
