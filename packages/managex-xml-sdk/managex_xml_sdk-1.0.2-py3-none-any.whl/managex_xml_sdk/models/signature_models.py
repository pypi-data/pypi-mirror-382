"""
Signature related models and enums for ManageX XML Signing SDK
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class SignatureAlgorithm(Enum):
    """XML Digital Signature algorithms"""
    RSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
    RSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    RSA_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha384"
    RSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha512"
    DSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#dsa-sha1"
    DSA_SHA256 = "http://www.w3.org/2009/xmldsig11#dsa-sha256"
    ECDSA_SHA1 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha1"
    ECDSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"
    ECDSA_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha384"
    ECDSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha512"

class DigestAlgorithm(Enum):
    """Digest algorithms for XML signatures"""
    SHA1 = "http://www.w3.org/2000/09/xmldsig#sha1"
    SHA256 = "http://www.w3.org/2001/04/xmlenc#sha256"
    SHA384 = "http://www.w3.org/2001/04/xmldsig-more#sha384"
    SHA512 = "http://www.w3.org/2001/04/xmlenc#sha512"

class CanonicalizationAlgorithm(Enum):
    """Canonicalization algorithms"""
    C14N_OMIT_COMMENTS = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
    C14N_WITH_COMMENTS = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments"
    EXCLUSIVE_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"

class TransformAlgorithm(Enum):
    """Transform algorithms"""
    ENVELOPED_SIGNATURE = "http://www.w3.org/2000/09/xmldsig#enveloped-signature"
    C14N_OMIT_COMMENTS = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
    EXCLUSIVE_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"

@dataclass
class SignatureInfo:
    """Configuration for XML signature information"""
    signature_id: str = "ManageX-Signature"  # Fixed signature ID - cannot be changed
    canonicalization_algorithm: CanonicalizationAlgorithm = CanonicalizationAlgorithm.C14N_OMIT_COMMENTS
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.RSA_SHA256

    def __post_init__(self):
        """Ensure signature_id is always set to ManageX-Signature"""
        object.__setattr__(self, 'signature_id', "ManageX-Signature")

    def validate(self) -> bool:
        """Validate signature configuration"""
        if self.signature_id != "ManageX-Signature":
            raise ValueError("signature_id must be 'ManageX-Signature' and cannot be changed")
        if not isinstance(self.canonicalization_algorithm, CanonicalizationAlgorithm):
            raise ValueError("Invalid canonicalization algorithm")
        if not isinstance(self.signature_algorithm, SignatureAlgorithm):
            raise ValueError("Invalid signature algorithm")
        return True

@dataclass
class ReferenceInfo:
    """Configuration for XML signature reference"""
    uri: str = ""
    digest_algorithm: DigestAlgorithm = DigestAlgorithm.SHA256
    transforms: List[TransformAlgorithm] = None
    reference_id: Optional[str] = None

    def __post_init__(self):
        if self.transforms is None:
            self.transforms = [TransformAlgorithm.ENVELOPED_SIGNATURE, TransformAlgorithm.EXCLUSIVE_C14N]

    def validate(self) -> bool:
        """Validate reference configuration"""
        if not isinstance(self.uri, str):
            raise ValueError("URI must be a string")
        if not isinstance(self.digest_algorithm, DigestAlgorithm):
            raise ValueError("Invalid digest algorithm")
        if not isinstance(self.transforms, list):
            raise ValueError("Transforms must be a list")
        for transform in self.transforms:
            if not isinstance(transform, TransformAlgorithm):
                raise ValueError("Invalid transform algorithm")
        if self.reference_id and not isinstance(self.reference_id, str):
            raise ValueError("reference_id must be a string")
        return True

@dataclass
class KeyInfo:
    """Configuration for XML signature KeyInfo element"""
    include_subject_name: bool = True
    include_certificate: bool = True
    include_public_key: bool = False
    include_issuer_serial: bool = False
    include_subject_key_id: bool = False
    key_name: Optional[str] = None

    def validate(self) -> bool:
        """Validate KeyInfo configuration"""
        if not isinstance(self.include_subject_name, bool):
            raise ValueError("include_subject_name must be boolean")
        if not isinstance(self.include_certificate, bool):
            raise ValueError("include_certificate must be boolean")
        if not isinstance(self.include_public_key, bool):
            raise ValueError("include_public_key must be boolean")
        if not isinstance(self.include_issuer_serial, bool):
            raise ValueError("include_issuer_serial must be boolean")
        if not isinstance(self.include_subject_key_id, bool):
            raise ValueError("include_subject_key_id must be boolean")
        if self.key_name and not isinstance(self.key_name, str):
            raise ValueError("key_name must be a string")
        return True

@dataclass
class SignatureEnvelopeParameters:
    """Complete configuration for XML signature envelope"""
    signature_info: SignatureInfo
    reference_info: ReferenceInfo
    key_info: KeyInfo
    namespace_prefix: Optional[str] = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> bool:
        """Validate complete signature envelope configuration"""
        try:
            if not isinstance(self.signature_info, SignatureInfo):
                raise ValueError("signature_info must be SignatureInfo instance")
            self.signature_info.validate()

            if not isinstance(self.reference_info, ReferenceInfo):
                raise ValueError("reference_info must be ReferenceInfo instance")
            self.reference_info.validate()

            if not isinstance(self.key_info, KeyInfo):
                raise ValueError("key_info must be KeyInfo instance")
            self.key_info.validate()

            if self.namespace_prefix and not isinstance(self.namespace_prefix, str):
                raise ValueError("namespace_prefix must be a string")

            return True
        except ValueError as e:
            print(f"Validation error: {e}")
            raise

    @classmethod
    def create_default(cls):
        """Create default signature envelope parameters with fixed ManageX-Signature ID"""
        return cls(
            signature_info=SignatureInfo(),
            reference_info=ReferenceInfo(),
            key_info=KeyInfo()
        )