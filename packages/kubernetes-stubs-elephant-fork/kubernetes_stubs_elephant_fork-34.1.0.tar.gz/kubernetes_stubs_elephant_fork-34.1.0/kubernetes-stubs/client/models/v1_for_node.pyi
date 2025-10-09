import datetime
import typing

import kubernetes.client

class V1ForNode:
    name: str
    
    def __init__(self, *, name: str) -> None:
        ...
    def to_dict(self) -> V1ForNodeDict:
        ...
class V1ForNodeDict(typing.TypedDict, total=False):
    name: str
