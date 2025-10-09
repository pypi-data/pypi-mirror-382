import datetime
import typing

import kubernetes.client

class V1VolumeError:
    error_code: typing.Optional[int]
    message: typing.Optional[str]
    time: typing.Optional[datetime.datetime]
    
    def __init__(self, *, error_code: typing.Optional[int] = ..., message: typing.Optional[str] = ..., time: typing.Optional[datetime.datetime] = ...) -> None:
        ...
    def to_dict(self) -> V1VolumeErrorDict:
        ...
class V1VolumeErrorDict(typing.TypedDict, total=False):
    errorCode: typing.Optional[int]
    message: typing.Optional[str]
    time: typing.Optional[datetime.datetime]
