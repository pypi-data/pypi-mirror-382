import datetime
import typing

import kubernetes.client

class V1beta1ClusterTrustBundleList:
    api_version: typing.Optional[str]
    items: list[kubernetes.client.V1beta1ClusterTrustBundle]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMeta]
    
    def __init__(self, *, api_version: typing.Optional[str] = ..., items: list[kubernetes.client.V1beta1ClusterTrustBundle], kind: typing.Optional[str] = ..., metadata: typing.Optional[kubernetes.client.V1ListMeta] = ...) -> None:
        ...
    def to_dict(self) -> V1beta1ClusterTrustBundleListDict:
        ...
class V1beta1ClusterTrustBundleListDict(typing.TypedDict, total=False):
    apiVersion: typing.Optional[str]
    items: list[kubernetes.client.V1beta1ClusterTrustBundleDict]
    kind: typing.Optional[str]
    metadata: typing.Optional[kubernetes.client.V1ListMetaDict]
