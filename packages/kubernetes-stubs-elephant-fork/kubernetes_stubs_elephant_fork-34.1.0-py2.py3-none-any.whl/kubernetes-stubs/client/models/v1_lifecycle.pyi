import datetime
import typing

import kubernetes.client

class V1Lifecycle:
    post_start: typing.Optional[kubernetes.client.V1LifecycleHandler]
    pre_stop: typing.Optional[kubernetes.client.V1LifecycleHandler]
    stop_signal: typing.Optional[str]
    
    def __init__(self, *, post_start: typing.Optional[kubernetes.client.V1LifecycleHandler] = ..., pre_stop: typing.Optional[kubernetes.client.V1LifecycleHandler] = ..., stop_signal: typing.Optional[str] = ...) -> None:
        ...
    def to_dict(self) -> V1LifecycleDict:
        ...
class V1LifecycleDict(typing.TypedDict, total=False):
    postStart: typing.Optional[kubernetes.client.V1LifecycleHandlerDict]
    preStop: typing.Optional[kubernetes.client.V1LifecycleHandlerDict]
    stopSignal: typing.Optional[str]
