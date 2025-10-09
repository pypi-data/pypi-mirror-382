import datetime
import typing

import kubernetes.client

class V1PodCertificateProjection:
    certificate_chain_path: typing.Optional[str]
    credential_bundle_path: typing.Optional[str]
    key_path: typing.Optional[str]
    key_type: str
    max_expiration_seconds: typing.Optional[int]
    signer_name: str
    
    def __init__(self, *, certificate_chain_path: typing.Optional[str] = ..., credential_bundle_path: typing.Optional[str] = ..., key_path: typing.Optional[str] = ..., key_type: str, max_expiration_seconds: typing.Optional[int] = ..., signer_name: str) -> None:
        ...
    def to_dict(self) -> V1PodCertificateProjectionDict:
        ...
class V1PodCertificateProjectionDict(typing.TypedDict, total=False):
    certificateChainPath: typing.Optional[str]
    credentialBundlePath: typing.Optional[str]
    keyPath: typing.Optional[str]
    keyType: str
    maxExpirationSeconds: typing.Optional[int]
    signerName: str
