import datetime
import typing

import kubernetes.client

class V1NodeSwapStatus:
    capacity: typing.Optional[int]
    
    def __init__(self, *, capacity: typing.Optional[int] = ...) -> None:
        ...
    def to_dict(self) -> V1NodeSwapStatusDict:
        ...
class V1NodeSwapStatusDict(typing.TypedDict, total=False):
    capacity: typing.Optional[int]
