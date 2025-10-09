import datetime
import typing

import kubernetes.client

class V1alpha1PodCertificateRequestSpec:
    max_expiration_seconds: typing.Optional[int]
    node_name: str
    node_uid: str
    pkix_public_key: str
    pod_name: str
    pod_uid: str
    proof_of_possession: str
    service_account_name: str
    service_account_uid: str
    signer_name: str
    
    def __init__(self, *, max_expiration_seconds: typing.Optional[int] = ..., node_name: str, node_uid: str, pkix_public_key: str, pod_name: str, pod_uid: str, proof_of_possession: str, service_account_name: str, service_account_uid: str, signer_name: str) -> None:
        ...
    def to_dict(self) -> V1alpha1PodCertificateRequestSpecDict:
        ...
class V1alpha1PodCertificateRequestSpecDict(typing.TypedDict, total=False):
    maxExpirationSeconds: typing.Optional[int]
    nodeName: str
    nodeUID: str
    pkixPublicKey: str
    podName: str
    podUID: str
    proofOfPossession: str
    serviceAccountName: str
    serviceAccountUID: str
    signerName: str
