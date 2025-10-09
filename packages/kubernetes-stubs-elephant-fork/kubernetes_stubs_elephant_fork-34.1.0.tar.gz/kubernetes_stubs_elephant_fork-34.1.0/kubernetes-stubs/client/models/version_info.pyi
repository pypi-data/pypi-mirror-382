import datetime
import typing

import kubernetes.client

class VersionInfo:
    build_date: str
    compiler: str
    emulation_major: typing.Optional[str]
    emulation_minor: typing.Optional[str]
    git_commit: str
    git_tree_state: str
    git_version: str
    go_version: str
    major: str
    min_compatibility_major: typing.Optional[str]
    min_compatibility_minor: typing.Optional[str]
    minor: str
    platform: str
    
    def __init__(self, *, build_date: str, compiler: str, emulation_major: typing.Optional[str] = ..., emulation_minor: typing.Optional[str] = ..., git_commit: str, git_tree_state: str, git_version: str, go_version: str, major: str, min_compatibility_major: typing.Optional[str] = ..., min_compatibility_minor: typing.Optional[str] = ..., minor: str, platform: str) -> None:
        ...
    def to_dict(self) -> VersionInfoDict:
        ...
class VersionInfoDict(typing.TypedDict, total=False):
    buildDate: str
    compiler: str
    emulationMajor: typing.Optional[str]
    emulationMinor: typing.Optional[str]
    gitCommit: str
    gitTreeState: str
    gitVersion: str
    goVersion: str
    major: str
    minCompatibilityMajor: typing.Optional[str]
    minCompatibilityMinor: typing.Optional[str]
    minor: str
    platform: str
