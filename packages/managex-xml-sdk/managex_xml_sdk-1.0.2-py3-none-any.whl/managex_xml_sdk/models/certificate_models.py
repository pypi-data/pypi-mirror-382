"""
Certificate related models for ManageX XML Signing SDK
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class CertificateInfo:
    """Certificate information container"""
    cert_context: Optional[object] = None
    subject_name: str = ""
    issuer_name: str = ""
    serial_number: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    cert_bytes: Optional[bytes] = None
    cert: Optional[object] = None
    thumbprint: Optional[str] = None
    dll_path: Optional[str] = None  # For HSM certificates

    def __str__(self):
        return f"{self.subject_name} (Serial: {self.serial_number})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'subject_name': self.subject_name,
            'issuer_name': self.issuer_name,
            'serial_number': self.serial_number,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_to': self.valid_to.isoformat() if self.valid_to else None,
            'thumbprint': self.thumbprint,
            'dll_path': self.dll_path
        }

@dataclass
class CertificateFilter:
    """Certificate filtering criteria"""
    cn: Optional[str] = None  # Common Name
    o: Optional[str] = None   # Organization
    ou: Optional[str] = None  # Organizational Unit
    email: Optional[str] = None  # Email from SAN
    serial: Optional[str] = None  # Serial number in hex
    ca: Optional[str] = None  # Issuer Common Name

    def has_filters(self) -> bool:
        """Check if any filters are set"""
        return any([self.cn, self.o, self.ou, self.email, self.serial, self.ca])

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class ValidationConfig:
    """Certificate validation configuration"""
    check_validity: bool = False
    check_revocation_crl: bool = False
    check_revocation_ocsp: bool = False
    trusted_roots_folder: str = "root_certificates"
    require_key_usage_for_signing: bool = True

    @classmethod
    def strict_validation(cls, trusted_roots_folder: str = "root_certificates"):
        """Create strict validation configuration"""
        return cls(
            check_validity=True,
            check_revocation_crl=True,
            check_revocation_ocsp=True,
            trusted_roots_folder=trusted_roots_folder,
            require_key_usage_for_signing=True
        )

    @classmethod
    def basic_validation(cls, trusted_roots_folder: str = "root_certificates"):
        """Create basic validation configuration - matches imb.py defaults"""
        return cls(
            check_validity=False,  # Match imb.py default: check_validity = "no"
            check_revocation_crl=False,  # Match imb.py default: check_revocation_crl = "no"
            check_revocation_ocsp=False,  # Match imb.py default: check_revocation_ocsp = "no"
            trusted_roots_folder=trusted_roots_folder,
            require_key_usage_for_signing=True
        )

@dataclass
class SignerConfig:
    """Base signer configuration"""
    method: str  # "store", "pfx", "hsm"
    certificate_filter: Optional[CertificateFilter] = None
    validation_config: Optional[ValidationConfig] = None

    def __post_init__(self):
        if self.certificate_filter is None:
            self.certificate_filter = CertificateFilter()
        if self.validation_config is None:
            self.validation_config = ValidationConfig.basic_validation()

@dataclass
class WindowsStoreConfig(SignerConfig):
    """Windows Certificate Store signer configuration"""
    store: str = "MY"  # Certificate store name
    method: str = "store"

@dataclass
class PFXConfig(SignerConfig):
    """PFX file signer configuration"""
    pfx_file: str = ""
    password: str = ""
    method: str = "pfx"

@dataclass
class HSMConfig(SignerConfig):
    """HSM signer configuration"""
    dll_path: Optional[str] = None
    pin: Optional[str] = None
    token_label: Optional[str] = None
    method: str = "hsm"

@dataclass
class HSMTokenInfo:
    """HSM Token information"""
    slot: int
    label: str
    manufacturer: str
    model: str
    serial: str
    dll_path: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'slot': self.slot,
            'label': self.label,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial': self.serial,
            'dll_path': self.dll_path
        }